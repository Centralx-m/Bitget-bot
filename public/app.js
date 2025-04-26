let botRunning = false;
let totalPnL = 0; // total profit and loss

document.getElementById('start-btn').addEventListener('click', startBot);
document.getElementById('stop-btn').addEventListener('click', stopBot);

function startBot() {
  botRunning = true;
  updateStatus();
  showNotification('Bot Started!');
}

function stopBot() {
  botRunning = false;
  updateStatus();
  showNotification('Bot Stopped!');
}

function updateStatus() {
  const statusElement = document.getElementById('bot-status');
  const startBtn = document.getElementById('start-btn');
  const stopBtn = document.getElementById('stop-btn');

  if (botRunning) {
    statusElement.textContent = 'Running';
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } else {
    statusElement.textContent = 'Stopped';
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

function showNotification(message) {
  const notif = document.createElement('div');
  notif.className = 'notification';
  notif.innerText = message;
  document.body.appendChild(notif);

  setTimeout(() => {
    notif.remove();
  }, 3000);
}

// Function to simulate a new trade (you replace this with real trading logic)
function simulateTrade(side, price, amount) {
  const profit = Math.random() * 10 - 5; // random profit/loss between -5 and +5
  totalPnL += profit;

  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${new Date().toLocaleTimeString()}</td>
    <td>${side}</td>
    <td>${price.toFixed(2)}</td>
    <td>${amount.toFixed(4)}</td>
    <td>${profit.toFixed(2)}</td>
  `;
  document.getElementById('trade-table-body').appendChild(row);

  document.getElementById('live-pnl').innerText = `${totalPnL.toFixed(2)} USDT`;
}

// You can call simulateTrade('Buy', 42000, 0.01) for testing live!