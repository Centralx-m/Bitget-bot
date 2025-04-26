let botRunning = false;
let totalPnL = 0;
let tradeInterval;
let gridLevels = 0;
let upperLimit = 0;
let lowerLimit = 0;
let investmentAmount = 0;

// DOM Elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusElement = document.getElementById('bot-status');
const pnlElement = document.getElementById('live-pnl');
const tradeTableBody = document.getElementById('trade-table-body');

// Event Listeners
startBtn.addEventListener('click', startBot);
stopBtn.addEventListener('click', stopBot);

// Main Bot Functions
function startBot() {
  if (!validateInputs()) return;
  
  botRunning = true;
  updateStatus();
  showNotification('Bot Started Successfully!', 'success');
  
  // Initialize grid parameters
  gridLevels = parseInt(document.getElementById('grid-levels').value);
  upperLimit = parseFloat(document.getElementById('upper-limit').value);
  lowerLimit = parseFloat(document.getElementById('lower-limit').value);
  investmentAmount = parseFloat(document.getElementById('investment-amount').value);
  
  // Calculate grid spacing and order amounts
  const gridSpacing = (upperLimit - lowerLimit) / (gridLevels - 1);
  const orderAmount = investmentAmount / gridLevels;
  
  // Start simulated trading (replace with real API calls)
  tradeInterval = setInterval(() => {
    const randomLevel = Math.floor(Math.random() * gridLevels);
    const price = lowerLimit + (randomLevel * gridSpacing);
    const side = Math.random() > 0.5 ? 'Buy' : 'Sell';
    simulateTrade(side, price, orderAmount);
  }, 3000); // Simulate a trade every 3 seconds
}

function stopBot() {
  botRunning = false;
  clearInterval(tradeInterval);
  updateStatus();
  showNotification('Bot Stopped Successfully!', 'info');
}

function updateStatus() {
  if (botRunning) {
    statusElement.textContent = 'Running';
    statusElement.className = 'status-active';
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else {
    statusElement.textContent = 'Stopped';
    statusElement.className = 'status-inactive';
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
  updatePnLColor();
}

// Helper Functions
function validateInputs() {
  const levels = document.getElementById('grid-levels').value;
  const upper = document.getElementById('upper-limit').value;
  const lower = document.getElementById('lower-limit').value;
  const amount = document.getElementById('investment-amount').value;
  
  if (!levels || !upper || !lower || !amount) {
    showNotification('Please fill all settings fields!', 'error');
    return false;
  }
  
  if (parseFloat(upper) <= parseFloat(lower)) {
    showNotification('Upper limit must be greater than lower limit!', 'error');
    return false;
  }
  
  if (parseInt(levels) < 2) {
    showNotification('Grid levels must be at least 2!', 'error');
    return false;
  }
  
  if (parseFloat(amount) <= 0) {
    showNotification('Investment amount must be positive!', 'error');
    return false;
  }
  
  return true;
}

function showNotification(message, type = 'info') {
  const notif = document.createElement('div');
  notif.className = `notification notification-${type}`;
  notif.innerText = message;
  document.body.appendChild(notif);

  setTimeout(() => {
    notif.style.opacity = '0';
    setTimeout(() => notif.remove(), 300);
  }, 3000);
}

function simulateTrade(side, price, amount) {
  const profit = (Math.random() * 10 - 5) * (side === 'Buy' ? 1 : -1);
  totalPnL += profit;

  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${new Date().toLocaleTimeString()}</td>
    <td class="trade-side-${side.toLowerCase()}">${side}</td>
    <td>${price.toFixed(2)}</td>
    <td>${amount.toFixed(4)}</td>
    <td class="${profit >= 0 ? 'profit-positive' : 'profit-negative'}">
      ${profit.toFixed(2)}
    </td>
  `;
  
  // Add to top of table
  tradeTableBody.insertBefore(row, tradeTableBody.firstChild);
  
  // Keep only the last 50 trades
  if (tradeTableBody.children.length > 50) {
    tradeTableBody.removeChild(tradeTableBody.lastChild);
  }
  
  updatePnLDisplay();
}

function updatePnLDisplay() {
  pnlElement.textContent = `${totalPnL.toFixed(2)} USDT`;
  updatePnLColor();
}

function updatePnLColor() {
  pnlElement.className = totalPnL > 0 ? 'pnl-positive' : 
                        totalPnL < 0 ? 'pnl-negative' : 'pnl-neutral';
}

// Initialize
updateStatus();
