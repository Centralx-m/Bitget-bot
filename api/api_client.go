package main

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"time"
)

type BitgetAPIClient struct {
	apiKey      string
	apiSecret   string
	passphrase  string
	baseURL     string
	httpClient  *http.Client
}

func NewBitgetAPIClient(apiKey, apiSecret, passphrase string) *BitgetAPIClient {
	return &BitgetAPIClient{
		apiKey:     apiKey,
		apiSecret:  apiSecret,
		passphrase: passphrase,
		baseURL:    "https://api.bitget.com",
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *BitgetAPIClient) signRequest(method, path, bodyStr string) (string, string) {
	timestamp := strconv.FormatInt(time.Now().UnixMilli(), 10)
	
	prehash := timestamp + method + path
	if bodyStr != "" {
		prehash += bodyStr
	}

	mac := hmac.New(sha256.New, []byte(c.apiSecret))
	mac.Write([]byte(prehash))
	signature := base64.StdEncoding.EncodeToString(mac.Sum(nil))

	return timestamp, signature
}

func (c *BitgetAPIClient) makeRequest(method, endpoint string, params interface{}, result interface{}) error {
	var body io.Reader
	var bodyStr string

	if params != nil {
		jsonData, err := json.Marshal(params)
		if err != nil {
			return err
		}
		bodyStr = string(jsonData)
		body = bytes.NewBuffer(jsonData)
	}

	req, err := http.NewRequest(method, c.baseURL+endpoint, body)
	if err != nil {
		return err
	}

	timestamp, signature := c.signRequest(method, endpoint, bodyStr)

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("ACCESS-KEY", c.apiKey)
	req.Header.Set("ACCESS-SIGN", signature)
	req.Header.Set("ACCESS-TIMESTAMP", timestamp)
	req.Header.Set("ACCESS-PASSPHRASE", c.passphrase)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	return json.NewDecoder(resp.Body).Decode(result)
}

// Trading API Methods
func (c *BitgetAPIClient) GetTicker(symbol string) (*TickerData, error) {
	var response struct {
		Data TickerData `json:"data"`
	}
	endpoint := fmt.Sprintf("/api/spot/v1/market/ticker?symbol=%s", symbol)
	err := c.makeRequest("GET", endpoint, nil, &response)
	return &response.Data, err
}

func (c *BitgetAPIClient) PlaceOrder(order OrderRequest) (string, error) {
	var response struct {
		OrderID string `json:"orderId"`
	}
	endpoint := "/api/spot/v1/trade/orders"
	err := c.makeRequest("POST", endpoint, order, &response)
	return response.OrderID, err
}

func (c *BitgetAPIClient) GetOpenOrders(symbol string) ([]OrderDetail, error) {
	var response struct {
		Data []OrderDetail `json:"data"`
	}
	endpoint := fmt.Sprintf("/api/spot/v1/trade/open-orders?symbol=%s", symbol)
	err := c.makeRequest("GET", endpoint, nil, &response)
	return response.Data, err
}

func (c *BitgetAPIClient) GetOrderDetail(symbol, orderID string) (*OrderDetail, error) {
	var response struct {
		Data OrderDetail `json:"data"`
	}
	endpoint := fmt.Sprintf("/api/spot/v1/trade/orderInfo?symbol=%s&orderId=%s", symbol, orderID)
	err := c.makeRequest("GET", endpoint, nil, &response)
	return &response.Data, err
}

func (c *BitgetAPIClient) CancelOrder(symbol, orderID string) error {
	params := map[string]string{
		"symbol":  symbol,
		"orderId": orderID,
	}
	var response struct {
		Success bool `json:"success"`
	}
	endpoint := "/api/spot/v1/trade/cancel-order"
	return c.makeRequest("POST", endpoint, params, &response)
}

func (c *BitgetAPIClient) GetSymbolPrecision(symbol string) int {
	// In production, you would call the exchange API to get this info
	// For demo purposes, we'll return typical values
	switch symbol {
	case "BTCUSDT":
		return 6
	case "ETHUSDT":
		return 4
	default:
		return 2
	}
}