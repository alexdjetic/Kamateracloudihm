# Kamatera Cloud IHM (interface de gestion)

Interface web et CLI pour lister et piloter des serveurs via l'API Kamatera.

## Modes d'utilisation

### 1. Interface Web (app.py)
Interface graphique moderne avec Tailwind CSS accessible via navigateur.

### 2. Interface CLI (app-cli.py)
Interface en ligne de commande pour gérer les serveurs depuis le terminal.

## Structure du projet

```
src/
	app.py                       # application FastAPI (interface web)
	app-cli.py                   # interface CLI
	kamatera-cli.sh              # wrapper shell pour le CLI
	pyproject.toml               # dépendances
	README.md                    # cette documentation
	CLI_README.md                # documentation détaillée du CLI
	template/
		index.html                 # page liste des serveurs (Tailwind CSS)
		detail.html                # page détail d'un serveur (Tailwind CSS)
	static/                      # fichiers statiques (css/js/images) - actuellement vide
	kamatera/
		Kamatera_cloud_management.py  # wrapper autour des endpoints Kamatera
		auth_kamatera.py              # gestion authentification OAuth
	route/
		list_route.py                 # endpoints de consultation (GET)
		control_route.py              # endpoints de contrôle (POST)
	models/
		control_modele.py             # modèles Pydantic
	logger.py                    # helper pour logging centralisé
```

## Prérequis

- Python 3.9+ (ou l'environnement que vous utilisez pour exécuter uvicorn)
- Les dépendances listées dans `pyproject.toml` : `fastapi`, `jinja2`, `requests`, `uvicorn[standard]`, etc.

Installez-les avec pip si nécessaire :

```bash
python3 -m pip install --user fastapi jinja2 requests uvicorn[standard]
```

Si vous utilisez Poetry ou un autre gestionnaire, installez via votre workflow habituel.

## Configuration

L'application (web et CLI) attend des identifiants Kamatera configurés via variables d'environnement :

**Option 1 : Clé API directe**
```bash
export KAMATERA_API_KEY="votre_clef_ici"
```

**Option 2 : OAuth (Client ID + Secret)**
```bash
export KAMATERA_CLIENT_ID="votre_client_id"
export KAMATERA_SECRET="votre_secret"
```

Sans ces variables, l'UI et le CLI afficheront un message d'erreur d'authentification.

## Lancer l'application

### Interface Web

Depuis le dossier `src/`, lancez uvicorn :

```bash
cd src
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Ou avec uv :

```bash
cd src
uv run app.py
```

Ensuite :

- UI (HTML) : http://127.0.0.1:8000/
- Détail serveur : http://127.0.0.1:8000/server/{server_id}
- API (JSON) : http://127.0.0.1:8000/api/servers
- Health : http://127.0.0.1:8000/health

### Interface CLI

```bash
cd src

# Avec uv (recommandé)
uv run app-cli.py list

# Avec le wrapper shell
./kamatera-cli.sh list

# Voir toutes les commandes
uv run app-cli.py --help
```

**Commandes disponibles :**
- `list` : Liste tous les serveurs
- `details <server_id>` : Affiche les détails d'un serveur
- `start <server_id>` : Démarre un serveur
- `stop <server_id>` : Arrête un serveur
- `reboot <server_id>` : Redémarre un serveur
- `destroy <server_id>` : Détruit un serveur (irréversible)

Consultez [CLI_README.md](CLI_README.md) pour la documentation complète du CLI.

## Endpoints API disponibles

### Routes de consultation (GET)
- GET `/api/servers` : Liste tous les serveurs
- GET `/api/server?server_id=<id>` : Détails d'un serveur spécifique

### Routes de contrôle (POST)
- POST `/api/start` : Démarre un serveur
- POST `/api/stop` : Arrête un serveur
- POST `/api/reboot` : Redémarre un serveur
- POST `/api/destroy` : Détruit un serveur

### Routes UI (HTML)
- GET `/` : Page d'accueil listant les serveurs
- GET `/server/{server_id}` : Page détail d'un serveur

## `kamatera/Kamatera_cloud_management.py`

Ce fichier contient une classe `KamateraCloudManagement` qui encapsule des méthodes pour appeler l'API Kamatera :

- `list_servers()` : Liste tous les serveurs
- `get_server_details(server_id)` : Récupère les détails d'un serveur
- `create_server(server_data)` : Crée un nouveau serveur
- `delete_server(server_id)` : Supprime un serveur
- `start_server(server_id)` : Démarre un serveur
- `stop_server(server_id)` : Arrête un serveur
- `reboot_server(server_id)` : Redémarre un serveur
- `resize_server(server_id, new_size)` : Redimensionne un serveur
- `clone_server(server_id, clone_data)` : Clone un serveur

Ces méthodes utilisent `requests` pour faire des appels HTTP et retournent des réponses formatées uniformément avec les clés `message`, `status` et `data`.

## Interface utilisateur (UI)

L'interface web utilise **Tailwind CSS** pour un design moderne et responsive :

- **Page principale** (`/`) : Grille de cartes affichant tous les serveurs
  - Boutons : Détails, Démarrer, Détruire
  - Statut coloré (vert=running, rouge=stopped, gris=autre)
  - Chargement asynchrone des données

- **Page détail** (`/server/{id}`) : Vue détaillée d'un serveur
  - Boutons d'action : Démarrer, Arrêter, Redémarrer, Détruire
  - Affichage de toutes les propriétés du serveur
  - Confirmations pour actions destructives

Le JavaScript est organisé en fonctions modulaires directement dans les templates HTML.

## Prochaines améliorations suggérées

- Ajouter la création de serveurs via l'UI et le CLI
- Ajouter des tests unitaires (pytest) avec `requests-mock`
- Mettre en place CI (lint, tests) et checks de sécurité
- Pagination pour les grandes listes de serveurs
- Filtrage et recherche dans la liste des serveurs
- Gestion des snapshots via l'UI/CLI
- Historique des actions effectuées

## Exemples d'utilisation

### Via l'interface web
1. Lancez `uv run app.py`
2. Ouvrez http://localhost:8000
3. Cliquez sur "Détails" pour voir un serveur
4. Utilisez les boutons d'action pour gérer vos serveurs

### Via le CLI
```bash
# Configuration
export KAMATERA_API_KEY="votre_clef"

# Lister les serveurs
uv run app-cli.py list

# Démarrer un serveur
uv run app-cli.py start abc123def456 -y

# Voir les détails en JSON
uv run app-cli.py details abc123def456 --json

# Script automation
for server in $(uv run app-cli.py list --json | jq -r '.[].id'); do
    echo "Checking $server..."
    uv run app-cli.py details "$server"
done
```

## Support et contact

Pour toute question, ouvrir une issue avec le détail et les logs. Si vous souhaitez que j'ajoute des fonctionnalités (UI de création, suppression, tests), dites lesquelles et je les implémente.

