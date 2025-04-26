const { getAccountInfo, placeOrder } = require('./bitget-api');

const startButton = document.getElementById('start-btn');
const stopButton = document.getElementById('stop-btn');
const statusDisplay = document.getElementById('status');
const tradeLogTable = document.getElementById('trade-log').getElementsByTagName('tbody')[0];

let isBotRunning = false;

startButton.addEventListener('click', async () => {
    statusDisplay.textContent = "Status: Running";
    startButton.disabled = true;
    stopButton.disabled = false;
    isBotRunning = true;

    const accountInfo = await getAccountInfo();
    console.log(accountInfo);

    await placeGridOrders();
});

stopButton.addEventListener('click', () => {
    isBotRunning = false;
    statusDisplay.textContent = "Status: Stopped";
    startButton.disabled = false;
    stopButton.disabled = true;
});

async function placeGridOrders() {
    const gridLevels = parseInt(document.getElementById('grid-levels').value);
    const upperPrice = parseFloat(document.getElementById('upper-price').value);
    const lowerPrice = parseFloat(document.getElementById('lower-price').value);
    const investment = parseFloat(document.getElementById('investment').value);

    const step = (upperPrice - lowerPrice) / gridLevels;
    const amountPerGrid = investment / gridLevels;

    for (let i = 0; i < gridLevels; i++) {
        const price = (lowerPrice + i * step).toFixed(2);
        const size = (amountPerGrid / price).toFixed(6);
        const side = i % 2 === 0 ? 'buy' : 'sell';

        const order = await placeOrder('BTCUSDT', price, size, side);
        console.log(order);

        const row = tradeLogTable.insertRow();
        row.insertCell(0).textContent = new Date().toLocaleString();
        row.insertCell(1).textContent = side;
        row.insertCell(2).textContent = price;
        row.insertCell(3).textContent = size;
        row.insertCell(4).textContent = 'Pending'; // or actual profit later
    }
}