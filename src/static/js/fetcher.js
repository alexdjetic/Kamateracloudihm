/**
 * Fetch and display server details
 */
async function fetchServerDetails() {
    const serverId = getServerIdFromUrl();

    try {
        const resp = await fetch(`/api/server?server_id=${serverId}`);
        const json = await resp.json();

        console.log('Server details:', json);

        const status = json.status ?? resp.status;
        if (status !== 200) {
            showAlert(json.message || 'Erreur lors de la récupération des détails', 'error');
            return;
        }

        serverData = json.data || json;
        const server = serverData;

        // Update header information
        const name = (server?.name || server?.label) || (server?.id || 'Serveur');
        const statusText = server?.status || 'unknown';
        const statusColor = getStatusColor(statusText);

        document.getElementById('server-name').textContent = name;
        document.getElementById('server-id').textContent = `ID: ${serverId}`;

        const statusBadge = document.getElementById('server-status');
        statusBadge.textContent = statusText;
        statusBadge.className = `px-4 py-2 rounded-full text-sm font-medium ${statusColor}`;

        // Render all server information
        renderServerInfo(server);

        showServerDetails();
    } catch (err) {
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Fetch and display servers
 */
async function fetchServers() {
    const container = document.getElementById('servers-container');

    try {
        const resp = await fetch('/api/servers');
        const json = await resp.json();

        console.log('Response JSON:', json);

        const status = json.status ?? resp.status;
        if (status !== 200) {
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