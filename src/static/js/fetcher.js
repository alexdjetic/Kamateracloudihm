/**
 * Fetch and display server details
 * Falls back to fetching from the servers list if the detail endpoint fails
 */
async function fetchServerDetails() {
    const serverId = getServerIdFromUrl();
    console.log('[DEBUG] getServerIdFromUrl() returned:', serverId);
    console.log('[DEBUG] SERVER_ID variable:', typeof SERVER_ID !== 'undefined' ? SERVER_ID : 'NOT DEFINED');

    const url = `/api/server?server_id=${serverId}`;
    console.log('[DEBUG] Fetching from URL:', url);

    try {
        const resp = await fetch(url);
        console.log('[DEBUG] Response status:', resp.status);
        const json = await resp.json();

        console.log('[DEBUG] Server details response:', json);
        console.log('[DEBUG] Response status from json:', json.status);
        console.log('[DEBUG] Response message:', json.message);

        const status = json.status ?? resp.status;
        if (status !== 200) {
            console.log('[DEBUG] Error detected. Status:', status, 'Message:', json.message);
            console.log('[DEBUG] Attempting fallback: fetching from /api/servers list');
            
            // Fallback: fetch from servers list
            await fetchServerDetailsFromList(serverId);
            return;
        }

        serverData = json.data || json;
        console.log('[DEBUG] serverData type:', typeof serverData, 'isArray:', Array.isArray(serverData));
        const server = Array.isArray(serverData) ? serverData[0] : serverData;
        console.log('[DEBUG] server object:', server);

        // Update header information
        const name = (server?.name || server?.label) || (server?.id || 'Serveur');
        const statusText = server?.status || server?.power || 'unknown';
        const statusColor = getStatusColor(statusText);

        console.log('[DEBUG] Setting name:', name, 'statusText:', statusText);
        document.getElementById('server-name').textContent = name;
        document.getElementById('server-id').textContent = `ID: ${server?.id || 'unknown'}`;

        const statusBadge = document.getElementById('server-status');
        statusBadge.textContent = statusText;
        statusBadge.className = `px-4 py-2 rounded-full text-sm font-medium ${statusColor}`;

        // Render all server information
        console.log('[DEBUG] Server data before render:', server);
        console.log('[DEBUG] Calling renderServerInfo...');
        renderServerInfo(server);
        console.log('[DEBUG] renderServerInfo completed');

        showServerDetails();
    } catch (err) {
        console.log('[DEBUG] Exception in fetchServerDetails:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Fallback: fetch server details from the servers list
 */
async function fetchServerDetailsFromList(serverId) {
    console.log('[DEBUG] fetchServerDetailsFromList called with serverId:', serverId);
    
    try {
        const resp = await fetch('/api/servers');
        console.log('[DEBUG] Servers list response status:', resp.status);
        const json = await resp.json();

        const status = json.status ?? resp.status;
        if (status !== 200) {
            console.log('[DEBUG] Error fetching servers list. Status:', status);
            showAlert('Impossible de récupérer les détails du serveur', 'error');
            return;
        }

        const items = Array.isArray(json.data) ? json.data : (json.data?.servers ?? []);
        console.log('[DEBUG] Found', items.length, 'servers in list');
        
        // Find the server with matching ID
        const server = items.find(s => s.id === serverId);
        
        if (!server) {
            console.log('[DEBUG] Server not found in list');
            showAlert(`Serveur ${serverId} non trouvé`, 'error');
            return;
        }

        console.log('[DEBUG] Found server in list:', server);
        serverData = server;

        // Update header information
        const name = (server?.name || server?.label) || (server?.id || 'Serveur');
        const statusText = server?.power || server?.status || 'unknown';
        const statusColor = getStatusColor(statusText);

        document.getElementById('server-name').textContent = name;
        document.getElementById('server-id').textContent = `ID: ${serverId}`;

        const statusBadge = document.getElementById('server-status');
        statusBadge.textContent = statusText;
        statusBadge.className = `px-4 py-2 rounded-full text-sm font-medium ${statusColor}`;

        // Render all server information
        console.log('[DEBUG] Server data before render (fallback):', server);
        renderServerInfo(server);
        
        showAlert('Affichage des informations de base (détails complets indisponibles)', 'warning');
        showServerDetails();
    } catch (err) {
        console.log('[DEBUG] Exception in fetchServerDetailsFromList:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Fetch and display servers
 */
async function fetchServers() {
    const container = document.getElementById('servers-container');
    console.log('[DEBUG] Fetching servers list from /api/servers');

    try {
        const resp = await fetch('/api/servers');
        console.log('[DEBUG] Response status:', resp.status);
        const json = await resp.json();

        console.log('[DEBUG] Servers response:', json);
        console.log('[DEBUG] Response data:', json.data);

        const status = json.status ?? resp.status;
        if (status !== 200) {
            console.log('[DEBUG] Error: Status', status, 'Message:', json.message);
            showAlert(json.message || 'Erreur lors de la récupération des serveurs', 'error');
            removeLoading();
            return;
        }

        const items = Array.isArray(json.data) ? json.data : (json.data?.servers ?? []);
        removeLoading();

        if (!items || items.length === 0) {
            container.innerHTML = `
              <div class="bg-yellow-100 border-yellow-400 text-yellow-700 border px-4 py-3 rounded" role="alert">
                <span class="block sm:inline">Aucun serveur trouvé.</span>
              </div>
            `;
            return;
        }

        renderServerList(items);
    } catch (err) {
        removeLoading();
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}