// admin.js - Food CRUD modal, toggles, sidebar

document.addEventListener('DOMContentLoaded', () => {

  // ── SIDEBAR TOGGLE (MOBILE) ──
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  sidebarToggle?.addEventListener('click', () => {
    sidebar?.classList.toggle('open');
    sidebarOverlay?.classList.toggle('active');
  });
  sidebarOverlay?.addEventListener('click', () => {
    sidebar?.classList.remove('open');
    sidebarOverlay?.classList.remove('active');
  });

  // ── ADD FOOD MODAL ──
  const addModal = document.getElementById('addFoodModal');
  document.getElementById('openAddModal')?.addEventListener('click', () => {
    addModal?.classList.add('open');
  });
  document.getElementById('closeAddModal')?.addEventListener('click', () => {
    addModal?.classList.remove('open');
  });
  addModal?.addEventListener('click', (e) => {
    if (e.target === addModal) addModal.classList.remove('open');
  });

  // ── EDIT FOOD MODAL ──
  const editModal = document.getElementById('editFoodModal');
  document.querySelectorAll('.edit-food-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('editId').value = btn.dataset.id;
      document.getElementById('editName').value = btn.dataset.name;
      document.getElementById('editCategory').value = btn.dataset.category;
      document.getElementById('editPrice').value = btn.dataset.price;
      document.getElementById('editAvailable').value = btn.dataset.available;
      editModal?.classList.add('open');
    });
  });
  document.getElementById('closeEditModal')?.addEventListener('click', () => {
    editModal?.classList.remove('open');
  });
  editModal?.addEventListener('click', (e) => {
    if (e.target === editModal) editModal.classList.remove('open');
  });

  // ── DELETE CONFIRM ──
  document.querySelectorAll('.delete-food-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm(`Delete "${btn.dataset.name}"? This cannot be undone.`)) {
        e.preventDefault();
      }
    });
  });

  // ── AVAILABILITY TOGGLE ──
  document.querySelectorAll('.avail-toggle').forEach(checkbox => {
    checkbox.addEventListener('change', async () => {
      const id = checkbox.dataset.id;
      try {
        const fd = new FormData();
        const res = await fetch(`/admin-food/toggle/${id}`, { method: 'POST', body: fd });
        const data = await res.json();
        // Update label next to toggle
        const label = checkbox.closest('td')?.querySelector('.avail-label');
        if (label) label.textContent = data.available ? 'Active' : 'Off';
        if (label) label.style.color = data.available ? '#15803D' : '#B91C1C';
      } catch (e) { checkbox.checked = !checkbox.checked; }
    });
  });
});
