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
    // Example Bitget endpoint
    const urlPath = '/api/spot/v1/order'; // <- Example, you will adjust
    const method = 'POST';
    const baseUrl = 'https://api.bitget.com';

    // Build body
    const body = {
      symbol: tradingPair,
      price: upperPrice,
      size: 1,
      side: 'buy',
      orderType: 'limit',
      force: 'normal'
    };
    const bodyString = JSON.stringify(body);

    // Generate timestamp
    const timestamp = Date.now().toString();

    // Create pre-sign string
    const preSign = timestamp + method + urlPath + bodyString;

    // Sign the preSign string
    const signature = crypto.createHmac('sha256', API_SECRET)
      .update(preSign)
      .digest('base64');

    // Now make request
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
      data: body
    });

    return res.status(200).json({ success: true, data: response.data });
  } catch (error) {
    console.error('Bot start error:', error.response?.data || error.message);
    return res.status(500).json({ success: false, error: error.response?.data || error.message });
  }
}