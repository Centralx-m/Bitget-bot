// Global Variables
let isBotRunning = false;
let simulationMode = true;
let intervalId;
let grids = [];
let investmentPerGrid = 0;

// Start Bot
document.getElementById('start-btn').addEventListener('click', () => {
    const apiKey = document.getElementById('api-key').value.trim();
    const apiSecret = document.getElementById('api-secret').value.trim();
    const passphrase = document.getElementById('api-passphrase').value.trim();
    const tradingPair = document.getElementById('trading-pair').value;
    const upperPrice = parseFloat(document.getElementById('upper-price').value);
    const lowerPrice = parseFloat(document.getElementById('lower-price').value);
    const gridLevels = parseInt(document.getElementById('grid-levels').value);
    const investment = parseFloat(document.getElementById('investment').value);

    if (isNaN(upperPrice) || isNaN(lowerPrice) || upperPrice <= lowerPrice || gridLevels < 2) {
        alert('Please check your grid settings.');
        return;
    }

    simulationMode = (apiKey === '' || apiSecret === '' || passphrase === '');

    grids = [];
    const priceStep = (upperPrice - lowerPrice) / gridLevels;
    for (let i = 0; i <= gridLevels; i++) {
        grids.push(lowerPrice + i * priceStep);
    }

    investmentPerGrid = investment / gridLevels;

    drawGrids();
    updateStatus('Running (' + (simulationMode ? 'Simulation' : 'Live') + ')');
    isBotRunning = true;

    document.getElementById('start-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;

    intervalId = setInterval(() => fetchPriceAndTrade(tradingPair, apiKey, apiSecret, passphrase), 3000);
});

// Stop Bot
document.getElementById('stop-btn').addEventListener('click', () => {
    clearInterval(intervalId);
    updateStatus('Stopped');
    isBotRunning = false;
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
});

// Fetch price and simulate or live trade
async function fetchPriceAndTrade(pair, apiKey, apiSecret, passphrase) {
    try {
        const res = await fetch(`https://api.bitget.com/api/v2/spot/market/ticker?symbol=${pair}`);
        const data = await res.json();
        const currentPrice = parseFloat(data.data.close);

        document.getElementById('current-price').innerText = `Current Price: ${currentPrice}`;

        if (!isBotRunning) return;

        // Check grid levels
        for (let i = 0; i < grids.length; i++) {
            const gridPrice = grids[i];

            if (Math.abs(currentPrice - gridPrice) < 0.5) { // Small threshold
                const tradeType = (Math.random() > 0.5) ? 'BUY' : 'SELL'; // Random for demo
                const amount = (investmentPerGrid / currentPrice).toFixed(6);

                if (simulationMode) {
                    addTradeLog('Sim', tradeType, gridPrice, amount, (Math.random() * 5).toFixed(2));
                } else {
                    await placeOrder(pair, tradeType, amount, apiKey, apiSecret, passphrase);
                }
            }
        }

    } catch (error) {
        console.error(error);
        updateStatus('Error fetching price.');
    }
}

// Place real order (via Vercel API function)
async function placeOrder(pair, side, amount, apiKey, apiSecret, passphrase) {
    try {
        const res = await fetch('/api/bitget', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pair, side, amount, apiKey, apiSecret, passphrase })
        });

        const data = await res.json();
        if (data.success) {
            addTradeLog('Live', side, data.price, amount, data.profit || 0);
        } else {
            console.error('Order failed:', data);
        }
    } catch (error) {
        console.error('Error placing order:', error);
    }
}

// Draw Grid Lines
function drawGrids() {
    const gridLinesContainer = document.getElementById('grid-lines');
    gridLinesContainer.innerHTML = '';

    for (let i = 0; i < grids.length; i++) {
        const line = document.createElement('div');
        line.style.position = 'absolute';
        line.style.top = `${100 - (i / (grids.length - 1)) * 100}%`;
        line.style.left = 0;
        line.style.width = '100%';
        line.style.height = '1px';
        line.style.backgroundColor = '#58a6ff';
        gridLinesContainer.appendChild(line);
    }
}

// Update Status
function updateStatus(text) {
    document.getElementById('status').innerText = 'Status: ' + text;
}

// Add to Trade History
function addTradeLog(mode, type, price, amount, profit) {
    const table = document.getElementById('trade-log').querySelector('tbody');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${new Date().toLocaleTimeString()}</td>
        <td>${mode} ${type}</td>
        <td>${parseFloat(price).toFixed(2)}</td>
        <td>${parseFloat(amount).toFixed(4)}</td>
        <td>${parseFloat(profit).toFixed(2)}</td>
    `;
    table.prepend(row);
}