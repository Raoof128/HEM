const latencyCtx = document.getElementById('latency-chart');
const sizeCtx = document.getElementById('size-chart');
const healthStatus = document.getElementById('health-status');
const auditLog = document.getElementById('audit-log');

const latencyChart = new Chart(latencyCtx, {
  type: 'line',
  data: {
    labels: ['add', 'mul', 'dot', 'polynomial', 'mean', 'linear'],
    datasets: [
      {
        label: 'Latency (ms)',
        data: [2, 3, 4, 5, 2.5, 4.1],
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.2)',
        tension: 0.3,
      },
    ],
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  },
});

const sizeChart = new Chart(sizeCtx, {
  type: 'bar',
  data: {
    labels: ['vector', 'dot', 'poly degree 3', 'linear'],
    datasets: [
      {
        label: 'Ciphertext bytes',
        data: [180, 200, 240, 210],
        backgroundColor: '#38bdf8',
      },
    ],
  },
  options: {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  },
});

async function refreshHealth() {
  try {
    const response = await fetch('/health');
    if (!response.ok) throw new Error('Unavailable');
    const body = await response.json();
    healthStatus.textContent = `Status: ${body.status}`;
  } catch (err) {
    healthStatus.textContent = 'Status: unavailable';
  }
}

function seedAuditEvents() {
  const events = [
    'http.access /encrypt',
    'compute.add ciphertexts processed',
    'compute.dot encrypted vectors scored',
    'compute.polynomial degree 3',
  ];
  auditLog.innerHTML = '';
  events.forEach((evt) => {
    const li = document.createElement('li');
    li.textContent = evt;
    auditLog.appendChild(li);
  });
}

refreshHealth();
seedAuditEvents();
