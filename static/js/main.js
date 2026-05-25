/* Arena Match — main.js */

// Auto-dismiss flash messages after 4s
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 4000);
  });

  // Confirm on delete buttons
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm(form.dataset.confirm || '¿Estás seguro?')) {
        e.preventDefault();
      }
    });
  });

  // Highlight active nav link based on URL path
  const path = window.location.pathname.split('/')[1];
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (path && href.includes(path)) {
      link.classList.add('active');
    }
  });
});
