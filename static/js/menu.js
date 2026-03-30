// menu.js - Category filtering, add to cart, My Orders panel

document.addEventListener('DOMContentLoaded', () => {

  // ── CATEGORY TABS ──
  const tabBtns = document.querySelectorAll('.tab-btn[data-category]');
  const sections = document.querySelectorAll('.menu-section');

  function filterCategory(cat) {
    sections.forEach(sec => {
      sec.style.display = (cat === 'All' || sec.dataset.category === cat) ? '' : 'none';
    });
    tabBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.category === cat);
    });
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => filterCategory(btn.dataset.category));
  });
  // Show all by default
  filterCategory('All');

  // ── ADD TO CART ──
  const popup = document.getElementById('cartPopup');
  const popupCount = document.getElementById('popupCount');
  const popupTotal = document.getElementById('popupTotal');
  let cartCount = parseInt(document.getElementById('cartBadge')?.textContent || '0');
  let cartTotal = parseFloat(document.getElementById('cartTotalHidden')?.value || '0');

  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const foodId = btn.dataset.foodId;
      const price = parseFloat(btn.dataset.price);
      btn.disabled = true;
      btn.textContent = '✓';
      try {
        const fd = new FormData();
        fd.append('food_id', foodId);
        const res = await fetch('/add-to-cart', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.success) {
          cartCount = data.cart_count;
          cartTotal += price;
          // Update badge
          const badge = document.getElementById('cartBadge');
          if (badge) badge.textContent = cartCount;
          // Update popup
          if (popupCount) popupCount.textContent = `${cartCount} item${cartCount !== 1 ? 's' : ''}`;
          if (popupTotal) popupTotal.textContent = `KES ${cartTotal.toFixed(0)}`;
          if (popup) popup.classList.add('visible');
        }
      } catch (e) {}
      setTimeout(() => { btn.disabled = false; btn.textContent = '+ Add'; }, 1200);
    });
  });

  // ── MY ORDERS PANEL ──
  const panel = document.getElementById('ordersPanel');
  const overlay = document.getElementById('panelOverlay');
  const openBtn = document.getElementById('openOrdersPanel');
  const closeBtn = document.getElementById('closePanelBtn');
  const phoneInput = document.getElementById('orderPhoneInput');
  const lookupBtn = document.getElementById('lookupOrdersBtn');
  const ordersContainer = document.getElementById('ordersContainer');

  function openPanel() {
    panel?.classList.add('open');
    overlay?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function closePanel() {
    panel?.classList.remove('open');
    overlay?.classList.remove('active');
    document.body.style.overflow = '';
  }

  openBtn?.addEventListener('click', openPanel);
  closeBtn?.addEventListener('click', closePanel);
  overlay?.addEventListener('click', closePanel);

  lookupBtn?.addEventListener('click', async () => {
    const phone = phoneInput?.value.trim();
    if (!phone) { ordersContainer.innerHTML = '<p style="color:var(--text-muted);text-align:center">Please enter your phone number.</p>'; return; }
    ordersContainer.innerHTML = '<p style="text-align:center;color:var(--text-muted)">Looking up orders...</p>';
    try {
      const res = await fetch(`/api/my-orders?phone=${encodeURIComponent(phone)}`);
      const orders = await res.json();
      if (!orders.length) {
        ordersContainer.innerHTML = '<div class="empty-state"><p>No orders found for this number.</p></div>';
        return;
      }
      ordersContainer.innerHTML = orders.map(o => `
        <div class="order-history-card">
          <div class="order-history-header">
            <span class="order-history-id">Order #${o.id}</span>
            ${statusBadge(o.status)}
          </div>
          <div class="order-history-details">
            <span>🪑 Table: ${o.table_number}</span>
            <span>💰 Total: KES ${o.total_amount}</span>
            <span>🕐 ${timeAgo(o.created_at)}</span>
          </div>
        </div>
      `).join('');
    } catch (e) {
      ordersContainer.innerHTML = '<p style="color:red;text-align:center">Error loading orders.</p>';
    }
  });

  // Allow Enter key on phone input
  phoneInput?.addEventListener('keydown', e => { if (e.key === 'Enter') lookupBtn?.click(); });
});
