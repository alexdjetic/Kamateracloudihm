/**
 * Display an alert message with modern styling
 */
function showAlert(message, type = 'error') {
    const alerts = document.getElementById('alerts');
    let alertClass, icon;

    if (type === 'error') {
        alertClass = 'bg-red-50 border-l-4 border-red-500 text-red-700';
        icon = '❌';
    } else if (type === 'success') {
        alertClass = 'bg-green-50 border-l-4 border-green-500 text-green-700';
        icon = '✅';
    } else {
        alertClass = 'bg-yellow-50 border-l-4 border-yellow-500 text-yellow-700';
        icon = '⚠️';
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `${alertClass} px-4 py-4 rounded-lg mb-4 flex items-start gap-3 shadow-md`;
    alertDiv.innerHTML = `
        <span class="text-xl flex-shrink-0">${icon}</span>
        <div class="flex-1">
            <p class="font-medium">${message}</p>
        </div>
        <button onclick="this.parentElement.remove()" class="flex-shrink-0 text-xl cursor-pointer hover:opacity-70">
            ✕
        </button>
    `;
    
    alerts.appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transition = 'opacity 0.3s ease';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

/**
 * Get server status badge color
 */
function getStatusColor(status) {
    const statusLower = (status || '').toLowerCase();
    if (statusLower === 'running' || statusLower === 'started' || statusLower === 'on') {
        return 'bg-green-100 text-green-800';
    } else if (statusLower === 'stopped' || statusLower === 'off') {
        return 'bg-red-100 text-red-800';
    } else {
        return 'bg-gray-100 text-gray-800';
    }
}