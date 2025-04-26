// app.js

let botRunning = false;
let trades = [];
let basePrice = null;
let simulationMode = true;
let apiKey = '';
let apiSecret = '';
let passphrase = '';
let pair = '';
let investment = 0;
let totalProfit = 0;

const statusEl = document.getElementById('status');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const priceDisplay = document.getElementById('current-price');
const tradeLog = document.getElementById('trade-log').querySelector('tbody');
const pnlDisplay = document.createElement('div');

pnlDisplay.className = 'pnl-tracker';
document.body.appendChild(pnlDisplay);

startBtn.addEventListener('click', startBot);
stopBtn.addEventListener('click', stopBot);

async function startBot() {
    apiKey = document.getElementById('api-key').value.trim();
    apiSecret = document.getElementById('api-secret').value.trim();
    passphrase = document.getElementById('api-passphrase').value.trim();
    simulationMode = !apiKey || !apiSecret || !passphrase;

    pair = document.getElementById('trading-pair').value;
    investment = parseFloat(document.getElementById('investment').value);
    basePrice = await fetchCurrentPrice();

    statusEl.textContent = `Status: Bot Running (${simulationMode ? 'Simulation' : 'Live'})`;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    botRunning = true;

    botLoop();
    livePnlLoop();
}

function stopBot() {
    statusEl.textContent = 'Status: Bot Stopped';
    startBtn.disabled = false;
    stopBtn.disabled = true;
    botRunning = false;
}

async function botLoop() {
    while (botRunning) {
        const price = await fetchCurrentPrice();
        priceDisplay.textContent = `Current Price: ${price}`;

        const action = Math.random() < 0.5 ? 'buy' : 'sell'; // Random action for now

        const amount = (investment / 10 / price).toFixed(6); // Example: 1/10 of investment

        if (simulationMode) {
            simulateTrade(action, price, amount);
        } else {
            await liveTrade(action, price, amount);
        }

        await delay(8000); // Wait 8 seconds between trades
    }
}

async function liveTrade(side, price, amount) {
    try {
        const response = await fetch('/api/bitget', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pair,
                side,
                amount,
                apiKey,
                apiSecret,
                passphrase
            })
        });

        const data = await response.json();
        if (data.success) {
            logTrade(side, price, amount, 0);
        } else {
            console.error('Trade Error:', data.error);
        }
    } catch (err) {
        console.error('Fetch Error:', err);
    }
}

function simulateTrade(side, price, amount) {
    logTrade(side, price, amount, 0);
}

function logTrade(type, price, amount, profit) {
    const now = new Date().toLocaleTimeString();
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${now}</td>
        <td>${type}</td>
        <td>${price}</td>
        <td>${amount}</td>
        <td>${profit.toFixed(4)}</td>
    `;
    tradeLog.appendChild(row);

    trades.push({ type, price: parseFloat(price), amount: parseFloat(amount) });

    // Update total profit for now (static) - real profit will be calculated below
}

async function fetchCurrentPrice() {
    const symbol = pair.toLowerCase();
    try {
        const res = await fetch(`https://api.bitget.com/api/v2/spot/market/ticker?symbol=${symbol}`);
        const data = await res.json();
        return parseFloat(data.data.close);
    } catch (err) {
        console.error('Price fetch error', err);
        return basePrice || 0;
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function livePnlLoop() {
    while (botRunning) {
        if (trades.length > 0) {
            const latestPrice = await fetchCurrentPrice();
            const pnl = calculatePnL(latestPrice);

            pnlDisplay.textContent = `Live PnL: ${pnl.toFixed(2)}%`;
        }
        await delay(5000); // Update PnL every 5 seconds
    }
}

function calculatePnL(currentPrice) {
    let initialInvestment = 0;
    let currentValue = 0;

    trades.forEach(trade => {
        if (trade.type === 'buy') {
            initialInvestment += trade.amount * trade.price;
            currentValue += trade.amount * currentPrice;
        } else if (trade.type === 'sell') {
            initialInvestment -= trade.amount * trade.price;
            currentValue -= trade.amount * currentPrice;
        }
    });

    if (initialInvestment === 0) return 0;
    return ((currentValue - initialInvestment) / Math.abs(initialInvestment)) * 100;
}