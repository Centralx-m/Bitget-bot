// /api/bitget.js

import crypto from 'crypto';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        res.status(405).send('Method Not Allowed');
        return;
    }

    try {
        const { pair, side, amount, apiKey, apiSecret, passphrase } = req.body;

        const baseUrl = 'https://api.bitget.com';
        const timestamp = Date.now().toString();
        const method = 'POST';
        const requestPath = '/api/v2/spot/trade/placeOrder';

        const body = JSON.stringify({
            symbol: pair,
            side: side.toUpperCase() === 'BUY' ? 'buy' : 'sell',
            orderType: 'market',
            force: 'gtc',
            quantity: amount,
        });

        const preHash = timestamp + method + requestPath + body;
        const signature = crypto
            .createHmac('sha256', apiSecret)
            .update(preHash)
            .digest('base64');

        const headers = {
            'Content-Type': 'application/json',
            'ACCESS-KEY': apiKey,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': passphrase,
        };

        const response = await fetch(baseUrl + requestPath, {
            method,
            headers,
            body,
        });

        const data = await response.json();

        if (data.code === '00000') {
            res.status(200).json({ success: true, price: data.data.price || 0 });
        } else {
            res.status(400).json({ success: false, error: data });
        }

    } catch (error) {
        console.error('Serverless Error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
}