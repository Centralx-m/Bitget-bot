package main

import (
	"context"
	"log"
	"math"
	"sync"
	"time"

	"github.com/bitget-limited/bitget-api-golang-sdk/model"
	"github.com/bitget-limited/bitget-api-golang-sdk/rest"
)

type GridLevel struct {
	Price       float64
	BuyOrderID  string
	SellOrderID string
	Filled      bool
}

type TradingSession struct {
	Client       *rest.BitgetApiClient
	Config       BotConfig
	GridLevels   []GridLevel
	ActiveOrders map[string]bool
	Mutex        sync.Mutex
	TotalProfit  float64
	StartTime    time.Time
}

func NewTradingSession(config BotConfig) *TradingSession {
	client := rest.NewBitgetApiClient(config.APIKey, config.APISecret, config.APIPassphrase)
	
	// Calculate grid levels
	priceIncrement := (config.UpperPrice - config.LowerPrice) / float64(config.Grids)
	gridLevels := make([]GridLevel, config.Grids+1)
	for i := 0; i <= config.Grids; i++ {
		gridLevels[i] = GridLevel{
			Price: config.LowerPrice + (float64(i) * priceIncrement),
		}
	}

	return &TradingSession{
		Client:       client,
		Config:       config,
		GridLevels:   gridLevels,
		ActiveOrders: make(map[string]bool),
		StartTime:    time.Now(),
	}
}

func (ts *TradingSession) Run(ctx context.Context) {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Printf("Stopping trading session for %s", ts.Config.Symbol)
			ts.CancelAllOrders()
			return
		case <-ticker.C:
			ts.CheckMarket()
		}
	}
}

func (ts *TradingSession) CheckMarket() {
	ts.Mutex.Lock()
	defer ts.Mutex.Unlock()

	// Get current market price
	ticker, err := ts.Client.SpotPublicService().Ticker(ts.Config.Symbol)
	if err != nil {
		log.Printf("Error getting ticker: %v", err)
		return
	}

	currentPrice, err := strconv.ParseFloat(ticker.Data[0].LastPr, 64)
	if err != nil {
		log.Printf("Error parsing price: %v", err)
		return
	}

	// Check for filled orders
	ts.CheckOrderStatus()

	// Place new orders based on grid levels
	for i, level := range ts.GridLevels {
		if level.Filled {
			continue
		}

		// Place buy order if price is below this level and we don't have an active order
		if currentPrice < level.Price && level.BuyOrderID == "" {
			orderID, err := ts.PlaceBuyOrder(level.Price)
			if err != nil {
				log.Printf("Error placing buy order: %v", err)
				continue
			}
			ts.GridLevels[i].BuyOrderID = orderID
			ts.ActiveOrders[orderID] = true
		}

		// Place sell order if price is above this level and we don't have an active order
		if currentPrice > level.Price && level.SellOrderID == "" {
			orderID, err := ts.PlaceSellOrder(level.Price)
			if err != nil {
				log.Printf("Error placing sell order: %v", err)
				continue
			}
			ts.GridLevels[i].SellOrderID = orderID
			ts.ActiveOrders[orderID] = true
		}
	}
}

func (ts *TradingSession) PlaceBuyOrder(price float64) (string, error) {
	// Calculate quantity based on investment and grid count
	quantity := (ts.Config.Investment / float64(ts.Config.Grids)) / price
	
	// Round to appropriate decimal places based on symbol
	quantity = math.Floor(quantity*100000) / 100000 // Example for BTC
	
	req := model.PlaceOrderReq{
		Symbol:   ts.Config.Symbol,
		Side:     "buy",
		OrderType: "limit",
		Price:    strconv.FormatFloat(price, 'f', -1, 64),
		Size:     strconv.FormatFloat(quantity, 'f', -1, 64),
	}
	
	resp, err := ts.Client.SpotOrderService().PlaceOrder(req)
	if err != nil {
		return "", err
	}
	
	return resp.OrderId, nil
}

func (ts *TradingSession) PlaceSellOrder(price float64) (string, error) {
	// Similar to PlaceBuyOrder but with side="sell"
	// Implementation omitted for brevity
}

func (ts *TradingSession) CheckOrderStatus() {
	// Get all open orders
	orders, err := ts.Client.SpotOrderService().Orders(ts.Config.Symbol, "open", "", "", "", 100)
	if err != nil {
		log.Printf("Error getting orders: %v", err)
		return
	}

	// Check which of our active orders are still open
	for orderID := range ts.ActiveOrders {
		found := false
		for _, order := range orders {
			if order.OrderId == orderID {
				found = true
				break
			}
		}
		
		if !found {
			// Order is no longer open - check if filled
			orderDetail, err := ts.Client.SpotOrderService().OrderDetail(ts.Config.Symbol, orderID)
			if err != nil {
				log.Printf("Error getting order detail: %v", err)
				continue
			}
			
			if orderDetail.Status == "filled" {
				ts.ProcessFilledOrder(orderID)
			}
			delete(ts.ActiveOrders, orderID)
		}
	}
}

func (ts *TradingSession) ProcessFilledOrder(orderID string) {
	// Find which grid level this order belongs to
	for i, level := range ts.GridLevels {
		if level.BuyOrderID == orderID {
			// Buy order was filled - mark level as filled
			ts.GridLevels[i].Filled = true
			// Place corresponding sell order
			// Implementation omitted
			break
		} else if level.SellOrderID == orderID {
			// Sell order was filled - calculate profit
			// Reset level for next cycle
			ts.GridLevels[i].Filled = false
			ts.GridLevels[i].BuyOrderID = ""
			ts.GridLevels[i].SellOrderID = ""
			// Update profit tracking
			// Implementation omitted
			break
		}
	}
}

func (ts *TradingSession) CancelAllOrders() {
	// Implementation to cancel all active orders
}
