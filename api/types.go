package main

import "time"

type BotConfig struct {
	APIKey        string  `json:"api_key" yaml:"api_key"`
	APISecret     string  `json:"api_secret" yaml:"api_secret"`
	APIPassphrase string  `json:"api_passphrase" yaml:"api_passphrase"`
	Symbol        string  `json:"symbol" yaml:"symbol"`
	UpperPrice    float64 `json:"upper_price" yaml:"upper_price"`
	LowerPrice    float64 `json:"lower_price" yaml:"lower_price"`
	Grids         int     `json:"grids" yaml:"grids"`
	Investment    float64 `json:"investment" yaml:"investment"`
	MaxDrawdown   float64 `json:"max_drawdown" yaml:"max_drawdown"`
}

type GridLevel struct {
	Price       float64 `json:"price"`
	BuyOrderID  string  `json:"buy_order_id,omitempty"`
	SellOrderID string  `json:"sell_order_id,omitempty"`
	Filled      bool    `json:"filled"`
}

type OrderRequest struct {
	Symbol    string  `json:"symbol"`
	Side      string  `json:"side"`
	OrderType string  `json:"orderType"`
	Price     float64 `json:"price"`
	Quantity  float64 `json:"size"`
}

type OrderInfo struct {
	OrderID   string  `json:"order_id"`
	GridIndex int     `json:"grid_index"`
	Side      string  `json:"side"`
	Price     float64 `json:"price"`
}

type OrderDetail struct {
	OrderID   string `json:"orderId"`
	Symbol    string `json:"symbol"`
	Price     string `json:"price"`
	Quantity  string `json:"size"`
	Side      string `json:"side"`
	Status    string `json:"status"`
	CreatedAt string `json:"createTime"`
}

type TickerData struct {
	Symbol    string `json:"symbol"`
	LastPrice string `json:"lastPr"`
	BidPrice  string `json:"bidPr"`
	AskPrice  string `json:"askPr"`
	Volume    string `json:"vol"`
}

type TradingStats struct {
	StartTime    time.Time        `json:"start_time"`
	RunningTime  string           `json:"running_time,omitempty"`
	TotalBuys    int              `json:"total_buys"`
	TotalSells   int              `json:"total_sells"`
	TotalProfit  float64          `json:"total_profit"`
	ProfitPerGrid map[int]float64 `json:"profit_per_grid"`
	ROI         float64          `json:"roi"`
}

type APIResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}