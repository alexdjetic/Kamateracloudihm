.PHONY: help install run-web run-cli list start stop test clean

help:
	@echo "Kamatera Cloud IHM - Commandes disponibles:"
	@echo ""
	@echo "  make install     - Installer les dépendances"
	@echo "  make run-web     - Lancer l'interface web"
	@echo "  make run-cli     - Afficher l'aide du CLI"
	@echo "  make list        - Lister les serveurs (CLI)"
	@echo "  make test        - Lancer les tests (TODO)"
	@echo "  make clean       - Nettoyer les fichiers temporaires"
	@echo ""
	@echo "Variables d'environnement requises:"
	@echo "  KAMATERA_API_KEY ou (KAMATERA_CLIENT_ID + KAMATERA_SECRET)"
	@echo ""
	@echo "Exemples:"
	@echo "  export KAMATERA_API_KEY='votre_clef'"
	@echo "  make run-web"
	@echo "  make list"

install:
	@echo "Installation des dépendances avec uv..."
	uv sync

run-web:
	@echo "Lancement de l'interface web sur http://localhost:8000"
	uv run app.py

run-cli:
	@echo "Aide du CLI Kamatera:"
	uv run app-cli.py --help

list:
	@echo "Liste des serveurs:"
	uv run app-cli.py list

start:
	@if [ -z "$(SERVER_ID)" ]; then \
		echo "Usage: make start SERVER_ID=<server_id>"; \
		exit 1; \
	fi
	uv run app-cli.py start $(SERVER_ID)

stop:
	@if [ -z "$(SERVER_ID)" ]; then \
		echo "Usage: make stop SERVER_ID=<server_id>"; \
		exit 1; \
	fi
	uv run app-cli.py stop $(SERVER_ID)

details:
	@if [ -z "$(SERVER_ID)" ]; then \
		echo "Usage: make details SERVER_ID=<server_id>"; \
		exit 1; \
	fi
	uv run app-cli.py details $(SERVER_ID)

test:
	@echo "Tests non implémentés pour le moment"
	@echo "TODO: pytest"

clean:
	@echo "Nettoyage des fichiers temporaires..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Nettoyage terminé"
