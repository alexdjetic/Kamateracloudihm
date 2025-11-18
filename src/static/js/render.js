/**
 * Format a value for display based on its type and key
 */
function formatValue(key, value) {
    if (value === null || value === undefined || value === '') {
        return '-';
    }

    // Handle arrays
    if (Array.isArray(value)) {
        if (key === 'diskSizes') {
            return value.map(size => `${size} GB`).join(', ');
        }
        if (key === 'networks') {
            return value.map(net => {
                const ips = net.ips ? net.ips.join(', ') : 'N/A';
                return `${net.network}: ${ips}`;
            }).join(' | ');
        }
        return value.join(', ');
    }

    // Handle numeric values
    if (typeof value === 'number') {
        if (key === 'ram') {
            return `${value} MB`;
        }
        if (key === 'traffic') {
            return `${value} GB`;
        }
        if (key === 'managed' || key === 'backup') {
            return value === '1' || value === 1 ? 'Activé' : 'Désactivé';
        }
        return value.toString();
    }

    // Handle boolean or 0/1 for managed/backup
    if (key === 'managed' || key === 'backup') {
        return value === '1' || value === 1 || value === true ? 'Activé' : 'Désactivé';
    }

    // Handle power status
    if (key === 'power') {
        return value === 'on' ? '🟢 Allumé' : '🔴 Éteint';
    }

    return String(value);
}

/**
 * Format a key for display (humanize)
 */
function formatKey(key) {
    const keyMap = {
        'id': 'ID du serveur',
        'name': 'Nom',
        'datacenter': 'Centre de données',
        'cpu': 'CPU',
        'ram': 'Mémoire',
        'power': 'État',
        'diskSizes': 'Disques',
        'networks': 'Réseaux & IPs',
        'billing': 'Mode de facturation',
        'traffic': 'Trafic',
        'managed': 'Serveur géré',
        'backup': 'Sauvegarde'
    };
    return keyMap[key] || key.charAt(0).toUpperCase() + key.slice(1);
}

/**
 * Render server information as key-value pairs in a grid
 */
function renderServerInfo(server) {
    console.log('[RENDER] renderServerInfo called with:', server);
    const infoContainer = document.getElementById('server-info');
    console.log('[RENDER] infoContainer element:', infoContainer);
    
    if (!infoContainer) {
        console.error('[RENDER] server-info container not found!');
        return;
    }
    
    // Define the order and which fields to show
    const fieldsToShow = [
        'id', 'name', 'datacenter', 'cpu', 'ram', 'power',
        'diskSizes', 'networks', 'billing', 'traffic', 'managed', 'backup'
    ];

    const html = fieldsToShow.map(key => {
        const value = server[key];
        if (value === undefined) return '';
        
        const displayKey = formatKey(key);
        const displayValue = formatValue(key, value);
        
        // Determine if this is a full-width field
        const isFullWidth = key === 'networks' || key === 'id';
        const gridClass = isFullWidth ? 'md:col-span-2 lg:col-span-3' : '';

        return `
            <div class="bg-gray-50 rounded-lg p-4 ${gridClass}">
              <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">${displayKey}</dt>
              <dd class="text-sm text-gray-900 font-medium break-words">${displayValue}</dd>
            </div>
          `;
    }).join('');
    
    console.log('[RENDER] Generated HTML length:', html.length);
    infoContainer.innerHTML = html;
    console.log('[RENDER] HTML set to container');
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