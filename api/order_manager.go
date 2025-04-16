package main

import (
	"fmt"
	"strings"
	"time"

	"github.com/bitget-limited/bitget-api-golang-sdk/model"
)

func (e *TradingEngine) checkOrders() {
	e.orderMutex.Lock()
	defer e.orderMutex.Unlock()

	// Get all open orders from exchange
	exchangeOrders, err := e.client.SpotOrderService().Orders(e.config.Symbol, "live", "", "", "", 100)
	if err != nil {
		log.Printf("Error fetching orders: %v", err)
		return
	}

	// Create map of exchange orders for quick lookup
	exchangeOrderMap := make(map[string]model.OrderInfo)
	for _, order := range exchangeOrders {
		exchangeOrderMap[order.OrderId] = order
	}

	// Check our tracked orders
	for orderID, trackedOrder := range e.activeOrders {
		exchangeOrder, exists := exchangeOrderMap[orderID]
		
		if !exists || exchangeOrder.Status == "filled" || exchangeOrder.Status == "canceled" {
			// Order no longer active - process it
			e.processCompletedOrder(orderID, trackedOrder)
			delete(e.activeOrders, orderID)
		}
	}
}

func (e *TradingEngine) processCompletedOrder(orderID string, order model.OrderInfo) {
	// Find which grid this order belongs to
	for i := range e.gridLevels {
		grid := &e.gridLevels[i]
		
		if grid.BuyOrderID == orderID {
			if order.Status == "filled" {
				grid.BuyFilled = true
				filledQty, _ := strconv.ParseFloat(order.FilledSize, 64)
				e.positionSize += filledQty
				log.Printf("Buy order filled at %s: %s @ %s", order.Price, order.FilledSize, order.Price)
			}
			grid.BuyOrderID = ""
			return
		}
		
		if grid.SellOrderID == orderID {
			if order.Status == "filled" {
				grid.SellFilled = true
				filledQty, _ := strconv.ParseFloat(order.FilledSize, 64)
				filledAmount, _ := strconv.ParseFloat(order.FilledAmount, 64)
				
				profit := filledAmount - (grid.Price * filledQty)
				e.profitTracker.AddTrade(profit)
				e.positionSize -= filledQty
				
				log.Printf("Sell order filled at %s: %s @ %s (Profit: %.4f)", 
					order.Price, order.FilledSize, order.Price, profit)
			}
			grid.SellOrderID = ""
			return
		}
	}
	
	log.Printf("Warning: Completed order %s not found in any grid", orderID)
}

func (e *TradingEngine) cancelAllOrders() {
	for orderID := range e.activeOrders {
		_, err := e.client.SpotOrderService().CancelOrder(e.config.Symbol, orderID)
		if err != nil {
			log.Printf("Error canceling order %s: %v", orderID, err)
		} else {
			log.Printf("Canceled order %s", orderID)
		}
	}
	e.activeOrders = make(map[string]model.OrderInfo)
}