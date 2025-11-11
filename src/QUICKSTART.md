# Guide de Démarrage Rapide - Kamatera Cloud IHM

## Installation en 3 étapes

### 1. Cloner et installer

```bash
cd /Users/alexandre/Kamateracloudihm/src
make install
```

### 2. Configurer les identifiants

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer et ajouter votre clé API
export KAMATERA_API_KEY="votre_clef_ici"
```

### 3. Lancer l'application

**Interface Web:**
```bash
make run-web
# Ouvrir http://localhost:8000
```

**Interface CLI:**
```bash
make list
# ou
uv run app-cli.py list
```

## Exemples d'utilisation rapide

### Interface Web

1. **Voir tous les serveurs**
   - Allez sur http://localhost:8000
   - Les serveurs s'affichent en cartes avec leur statut

2. **Voir les détails d'un serveur**
   - Cliquez sur "Détails" sur une carte
   - Vous verrez toutes les propriétés du serveur

3. **Démarrer un serveur**
   - Cliquez sur "Démarrer" (bouton vert)
   - Confirmez dans la popup

4. **Détruire un serveur**
   - Cliquez sur "Détruire" (bouton rouge)
   - Confirmez deux fois (action irréversible!)

### Interface CLI

```bash
# Lister tous les serveurs
make list

# Voir les détails d'un serveur
make details SERVER_ID=abc123def456

# Démarrer un serveur (avec confirmation)
make start SERVER_ID=abc123def456

# Démarrer sans confirmation
uv run app-cli.py start abc123def456 -y

# Arrêter un serveur
uv run app-cli.py stop abc123def456

# Redémarrer un serveur
uv run app-cli.py reboot abc123def456

# Format JSON pour scripting
uv run app-cli.py list --json | jq '.'
```

## Commandes Make disponibles

```bash
make help      # Afficher l'aide
make install   # Installer les dépendances
make run-web   # Lancer l'interface web
make run-cli   # Aide du CLI
make list      # Lister les serveurs
make clean     # Nettoyer les fichiers temporaires
```

## Dépannage rapide

### "Aucune clé API trouvée"
```bash
export KAMATERA_API_KEY="votre_clef"
```

### "Command not found: uv"
Installez uv: https://docs.astral.sh/uv/

### L'interface web ne se lance pas
```bash
cd src
uv run app.py
```

### Activer le mode debug
```bash
export LOG_LEVEL=DEBUG
make run-web
```

## Architecture rapide

```
┌─────────────────────────────────────────┐
│        Interface Utilisateur            │
├──────────────────┬──────────────────────┤
│   Web (app.py)   │   CLI (app-cli.py)   │
│   Tailwind CSS   │   argparse colors    │
└──────────────────┴──────────────────────┘
            ↓                ↓
┌─────────────────────────────────────────┐
│         Routes FastAPI / Handlers       │
│  list_route.py  |  control_route.py    │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│    Kamatera_cloud_management.py         │
│    (Client API Kamatera)                │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│         API Kamatera Cloud              │
│   https://console.kamatera.com/service  │
└─────────────────────────────────────────┘
```

## Prochaines étapes

1. **Explorez l'interface web** - Interface moderne et intuitive
2. **Testez le CLI** - Parfait pour l'automatisation
3. **Lisez la doc complète** - README.md et CLI_README.md
4. **Automatisez** - Créez des scripts avec le CLI

## Liens utiles

- [README principal](README.md) - Documentation complète
- [Documentation CLI](CLI_README.md) - Guide détaillé du CLI
- [API Kamatera](https://console.kamatera.com/docs/) - Documentation officielle

---

**Besoin d'aide?** Consultez les fichiers README ou utilisez `make help`
