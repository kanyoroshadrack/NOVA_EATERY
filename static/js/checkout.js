// checkout.js - Form validation and checkbox enforcement
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('checkoutForm');
  const checkbox = document.getElementById('mpesaConfirm');
  const submitBtn = document.getElementById('submitOrderBtn');

  function updateSubmitState() {
    if (submitBtn) {
      submitBtn.disabled = !checkbox?.checked;
      submitBtn.style.opacity = checkbox?.checked ? '1' : '0.5';
    }
  }

  checkbox?.addEventListener('change', updateSubmitState);
  updateSubmitState();

  form?.addEventListener('submit', (e) => {
    const name = document.getElementById('customerName')?.value.trim();
    const phone = document.getElementById('customerPhone')?.value.trim();
    const table = document.getElementById('tableNumber')?.value;
    if (!name || !phone || !table) {
      e.preventDefault();
      alert('Please fill in all required fields.');
      return;
    }
    if (!checkbox?.checked) {
      e.preventDefault();
      alert('Please confirm you have sent the M-PESA payment.');
      return;
    }
    submitBtn.textContent = 'Placing order...';
    submitBtn.disabled = true;
  });
});
