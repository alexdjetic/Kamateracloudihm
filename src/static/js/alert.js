/**
 * Display an alert message
 */
function showAlert(message, type = 'error') {
    const alerts = document.getElementById('alerts');
    let alertClass;

    if (type === 'error') {
        alertClass = 'bg-red-100 border-red-400 text-red-700';
    } else if (type === 'success') {
        alertClass = 'bg-green-100 border-green-400 text-green-700';
    } else {
        alertClass = 'bg-yellow-100 border-yellow-400 text-yellow-700';
    }

    alerts.innerHTML = `
          <div class="${alertClass} border px-4 py-3 rounded mb-4" role="alert">
            <span class="block sm:inline">${message}</span>
          </div>
        `;
}

/**
 * Get server status badge color
 */
function getStatusColor(status) {
    const statusLower = (status || '').toLowerCase();
    if (statusLower === 'running' || statusLower === 'started') {
        return 'bg-green-100 text-green-800';
    } else if (statusLower === 'stopped') {
        return 'bg-red-100 text-red-800';
    } else {
        return 'bg-gray-100 text-gray-800';
    }
}