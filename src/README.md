
# Kamatera Cloud IHM (interface de gestion)

Petite interface web pour lister et piloter des serveurs via l'API Kamatera.

## Structure du projet

```
src/
	app.py                       # application FastAPI
	pyproject.toml               # dépendances
	README.md                    # cette documentation
	template/
		index.html                 # template Jinja2 pour l'UI
	static/                      # fichiers statiques (css/js/images) - actuellement vide
	classes/
		Kamatera_cloud_management.py  # wrapper minimal autour des endpoints Kamatera
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

L'application attend une variable d'environnement `KAMATERA_API_KEY` contenant votre clé API Kamatera. Exemple :

```bash
export KAMATERA_API_KEY="votre_clef_ici"
```

Sans cette variable, l'UI affichera un message expliquant comment configurer la clé et les endpoints API renverront une erreur 401.

## Lancer l'application

Depuis le dossier `src/`, lancez uvicorn :

```bash
cd src
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Ensuite :

- UI (HTML) : http://127.0.0.1:8000/ui
- API (JSON) : http://127.0.0.1:8000/api/servers
- Racine (info) : http://127.0.0.1:8000/

## Endpoints disponibles

- GET `/api/servers` : renvoie la réponse JSON brute de l'appel à l'API Kamatera (nécessite `KAMATERA_API_KEY`).
- GET `/ui` : interface HTML listant les serveurs (template `template/index.html`).
- GET `/` : page racine — renvoie JSON d'information ou la liste selon configuration.

## `classes/Kamatera_cloud_management.py`

Ce fichier contient une classe `KamateraCloudManagement` qui encapsule des méthodes pour appeler l'API Kamatera :

- `list_servers()`
- `create_server(server_data)`
- `delete_server(server_id)`
- `reboot_server(server_id)`
- `get_server_details(server_id)`
- `stop_server(server_id)`
- `start_server(server_id)`
- `resize_server(server_id, new_size)`
- `clone_server(server_id, clone_data)`

Ces méthodes utilisent `requests` pour faire des appels HTTP et retournent `response.json()` sans transformation. En production il est préférable d'ajouter :

- gestion d'erreurs HTTP (status codes, timeouts)
- validations des réponses
- retries/backoff pour erreurs transitoires

## Développement local sans clé réelle

Si vous voulez développer l'UI sans appeler l'API réelle, vous pouvez :

1. Modifier temporairement `Kamatera_cloud_management.list_servers` pour renvoyer une liste mock :

```py
def list_servers(self):
		return [{"id": "srv-1", "name": "test-1", "status": "running"}]
```

2. Ou écrire un wrapper/mock et injecter l'instance dans `app` (future amélioration).

## Prochaines améliorations suggérées

- Ajouter des formulaires dans l'UI pour créer/supprimer/rebooter des serveurs (POST/DELETE via JS + endpoints dans `app.py`).
- Ajouter des tests unitaires (pytest) avec `requests-mock` pour la classe `Kamatera_cloud_management`.
- Mettre en place CI (lint, tests) et checks de sécurité.
- Gérer les erreurs réseau proprement (timeouts, code non 2xx).

## Support et contact

Pour toute question, ouvrir une issue avec le détail et les logs. Si vous souhaitez que j'ajoute des fonctionnalités (UI de création, suppression, tests), dites lesquelles et je les implémente.

