// main.js - Global utilities

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.transition = 'opacity 0.5s';
      f.style.opacity = '0';
      setTimeout(() => f.remove(), 500);
    }, 4000);
  });
});

// Time ago helper
function timeAgo(dateStr) {
  const now = new Date();
  const then = new Date(dateStr);
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return `${diff} sec ago`;
  if (diff < 3600) return `${Math.floor(diff/60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)} hr ago`;
  return `${Math.floor(diff/86400)} day ago`;
}

// Status badge HTML
function statusBadge(status) {
  const map = {
    'Pending': 'badge-pending',
    'Preparing': 'badge-preparing',
    'Ready': 'badge-ready',
    'Served': 'badge-served',
    'Cancelled': 'badge-cancelled',
    'Paid': 'badge-paid',
    'Unpaid': 'badge-unpaid',
  };
  return `<span class="badge ${map[status] || ''}">${status}</span>`;
}
