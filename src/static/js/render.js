/**
 * Render server information as key-value pairs
 */
function renderServerInfo(server) {
    const infoContainer = document.getElementById('server-info');
    const entries = Object.entries(server);

    infoContainer.innerHTML = entries.map(([key, value]) => {
        // Skip rendering complex objects or arrays
        if (typeof value === 'object' && value !== null) {
            value = JSON.stringify(value, null, 2);
        }

        return `
            <div class="border-b border-gray-200 pb-3">
              <dt class="text-sm font-medium text-gray-500 mb-1">${key}</dt>
              <dd class="text-sm text-gray-900 break-all">${value || '-'}</dd>
            </div>
          `;
    }).join('');
}

/**
 * Render the list of servers
 */
function renderServerList(servers) {
    const container = document.getElementById('servers-container');
    container.innerHTML = '';

    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';

    for (const server of servers) {
        const card = renderServerCard(server);
        grid.appendChild(card);
    }

    container.appendChild(grid);
}

/**
 * Render a single server card
 */
function renderServerCard(server) {
    const name = (server?.name || server?.label) || (server?.id || 'Serveur');
    const statusText = server?.status || 'unknown';
    const idText = server?.id || '-';
    const statusColor = getStatusColor(statusText);

    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6';
    card.innerHTML = `
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-xl font-semibold text-gray-900">${name}</h3>
              <p class="text-sm text-gray-500 mt-1">ID: ${idText}</p>
            </div>
            <span class="px-3 py-1 rounded-full text-xs font-medium ${statusColor}">
              ${statusText}
            </span>
          </div>
          <div class="flex gap-2">
            <button 
              onclick="viewDetails('${idText}')"
              class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded transition-colors">
              Détails
            </button>
            <button 
              onclick="startServer('${idText}', '${name}')"
              class="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded transition-colors">
              Démarrer
            </button>
            <button 
              onclick="destroyServer('${idText}', '${name}')"
              class="flex-1 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded transition-colors">
              Détruire
            </button>
          </div>
        `;
    return card;
}