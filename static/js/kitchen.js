// kitchen.js - Kitchen dashboard with polling

document.addEventListener('DOMContentLoaded', () => {
  let currentFilter = 'All';

  // ── FILTER TABS ──
  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      currentFilter = btn.dataset.filter;
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderOrders(lastOrders);
    });
  });

  // ── STATUS BUTTONS ──
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.status-btn');
    if (!btn) return;
    const orderId = btn.dataset.orderId;
    const status = btn.dataset.status;
    btn.disabled = true;
    try {
      const fd = new FormData();
      fd.append('order_id', orderId);
      fd.append('status', status);
      await fetch('/update-order-status', { method: 'POST', body: fd });
      await fetchOrders();
    } catch (e) {}
    btn.disabled = false;
  });

  // ── RENDER ORDERS ──
  let lastOrders = [];

  function renderOrders(orders) {
    lastOrders = orders;
    const container = document.getElementById('ordersContainer');
    if (!container) return;

    const filtered = currentFilter === 'All' ? orders : orders.filter(o => o.status === currentFilter);

    // Update stats
    const countPending = orders.filter(o => o.status === 'Pending').length;
    const countPreparing = orders.filter(o => o.status === 'Preparing').length;
    const countReady = orders.filter(o => o.status === 'Ready').length;
    document.getElementById('statPending') && (document.getElementById('statPending').textContent = countPending);
    document.getElementById('statPreparing') && (document.getElementById('statPreparing').textContent = countPreparing);
    document.getElementById('statReady') && (document.getElementById('statReady').textContent = countReady);

    if (!filtered.length) {
      container.innerHTML = '<div class="empty-state"><p>No orders in this category.</p></div>';
      return;
    }

    container.innerHTML = filtered.map(order => {
      const itemsHtml = order.items.map(item =>
        `<div class="order-item-entry"><span><strong>${item.qty}x</strong> ${item.name}</span></div>`
      ).join('');

      const statuses = ['Pending', 'Preparing', 'Ready', 'Served'];
      const statusBtns = statuses.map(s => {
        const isCurrent = order.status === s;
        const cls = isCurrent ? `current-${s.toLowerCase()}` : '';
        return `<button class="status-btn ${cls}" data-order-id="${order.id}" data-status="${s}">${s}</button>`;
      }).join('');

      return `
        <div class="order-card" data-status="${order.status}">
          <div class="order-card-header">
            <span class="order-card-id">Order #${order.id}</span>
            <span class="order-card-time">${timeAgo(order.created_at)}</span>
          </div>
          <div class="order-card-info">
            <span class="order-info-item">👤 ${order.customer_name}</span>
            <span class="order-info-item">🪑 Table ${order.table_number}</span>
            <span class="order-info-item">📞 ${order.phone_number}</span>
          </div>
          <div class="order-items-list">${itemsHtml}</div>
          <div class="order-card-total">
            <span>Total</span>
            <span>KES ${order.total_amount}</span>
          </div>
          <div class="status-buttons">${statusBtns}</div>
        </div>
      `;
    }).join('');
  }

  async function fetchOrders() {
    try {
      const res = await fetch('/api/orders');
      const orders = await res.json();
      renderOrders(orders);
    } catch (e) {}
  }

  // Poll every 2 seconds
  fetchOrders();
  setInterval(fetchOrders, 2000);
});
