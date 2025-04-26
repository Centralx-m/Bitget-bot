import crypto from 'crypto';

// Environment variable validations
const REQUIRED_ENV_VARS = ['BITGET_API_BASE_URL'];
REQUIRED_ENV_VARS.forEach(varName => {
  if (!process.env[varName]) {
    console.error(`Missing required environment variable: ${varName}`);
    process.exit(1);
  }
});

export default async function handler(req, res) {
  // Validate HTTP method
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ 
      success: false,
      error: 'Method Not Allowed'
    });
  }

  try {
    // Input validation
    const { pair, side, amount, apiKey, apiSecret, passphrase } = req.body;
    
    if (!pair || !side || !amount || !apiKey || !apiSecret || !passphrase) {
      return res.status(400).json({
        success: false,
        error: 'Missing required parameters'
      });
    }

    if (!['buy', 'sell'].includes(side.toLowerCase())) {
      return res.status(400).json({
        success: false,
        error: 'Invalid side. Must be "buy" or "sell"'
      });
    }

    if (isNaN(amount) || parseFloat(amount) <= 0) {
      return res.status(400).json({
        success: false,
        error: 'Amount must be a positive number'
      });
    }

    // API configuration
    const baseUrl = process.env.BITGET_API_BASE_URL || 'https://api.bitget.com';
    const endpoint = '/api/v2/spot/trade/placeOrder';
    const timestamp = Date.now().toString();
    const method = 'POST';

    // Request body
    const requestBody = {
      symbol: pair.toUpperCase(),
      side: side.toLowerCase(),
      orderType: 'market',
      force: 'gtc',
      quantity: amount.toString(),
    };

    const bodyString = JSON.stringify(requestBody);

    // Generate signature
    const preHash = timestamp + method + endpoint + bodyString;
    const signature = crypto
      .createHmac('sha256', apiSecret)
      .update(preHash)
      .digest('base64');

    // Request headers
    const headers = {
      'Content-Type': 'application/json',
      'ACCESS-KEY': apiKey,
      'ACCESS-SIGN': signature,
      'ACCESS-TIMESTAMP': timestamp,
      'ACCESS-PASSPHRASE': passphrase,
    };

    // API request with timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(baseUrl + endpoint, {
      method,
      headers,
      body: bodyString,
      signal: controller.signal
    });

    clearTimeout(timeout);

    // Handle response
    const data = await response.json();

    if (!response.ok) {
      return res.status(400).json({
        success: false,
        error: data.msg || 'API request failed',
        code: data.code,
        data
      });
    }

    if (data.code !== '00000') {
      return res.status(200).json({
        success: false,
        error: data.msg || 'Trading error',
        code: data.code,
        data
      });
    }

    return res.status(200).json({
      success: true,
      orderId: data.data?.orderId,
      price: data.data?.fillPrice || 0,
      executedAmount: data.data?.fillQuantity || 0
    });

  } catch (error) {
    console.error('Bitget API Error:', error);

    if (error.name === 'AbortError') {
      return res.status(504).json({
        success: false,
        error: 'Request timeout'
      });
    }

    return res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
        
