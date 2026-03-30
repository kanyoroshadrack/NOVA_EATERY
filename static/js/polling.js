// polling.js - Order status polling for customer and kitchen

// Customer order status polling (every 5s)
function startCustomerPolling(orderId) {
  const statusBadgeEl = document.getElementById('liveStatusBadge');
  const trackerEl = document.getElementById('orderTracker');

  const statusOrder = ['Pending', 'Preparing', 'Ready', 'Served'];
  const statusClasses = {
    'Pending': 'badge-pending',
    'Preparing': 'badge-preparing',
    'Ready': 'badge-ready',
    'Served': 'badge-served',
    'Cancelled': 'badge-cancelled',
  };

  async function poll() {
    try {
      const res = await fetch(`/api/order-status/${orderId}`);
      const data = await res.json();
      if (data.status && statusBadgeEl) {
        statusBadgeEl.className = `badge ${statusClasses[data.status] || ''}`;
        statusBadgeEl.textContent = data.status;
      }
      if (trackerEl) updateTracker(data.status);
      if (data.status === 'Served' || data.status === 'Cancelled') {
        clearInterval(pollInterval);
      }
    } catch (e) {}
  }

  function updateTracker(status) {
    const idx = statusOrder.indexOf(status);
    document.querySelectorAll('.tracker-step').forEach((step, i) => {
      const dot = step.querySelector('.tracker-dot');
      if (!dot) return;
      if (i < idx) { dot.className = 'tracker-dot done'; dot.innerHTML = '✓'; }
      else if (i === idx) { dot.className = 'tracker-dot active'; dot.innerHTML = (i+1); }
      else { dot.className = 'tracker-dot'; dot.innerHTML = (i+1); }
    });
  }

  const pollInterval = setInterval(poll, 5000);
  poll(); // immediate first call
}

// Kitchen polling handled in kitchen.js
