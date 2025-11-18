/**
 * Start the server
 */
async function startServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;
    console.log('[DEBUG] startServer() called with serverId:', serverId, 'name:', name);

    if (!confirm(`Démarrer le serveur "${name}" ?`)) {
        console.log('[DEBUG] User cancelled start confirmation');
        return;
    }

    try {
        const payload = { server_id: serverId };
        console.log('[DEBUG] Sending POST to /api/start with payload:', payload);
        
        const resp = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        console.log('[DEBUG] Response status:', resp.status, 'ok:', resp.ok);
        
        const json = await resp.json();
        console.log('[DEBUG] Response JSON:', json);

        if (resp.ok) {
            showAlert(`Serveur "${name}" démarré avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors du démarrage: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        console.log('[DEBUG] Exception caught:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Stop the server
 */
async function stopServer() {
    const serverId = getServerIdFromUrl();
    const name = document.getElementById('server-name').textContent;
    console.log('[DEBUG] stopServer() called with serverId:', serverId);

    if (!confirm(`Arrêter le serveur "${name}" ?`)) {
        console.log('[DEBUG] User cancelled stop confirmation');
        return;
    }

    try {
        const payload = { server_id: serverId };
        console.log('[DEBUG] Sending POST to /api/stop with payload:', payload);
        
        const resp = await fetch('/api/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        console.log('[DEBUG] Response status:', resp.status);
        
        const json = await resp.json();
        console.log('[DEBUG] Response JSON:', json);

        if (resp.ok) {
            showAlert(`Serveur "${name}" arrêté avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors de l'arrêt: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        console.log('[DEBUG] Exception:', err);
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
    console.log('[DEBUG] destroyServer() called with serverId:', serverId);

    if (!confirm(`⚠️ ATTENTION: Voulez-vous vraiment DÉTRUIRE le serveur "${name}" ?\n\nCette action est IRRÉVERSIBLE!`)) {
        console.log('[DEBUG] User cancelled first destroy confirmation');
        return;
    }

    // Double confirmation for destructive action
    if (!confirm(`Confirmer la destruction de "${name}" (${serverId})?`)) {
        console.log('[DEBUG] User cancelled second destroy confirmation');
        return;
    }

    try {
        console.log('[DEBUG] Sending DELETE to /api/destroy?server_id=' + serverId);
        
        const resp = await fetch('/api/destroy?server_id=' + encodeURIComponent(serverId), {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        console.log('[DEBUG] Response status:', resp.status);
        
        const json = await resp.json();
        console.log('[DEBUG] Response JSON:', json);

        if (resp.ok) {
            showAlert(`Serveur "${name}" détruit avec succès! Redirection...`, 'success');
            setTimeout(() => {
                globalThis.location.href = '/';
            }, 2000);
        } else {
            showAlert(`Erreur lors de la destruction: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        console.log('[DEBUG] Exception:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Clone the server with a new public IP
 */
async function cloneServer() {
    const serverId = getServerIdFromUrl();
    const currentName = document.getElementById('server-name').textContent;
    console.log('[DEBUG] cloneServer() called with serverId:', serverId);

    // Ask user for clone name
    const cloneName = prompt(`Entrez un nom pour le clone de "${currentName}":\n\n(Laisser vide pour laisser Kamatera générer un nom)`);
    
    if (cloneName === null) {
        console.log('[DEBUG] User cancelled clone name prompt');
        return;
    }

    // Ask for password
    const password = prompt(`Entrez le mot de passe root pour le nouveau clone:\n\n(Ce champ est requis)`);
    
    if (password === null) {
        console.log('[DEBUG] User cancelled password prompt');
        return;
    }

    if (!password.trim()) {
        showAlert('Le mot de passe ne peut pas être vide', 'error');
        return;
    }

    if (!confirm(`Cloner le serveur "${currentName}"${cloneName ? ` en "${cloneName}"` : ''}?\n\nLe nouveau serveur aura une nouvelle IP publique, ne sera pas démarré, et sera facturé à l'heure.`)) {
        console.log('[DEBUG] User cancelled clone confirmation');
        return;
    }

    try {
        const payload = { 
            server_id: serverId,
            password: password.trim(),
            billing: "hour"
        };
        if (cloneName.trim()) {
            payload.name = cloneName.trim();
        }
        console.log('[DEBUG] Sending POST to /api/clone with payload:', payload);
        
        const resp = await fetch('/api/clone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        console.log('[DEBUG] Response status:', resp.status);
        
        const json = await resp.json();
        console.log('[DEBUG] Response JSON:', json);

        if (resp.ok) {
            showAlert(`Serveur cloné avec succès! Redirection...`, 'success');
            setTimeout(() => {
                globalThis.location.href = '/';
            }, 2000);
        } else {
            showAlert(`Erreur lors du clonage: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        console.log('[DEBUG] Exception:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}

/**
 * Rename the server
 */
async function renameServer() {
    const serverId = getServerIdFromUrl();
    const currentName = document.getElementById('server-name').textContent;
    console.log('[DEBUG] renameServer() called with serverId:', serverId, 'currentName:', currentName);

    const newName = prompt(`Entrez le nouveau nom du serveur:\n\n(Actuellement: "${currentName}")`);
    
    if (newName === null) {
        console.log('[DEBUG] User cancelled rename prompt');
        return;
    }

    if (!newName.trim()) {
        showAlert('Le nom du serveur ne peut pas être vide', 'error');
        return;
    }

    try {
        const payload = { server_id: serverId, name: newName.trim() };
        console.log('[DEBUG] Sending PUT to /api/rename with payload:', payload);
        
        const resp = await fetch('/api/rename', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        console.log('[DEBUG] Response status:', resp.status);
        
        const json = await resp.json();
        console.log('[DEBUG] Response JSON:', json);

        if (resp.ok) {
            showAlert(`Serveur renommé en "${newName}" avec succès!`, 'success');
            setTimeout(() => fetchServerDetails(), 2000);
        } else {
            showAlert(`Erreur lors du renommage: ${json.message || 'Erreur inconnue'}`, 'error');
        }
    } catch (err) {
        console.log('[DEBUG] Exception:', err);
        showAlert(`Erreur réseau: ${err.message || err}`, 'error');
    }
}
