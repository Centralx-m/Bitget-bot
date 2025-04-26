const CryptoJS = require("crypto-js");

const BITGET_API_KEY = process.env.BITGET_API_KEY;
const BITGET_API_SECRET = process.env.BITGET_API_SECRET;
const BITGET_API_PASSPHRASE = process.env.BITGET_API_PASSPHRASE;
const BITGET_API_BASE_URL = process.env.BITGET_API_BASE_URL || 'https://api.bitget.com';

function generateSignature(apiPath, params) {
    let queryString = '';
    Object.keys(params).sort().forEach((key) => {
        queryString += `${key}=${params[key]}&`;
    });
    queryString = queryString.slice(0, -1);

    const message = `${apiPath}${queryString}`;
    const signature = CryptoJS.HmacSHA256(message, BITGET_API_SECRET).toString(CryptoJS.enc.Base64);
    return signature;
}

async function makeApiRequest(endpoint, method, params = {}) {
    const timestamp = Date.now();
    const signature = generateSignature(endpoint, params);
    const url = `${BITGET_API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        'X-BITGET-APIKEY': BITGET_API_KEY,
        'X-BITGET-PASSPHRASE': BITGET_API_PASSPHRASE,
        'X-BITGET-SIGNATURE': signature,
        'X-BITGET-TIMESTAMP': timestamp,
    };

    const response = await fetch(url, {
        method,
        headers,
        body: method === 'POST' ? JSON.stringify(params) : undefined,
    });

    return await response.json();
}

async function getAccountInfo() {
    const endpoint = '/api/v1/account/info';
    return await makeApiRequest(endpoint, 'GET');
}

async function placeOrder(symbol, price, size, side) {
    const endpoint = '/api/v1/order';
    const params = {
        symbol,
        price,
        size,
        side,
        type: 'limit',
        time_in_force: 'GTC',
    };
    return await makeApiRequest(endpoint, 'POST', params);
}

module.exports = {
    getAccountInfo,
    placeOrder,
};
