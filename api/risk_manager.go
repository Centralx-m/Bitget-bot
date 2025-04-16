package main

import (
	"time"
)

type RiskManager struct {
	maxDailyLoss    float64
	maxPositionSize float64
	dailyProfit     float64
	dailyLoss       float64
	startTime      time.Time
}

func NewRiskManager(maxDailyLossPct, maxPositionSize float64) *RiskManager {
	return &RiskManager{
		maxDailyLoss:    maxDailyLossPct / 100,
		maxPositionSize: maxPositionSize,
		startTime:      time.Now(),
	}
}

func (rm *RiskManager) CheckRisk(engine *TradingEngine) bool {
	// Check daily loss limit
	accountBalance := engine.getAccountBalance()
	currentLoss := rm.dailyLoss / accountBalance
	
	if currentLoss > rm.maxDailyLoss {
		log.Printf("RISK ALERT: Daily loss limit reached (%.2f%%)", currentLoss*100)
		return false
	}
	
	// Check position size
	if engine.positionSize > rm.maxPositionSize {
		log.Printf("RISK ALERT: Position size exceeded (%.4f > %.4f)", 
			engine.positionSize, rm.maxPositionSize)
		return false
	}
	
	// Check for market gaps
	if engine.checkPriceGaps() {
		log.Println("RISK ALERT: Significant price gap detected")
		return false
	}
	
	return true
}

func (e *TradingEngine) riskCheck() {
	if !e.config.RiskManagement.Enabled {
		return
	}
	
	if !e.riskManager.CheckRisk(e) {
		log.Println("Risk limits exceeded - shutting down")
		e.Shutdown()
	}
}

func (e *TradingEngine) getAccountBalance() float64 {
	account, err := e.client.AccountService().AccountAssets(e.config.Symbol)
	if err != nil {
		log.Printf("Error getting account balance: %v", err)
		return 0
	}
	
	for _, asset := range account {
		if asset.Coin == strings.Split(e.config.Symbol, "_")[0] {
			balance, _ := strconv.ParseFloat(asset.Available, 64)
			return balance
		}
	}
	
	return 0
}