/**
 * Start the server
 */
async function startServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;

    if (!confirm(`Démarrer le serveur "${name}" ?`)) {
        return;
    }

    try {
        const resp = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_id: serverId })
        });
        const json = await resp.json();

        if (resp.ok) {
            showAlert(`Serveur "${name}" démarré avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors du démarrage: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Stop the server
 */
async function stopServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;

    if (!confirm(`Arrêter le serveur "${name}" ?`)) {
        return;
    }

    try {
        const resp = await fetch('/api/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_id: serverId })
        });
        const json = await resp.json();

        if (resp.ok) {
            showAlert(`Serveur "${name}" arrêté avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors de l'arrêt: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Reboot the server
*/
async function rebootServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;

    if (!confirm(`Redémarrer le serveur "${name}" ?`)) {
        return;
    }

    try {
        const resp = await fetch('/api/reboot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_id: serverId })
        });
        const json = await resp.json();

        if (resp.ok) {
            showAlert(`Serveur "${name}" redémarré avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors du redémarrage: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
       * Destroy the server
       */
async function destroyServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;

    if (!confirm(`⚠️ ATTENTION: Voulez-vous vraiment DÉTRUIRE le serveur "${name}" ?\n\nCette action est IRRÉVERSIBLE!`)) {
        return;
    }

    // Double confirmation for destructive action
    if (!confirm(`Confirmer la destruction de "${name}" (${serverId})?`)) {
        return;
    }

    try {
        const resp = await fetch('/api/destroy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server_id: serverId })
        });
        const json = await resp.json();

        if (resp.ok) {
            showAlert(`Serveur "${name}" détruit avec succès! Redirection...`, 'success');
            setTimeout(() => {
                globalThis.location.href = '/';
            }, 2000);
        } else {
            showAlert(`Erreur lors de la destruction: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}