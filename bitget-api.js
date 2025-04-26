const CryptoJS = require("crypto-js");
const fetch = require('node-fetch');

class BitgetApiClient {
  constructor() {
    if (!process.env.BITGET_API_KEY || !process.env.BITGET_API_SECRET || !process.env.BITGET_API_PASSPHRASE) {
      throw new Error('Missing required API credentials in environment variables');
    }

    this.config = {
      apiKey: process.env.BITGET_API_KEY,
      apiSecret: process.env.BITGET_API_SECRET,
      apiPassphrase: process.env.BITGET_API_PASSPHRASE,
      baseUrl: process.env.BITGET_API_BASE_URL || 'https://api.bitget.com',
      timeout: process.env.BITGET_API_TIMEOUT || 5000
    };
  }

  async makeRequest(endpoint, method = 'GET', params = {}) {
    const timestamp = Date.now().toString();
    const signature = this.generateSignature(timestamp, method, endpoint, params);
    
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'X-BITGET-APIKEY': this.config.apiKey,
      'X-BITGET-PASSPHRASE': this.config.apiPassphrase,
      'X-BITGET-SIGNATURE': signature,
      'X-BITGET-TIMESTAMP': timestamp,
    };

    const options = {
      method,
      headers,
      timeout: this.config.timeout,
      body: method !== 'GET' ? JSON.stringify(params) : undefined
    };

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`API request failed: ${errorData.msg || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request error: ${error.message}`);
      throw error;
    }
  }

  generateSignature(timestamp, method, endpoint, params = {}) {
    let message = timestamp + method.toUpperCase() + endpoint;
    
    if (Object.keys(params).length > 0) {
      const sortedParams = Object.keys(params).sort().reduce((acc, key) => {
        acc[key] = params[key];
        return acc;
      }, {});
      message += JSON.stringify(sortedParams);
    }

    return CryptoJS.HmacSHA256(message, this.config.apiSecret).toString(CryptoJS.enc.Base64);
  }

  // Account Endpoints
  async getAccountInfo() {
    return this.makeRequest('/api/v1/account/info');
  }

  async getBalances() {
    return this.makeRequest('/api/v1/account/assets');
  }

  // Market Data Endpoints
  async getTicker(symbol) {
    return this.makeRequest(`/api/v1/market/ticker?symbol=${symbol}`);
  }

  async getOrderBook(symbol, limit = 20) {
    return this.makeRequest(`/api/v1/market/orderbook?symbol=${symbol}&limit=${limit}`);
  }

  // Trading Endpoints
  async placeOrder(orderParams) {
    const requiredParams = ['symbol', 'side', 'type', 'size'];
    const missingParams = requiredParams.filter(param => !orderParams[param]);
    
    if (missingParams.length > 0) {
      throw new Error(`Missing required order parameters: ${missingParams.join(', ')}`);
    }

    return this.makeRequest('/api/v1/order', 'POST', orderParams);
  }

  async placeLimitOrder(symbol, side, price, size) {
    return this.placeOrder({
      symbol,
      side,
      price,
      size,
      type: 'limit',
      time_in_force: 'GTC'
    });
  }

  async placeMarketOrder(symbol, side, size) {
    return this.placeOrder({
      symbol,
      side,
      size,
      type: 'market'
    });
  }

  async cancelOrder(symbol, orderId) {
    return this.makeRequest('/api/v1/order/cancel', 'POST', {
      symbol,
      orderId
    });
  }

  async getOrderStatus(symbol, orderId) {
    return this.makeRequest(`/api/v1/order/detail?symbol=${symbol}&orderId=${orderId}`);
  }

  async getOpenOrders(symbol) {
    return this.makeRequest(`/api/v1/order/openOrders?symbol=${symbol}`);
  }

  // Grid Trading Specific Methods
  async placeGridOrders(symbol, lowerLimit, upperLimit, levels, totalInvestment) {
    const gridSpacing = (upperLimit - lowerLimit) / (levels - 1);
    const orderSize = totalInvestment / levels / upperLimit; // Approximate size in base currency
    
    const buyOrders = [];
    const sellOrders = [];
    
    for (let i = 0; i < levels; i++) {
      const price = lowerLimit + (i * gridSpacing);
      
      // Place buy order
      try {
        const buyResult = await this.placeLimitOrder(symbol, 'buy', price.toFixed(2), orderSize.toFixed(4));
        buyOrders.push(buyResult);
      } catch (error) {
        console.error(`Failed to place buy order at ${price}:`, error.message);
      }
      
      // Place sell order (at higher grid levels)
      if (i > 0) {
        const sellPrice = price + gridSpacing;
        try {
          const sellResult = await this.placeLimitOrder(symbol, 'sell', sellPrice.toFixed(2), orderSize.toFixed(4));
          sellOrders.push(sellResult);
        } catch (error) {
          console.error(`Failed to place sell order at ${sellPrice}:`, error.message);
        }
      }
    }
    
    return { buyOrders, sellOrders };
  }
}

module.exports = BitgetApiClient;
