package bitget

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

type Client struct {
	APIKey     string
	APISecret  string
	Passphrase string
	BaseURL    string
	HTTPClient *http.Client
}

func NewClient(apiKey, apiSecret, passphrase string) *Client {
	return &Client{
		APIKey:     apiKey,
		APISecret:  apiSecret,
		Passphrase: passphrase,
		BaseURL:    "https://api.bitget.com",
		HTTPClient: &http.Client{Timeout: 30 * time.Second},
	}
}

func (c *Client) signRequest(method, path, body string) (string, string, string) {
	timestamp := strconv.FormatInt(time.Now().UnixMilli(), 10)
	message := timestamp + method + path + body
	
	h := hmac.New(sha256.New, []byte(c.APISecret))
	h.Write([]byte(message))
	signature := base64.StdEncoding.EncodeToString(h.Sum(nil))
	
	return timestamp, signature, c.Passphrase
}

func (c *Client) doRequest(method, endpoint string, params interface{}, result interface{}) error {
	var bodyBytes []byte
	var err error
	
	if params != nil {
		bodyBytes, err = json.Marshal(params)
		if err != nil {
			return err
		}
	}
	
	path := "/api" + endpoint
	timestamp, signature, passphrase := c.signRequest(method, path, string(bodyBytes))
	
	req, err := http.NewRequest(method, c.BaseURL+path, bytes.NewBuffer(bodyBytes))
	if err != nil {
		return err
	}
	
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("ACCESS-KEY", c.APIKey)
	req.Header.Set("ACCESS-SIGN", signature)
	req.Header.Set("ACCESS-TIMESTAMP", timestamp)
	req.Header.Set("ACCESS-PASSPHRASE", passphrase)
	req.Header.Set("locale", "en-US")
	
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error: %s, %s", resp.Status, string(body))
	}
	
	return json.NewDecoder(resp.Body).Decode(result)
}

// PlaceGridOrder places a grid trading order
func (c *Client) PlaceGridOrder(pair string, lowerPrice, upperPrice float64, gridCount int, amount float64) error {
	endpoint := "/mix/v1/order/placeGridOrder"
	
	params := map[string]interface{}{
		"symbol":       pair,
		"lowerPrice":   strconv.FormatFloat(lowerPrice, 'f', -1, 64),
