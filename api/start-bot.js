// /api/start-bot.js
import crypto from 'crypto';
import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end('Method Not Allowed');

  const { tradingPair, upperPrice, lowerPrice, gridLevels, investment } = req.body;

  const API_KEY = process.env.BITGET_API_KEY;
  const API_SECRET = process.env.BITGET_API_SECRET;
  const API_PASSPHRASE = process.env.BITGET_API_PASSPHRASE;

  try {
    const baseUrl = 'https://api.bitget.com';
    const urlPath = '/api/spot/v1/order';
    const method = 'POST';

    // Grid generation
    const gridSpacing = (upperPrice - lowerPrice) / (gridLevels - 1);
    const orders = [];
    
    for (let i = 0; i < gridLevels; i++) {
      const price = (lowerPrice + gridSpacing * i).toFixed(2);
      const size = (investment / gridLevels / price).toFixed(6); // Investment equally divided

      orders.push({
        symbol: tradingPair,
        price,
        size,
        side: i % 2 === 0 ? 'buy' : 'sell', // alternate buy/sell
        orderType: 'limit',
        force: 'normal'
      });
    }

    // Place all orders one by one
    const responses = [];
    for (const order of orders) {
      const bodyString = JSON.stringify(order);
      const timestamp = Date.now().toString();
      const preSign = timestamp + method + urlPath + bodyString;
      const signature = crypto.createHmac('sha256', API_SECRET)
        .update(preSign)
        .digest('base64');

      const response = await axios({
        method,
        url: baseUrl + urlPath,
        headers: {
          'Content-Type': 'application/json',
          'ACCESS-KEY': API_KEY,
          'ACCESS-SIGN': signature,
          'ACCESS-TIMESTAMP': timestamp,
          'ACCESS-PASSPHRASE': API_PASSPHRASE
        },
        data: order
      });

      responses.push(response.data);
    }

    return res.status(200).json({ success: true, orders: responses });
  } catch (error) {
    console.error('Grid bot error:', error.response?.data || error.message);
    return res.status(500).json({ success: false, error: error.response?.data || error.message });
  }
}