/**
 * Get status color classes for dark theme
 */
function getStatusColor(status) {
    if (!status) return 'bg-gray-600/30 text-gray-300';
    const lower = String(status).toLowerCase();
    if (lower === 'on' || lower === 'running' || lower === 'active') {
        return 'bg-green-500/30 text-green-300';
    }
    if (lower === 'off' || lower === 'stopped' || lower === 'inactive') {
        return 'bg-red-500/30 text-red-300';
    }
    return 'bg-yellow-500/30 text-yellow-300';
}

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
 * Render server information as key-value pairs in a grid with dark theme
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
            <div class="bg-gray-900/50 border border-gray-700/30 rounded-lg p-4 ${gridClass} hover:border-blue-500/30 transition-colors">
              <dt class="text-xs font-bold text-blue-300 uppercase tracking-wider mb-2">🔹 ${displayKey}</dt>
              <dd class="text-sm text-gray-100 font-medium break-words">${displayValue}</dd>
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
    if (!container) return;
    
    container.innerHTML = '';

    if (servers.length === 0) {
        document.getElementById('loading')?.classList.add('hidden');
        document.getElementById('empty-state')?.classList.remove('hidden');
        return;
    }

    for (const server of servers) {
        const card = renderServerCard(server);
        container.appendChild(card);
    }
}

/**
 * Render a single server card with Tailwind CSS
 */
function renderServerCard(server) {
    const name = (server?.name || server?.label) || (server?.id || 'Serveur');
    const power = server?.power || 'unknown';
    const statusText = power === 'on' ? '🟢 En ligne' : '🔴 Hors ligne';
    const statusBg = power === 'on' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300';
    const idText = server?.id || '-';
    const cpu = server?.cpu || '?';
    const ram = server?.ram || '?';
    const datacenter = server?.datacenter || server?.dc || '-';

    const card = document.createElement('div');
    card.className = 'group bg-gradient-to-br from-gray-800/80 to-gray-900/60 backdrop-blur-sm border border-gray-700/50 hover:border-blue-500/50 rounded-2xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/20 hover:-translate-y-1';
    
    card.innerHTML = `
        <div class="h-full flex flex-col">
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1 min-w-0">
                    <h3 class="text-xl font-bold text-white truncate group-hover:text-blue-300 transition-colors">${name}</h3>
                </div>
                <span class="ml-3 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${statusBg}">
                    ${statusText}
                </span>
            </div>
            
            <div class="flex gap-2 mb-5 pb-4 border-b border-gray-700/30">
                <span class="text-xs font-bold px-2.5 py-1.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    <span class="text-sm">⚙️</span> ${cpu}
                </span>
                <span class="text-xs font-bold px-2.5 py-1.5 rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    <span class="text-sm">💾</span> ${ram}
                </span>
            </div>
            
            <div class="grid grid-cols-1 gap-3 mb-6 py-4">
                <div class="bg-gray-900/50 rounded-lg p-3 text-center border border-gray-700/30 group-hover:border-blue-500/30 transition-colors">
                    <div class="text-lg font-bold text-blue-400">${datacenter}</div>
                    <div class="text-xs text-gray-500 uppercase tracking-wider mt-1">Datacenter</div>
                </div>
            </div>
            
            <div class="mt-auto pt-4 border-t border-gray-700/30 flex flex-col gap-2">
                <button onclick="viewDetails('${idText}')" class="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white text-sm font-semibold rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40">
                    📋 Détails
                </button>
                <div class="flex gap-2">
                    <button onclick="startServerQuick('${idText}')" class="flex-1 px-3 py-2.5 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white text-sm font-semibold rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40">
                        ▶
                    </button>
                    <button onclick="stopServerQuick('${idText}')" class="flex-1 px-3 py-2.5 bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-700 hover:to-rose-800 text-white text-sm font-semibold rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-rose-500/20 hover:shadow-rose-500/40">
                        ⏹
                    </button>
                </div>
            </div>
        </div>
    `;
    return card;
}

/**
 * View server details
 */
function viewDetails(serverId) {
    globalThis.location.href = `/server/${serverId}`;
}

/**
 * Quick action helper functions for list view
 */
function quickStart(serverId) {
    // Will be implemented in control.js
    if (typeof startServerQuick === 'function') {
        startServerQuick(serverId);
    }
}

function quickStop(serverId) {
    // Will be implemented in control.js
    if (typeof stopServerQuick === 'function') {
        stopServerQuick(serverId);
    }
}