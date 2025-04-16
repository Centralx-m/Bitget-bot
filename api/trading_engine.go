package main

import (
	"context"
	"log"
	"math"
	"strconv"
	"sync"
	"time"
)

type TradingEngine struct {
	client      *BitgetAPIClient
	config      BotConfig
	gridLevels  []GridLevel
	activeOrders map[string]OrderInfo
	mutex       sync.Mutex
	stats       TradingStats
	stopChan    chan struct{}
}

func NewTradingEngine(cfg BotConfig) *TradingEngine {
	return &TradingEngine{
		client:      NewBitgetAPIClient(cfg.APIKey, cfg.APISecret, cfg.APIPassphrase),
		config:      cfg,
		gridLevels:  createGridLevels(cfg),
		activeOrders: make(map[string]OrderInfo),
		stopChan:    make(chan struct{}),
		stats: TradingStats{
			StartTime: time.Now(),
		},
	}
}

func (e *TradingEngine) Start() {
	log.Printf("Starting trading engine for %s", e.config.Symbol)
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-e.stopChan:
			log.Println("Received stop signal")
			e.CancelAllOrders()
			return
		case <-ticker.C:
			if err := e.RunCycle(); err != nil {
				log.Printf("Trading cycle error: %v", err)
			}
		}
	}
}

func (e *TradingEngine) RunCycle() error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	// 1. Get current market data
	ticker, err := e.client.GetTicker(e.config.Symbol)
	if err != nil {
		return err
	}

	currentPrice, err := strconv.ParseFloat(ticker.LastPrice, 64)
	if err != nil {
		return err
	}

	// 2. Check and update existing orders
	if err := e.checkOrderStatuses(); err != nil {
		return err
	}

	// 3. Place new grid orders
	return e.placeGridOrders(currentPrice)
}

func (e *TradingEngine) placeGridOrders(currentPrice float64) error {
	for i, level := range e.gridLevels {
		if level.Filled {
			continue
		}

		// Place buy order if price is below this level
		if currentPrice < level.Price && level.BuyOrderID == "" {
			quantity := e.calculateOrderQuantity(level.Price)
			orderID, err := e.client.PlaceOrder(OrderRequest{
				Symbol:   e.config.Symbol,
				Side:     "buy",
				OrderType: "limit",
				Price:    level.Price,
				Quantity: quantity,
			})
			if err != nil {
				return err
			}
			e.gridLevels[i].BuyOrderID = orderID
			e.activeOrders[orderID] = OrderInfo{
				OrderID:  orderID,
				GridIndex: i,
				Side:     "buy",
				Price:    level.Price,
			}
		}

		// Place sell order if price is above this level
		if currentPrice > level.Price && level.SellOrderID == "" {
			quantity := e.calculateOrderQuantity(level.Price)
			orderID, err := e.client.PlaceOrder(OrderRequest{
				Symbol:   e.config.Symbol,
				Side:     "sell",
				OrderType: "limit",
				Price:    level.Price,
				Quantity: quantity,
			})
			if err != nil {
				return err
			}
			e.gridLevels[i].SellOrderID = orderID
			e.activeOrders[orderID] = OrderInfo{
				OrderID:  orderID,
				GridIndex: i,
				Side:     "sell",
				Price:    level.Price,
			}
		}
	}
	return nil
}

func (e *TradingEngine) calculateOrderQuantity(price float64) float64 {
	// Calculate quantity based on investment divided by number of grids
	baseQty := (e.config.Investment / float64(e.config.Grids)) / price
	
	// Get symbol precision
	precision := e.client.GetSymbolPrecision(e.config.Symbol)
	
	// Round to correct precision
	return math.Floor(baseQty*math.Pow(10, float64(precision))) / math.Pow(10, float64(precision))
}

func (e *TradingEngine) checkOrderStatuses() error {
	orders, err := e.client.GetOpenOrders(e.config.Symbol)
	if err != nil {
		return err
	}

	// Check for filled orders
	for orderID, info := range e.activeOrders {
		found := false
		for _, order := range orders {
			if order.OrderID == orderID {
				found = true
				break
			}
		}

		if !found {
			// Order is no longer open - check if filled
			orderDetail, err := e.client.GetOrderDetail(e.config.Symbol, orderID)
			if err != nil {
				return err
			}

			if orderDetail.Status == "filled" {
				e.processFilledOrder(info, orderDetail)
			}
			delete(e.activeOrders, orderID)
		}
	}
	return nil
}

func (e *TradingEngine) processFilledOrder(info OrderInfo, detail OrderDetail) {
	gridIndex := info.GridIndex
	level := &e.gridLevels[gridIndex]

	if info.Side == "buy" {
		// Buy order filled - mark level as filled
		level.Filled = true
		level.BuyOrderID = ""
		e.stats.TotalBuys++
	} else {
		// Sell order filled - calculate profit
		level.Filled = false
		level.SellOrderID = ""
		e.stats.TotalSells++
		
		// Calculate profit from this grid
		buyPrice := level.Price
		sellPrice, _ := strconv.ParseFloat(detail.Price, 64)
		quantity, _ := strconv.ParseFloat(detail.Quantity, 64)
		profit := (sellPrice - buyPrice) * quantity
		
		e.stats.TotalProfit += profit
		e.stats.ProfitPerGrid[gridIndex] += profit
	}
}

func (e *TradingEngine) Stop() {
	close(e.stopChan)
}

func (e *TradingEngine) CancelAllOrders() {
	for orderID := range e.activeOrders {
		if err := e.client.CancelOrder(e.config.Symbol, orderID); err != nil {
			log.Printf("Error canceling order %s: %v", orderID, err)
		}
	}
	e.activeOrders = make(map[string]OrderInfo)
}

func (e *TradingEngine) GetStats() TradingStats {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	stats := e.stats
	stats.RunningTime = time.Since(e.stats.StartTime).String()
	stats.ROI = (stats.TotalProfit / e.config.Investment) * 100
	return stats
}