// cart.js - Cart quantity controls and live totals
document.addEventListener('DOMContentLoaded', () => {
  // All quantity/delete buttons use form POST — handled server-side
  // This file handles any client-side enhancements

  // Confirm before any delete
  document.querySelectorAll('.cart-delete-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      // Allow immediate removal without confirm for UX
    });
  });
});
