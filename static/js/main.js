/* Arena-Match — JavaScript principal */

// Auto-ocultar alertas después de 4 segundos
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Marcar fecha mínima en inputs de fecha (fecha_fin >= fecha_inicio)
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]');
    const fechaFin    = document.querySelector('input[name="fecha_fin"]');
    if (fechaInicio && fechaFin) {
        fechaInicio.addEventListener('change', function () {
            fechaFin.min = this.value;
        });
    }
});
