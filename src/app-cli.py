#!/usr/bin/env python3
"""CLI pour gérer les serveurs Kamatera.

Ce script permet d'interagir avec l'API Kamatera en ligne de commande
pour lister, démarrer, arrêter, redémarrer et détruire des serveurs.

Exemples d'utilisation:
    # Lister tous les serveurs
    python app-cli.py list

    # Afficher les détails d'un serveur
    python app-cli.py details <server_id>

    # Démarrer un serveur
    python app-cli.py start <server_id>

    # Arrêter un serveur
    python app-cli.py stop <server_id>

    # Redémarrer un serveur
    python app-cli.py reboot <server_id>

    # Détruire un serveur (avec confirmation)
    python app-cli.py destroy <server_id>

Variables d'environnement requises:
    KAMATERA_API_KEY: Clé API Kamatera
    OU
    KAMATERA_CLIENT_ID et KAMATERA_SECRET: Pour l'authentification OAuth
"""

import argparse
import os
import sys
from typing import Any, Dict, Optional
import json

from kamatera.Kamatera_cloud_management import KamateraCloudManagement
from kamatera.auth_kamatera import get_kamatera_token
from logger import configure_logging, get_logger


# Configure logging
configure_logging()
logger = get_logger(__name__)


def get_api_key() -> Optional[str]:
    """Récupère la clé API depuis l'environnement ou via OAuth.

    Returns:
        str: La clé API si disponible, None sinon.
    """
    # Try direct API key first
    api_key = os.getenv("KAMATERA_API_KEY")
    if api_key:
        logger.debug("Using KAMATERA_API_KEY from environment")
        return api_key

    # Try OAuth flow
    client_id = os.getenv("KAMATERA_CLIENT_ID")
    secret = os.getenv("KAMATERA_SECRET")
    
    if client_id and secret:
        logger.info("Fetching token using KAMATERA_CLIENT_ID and KAMATERA_SECRET")
        try:
            token = get_kamatera_token(client_id, secret)
            if token:
                # Store it in environment for subsequent calls
                os.environ["KAMATERA_API_KEY"] = token
                return token
        except Exception as e:
            logger.error(f"Failed to get token via OAuth: {e}")
            return None

    logger.error("No Kamatera credentials found in environment")
    return None


def print_json(data: Any) -> None:
    """Affiche les données en JSON formaté.

    Args:
        data: Données à afficher
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_error(message: str) -> None:
    """Affiche un message d'erreur en rouge.

    Args:
        message: Message d'erreur à afficher
    """
    print(f"\033[91m❌ Erreur: {message}\033[0m", file=sys.stderr)


def print_success(message: str) -> None:
    """Affiche un message de succès en vert.

    Args:
        message: Message de succès à afficher
    """
    print(f"\033[92m✅ {message}\033[0m")


def print_warning(message: str) -> None:
    """Affiche un message d'avertissement en jaune.

    Args:
        message: Message d'avertissement à afficher
    """
    print(f"\033[93m⚠️  {message}\033[0m")


def print_info(message: str) -> None:
    """Affiche un message d'information en bleu.

    Args:
        message: Message d'information à afficher
    """
    print(f"\033[94mℹ️  {message}\033[0m")


def print_server_table(servers: list) -> None:
    """Affiche la liste des serveurs sous forme de tableau.

    Args:
        servers: Liste des serveurs à afficher
    """
    if not servers:
        print_warning("Aucun serveur trouvé")
        return

    # Calculate column widths
    max_name_len = max(len(s.get('name', s.get('label', ''))) for s in servers)
    max_id_len = max(len(s.get('id', '')) for s in servers)
    max_status_len = max(len(s.get('status', '')) for s in servers)
    
    name_width = max(max_name_len, 10)
    id_width = max(max_id_len, 15)
    status_width = max(max_status_len, 10)

    # Print header
    print("\n" + "=" * (name_width + id_width + status_width + 10))
    print(f"{'Nom':<{name_width}} | {'ID':<{id_width}} | {'Statut':<{status_width}}")
    print("=" * (name_width + id_width + status_width + 10))

    # Print servers
    for server in servers:
        name = server.get('name', server.get('label', 'N/A'))
        server_id = server.get('id', 'N/A')
        status = server.get('status', 'unknown')
        
        # Color code status
        if status.lower() in ['running', 'started']:
            status_colored = f"\033[92m{status}\033[0m"
        elif status.lower() == 'stopped':
            status_colored = f"\033[91m{status}\033[0m"
        else:
            status_colored = f"\033[93m{status}\033[0m"
        
        print(f"{name:<{name_width}} | {server_id:<{id_width}} | {status_colored}")

    print("=" * (name_width + id_width + status_width + 10) + "\n")


def print_server_details(server: Dict[str, Any]) -> None:
    """Affiche les détails d'un serveur.

    Args:
        server: Dictionnaire contenant les détails du serveur
    """
    print("\n" + "=" * 60)
    print("DÉTAILS DU SERVEUR")
    print("=" * 60)
    
    for key, value in server.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")
    
    print("=" * 60 + "\n")


def confirm_action(message: str) -> bool:
    """Demande confirmation à l'utilisateur.

    Args:
        message: Message de confirmation

    Returns:
        bool: True si l'utilisateur confirme, False sinon
    """
    response = input(f"{message} (oui/non): ").lower().strip()
    return response in ['oui', 'o', 'yes', 'y']


def cmd_list(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Liste tous les serveurs.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        result = client.list_servers()
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de la récupération des serveurs'))
            return 1
        
        servers = result.get('data', [])
        if isinstance(servers, dict):
            servers = servers.get('servers', [])
        
        if args.json:
            print_json(servers)
        else:
            print_server_table(servers)
            print_info(f"Total: {len(servers)} serveur(s)")
        
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error listing servers")
        return 1


def cmd_details(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Affiche les détails d'un serveur.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        result = client.get_server_details(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de la récupération des détails'))
            return 1
        
        server = result.get('data', {})
        
        if args.json:
            print_json(server)
        else:
            print_server_details(server)
        
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error getting server details")
        return 1


def cmd_start(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Démarre un serveur.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        if not args.yes:
            if not confirm_action(f"Démarrer le serveur '{args.server_id}'?"):
                print_warning("Opération annulée")
                return 0
        
        print_info(f"Démarrage du serveur {args.server_id}...")
        result = client.start_server(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors du démarrage'))
            return 1
        
        print_success(f"Serveur {args.server_id} démarré avec succès")
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error starting server")
        return 1


def cmd_stop(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Arrête un serveur.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        if not args.yes:
            if not confirm_action(f"Arrêter le serveur '{args.server_id}'?"):
                print_warning("Opération annulée")
                return 0
        
        print_info(f"Arrêt du serveur {args.server_id}...")
        result = client.stop_server(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de l\'arrêt'))
            return 1
        
        print_success(f"Serveur {args.server_id} arrêté avec succès")
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error stopping server")
        return 1


def cmd_reboot(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Redémarre un serveur.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        if not args.yes:
            if not confirm_action(f"Redémarrer le serveur '{args.server_id}'?"):
                print_warning("Opération annulée")
                return 0
        
        print_info(f"Redémarrage du serveur {args.server_id}...")
        result = client.reboot_server(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors du redémarrage'))
            return 1
        
        print_success(f"Serveur {args.server_id} redémarré avec succès")
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error rebooting server")
        return 1


def cmd_destroy(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Détruit un serveur.

    Args:
        client: Instance du client Kamatera
        args: Arguments de la ligne de commande

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    try:
        if not args.yes:
            print_warning("⚠️  ATTENTION: Cette action est IRRÉVERSIBLE!")
            if not confirm_action(f"Détruire le serveur '{args.server_id}'?"):
                print_warning("Opération annulée")
                return 0
            
            # Double confirmation
            if not confirm_action("Confirmer la destruction?"):
                print_warning("Opération annulée")
                return 0
        
        print_info(f"Destruction du serveur {args.server_id}...")
        result = client.delete_server(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de la destruction'))
            return 1
        
        print_success(f"Serveur {args.server_id} détruit avec succès")
        return 0
    
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        logger.exception("Error destroying server")
        return 1


def main() -> int:
    """Point d'entrée principal du CLI.

    Returns:
        int: Code de retour (0 = succès, non-zero = erreur)
    """
    parser = argparse.ArgumentParser(
        description="CLI pour gérer les serveurs Kamatera",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s list                          # Liste tous les serveurs
  %(prog)s list --json                   # Liste en format JSON
  %(prog)s details <server_id>           # Détails d'un serveur
  %(prog)s start <server_id>             # Démarre un serveur
  %(prog)s stop <server_id>              # Arrête un serveur
  %(prog)s reboot <server_id>            # Redémarre un serveur
  %(prog)s destroy <server_id>           # Détruit un serveur
  %(prog)s start <server_id> -y          # Démarre sans confirmation

Variables d'environnement:
  KAMATERA_API_KEY                       # Clé API directe
  OU
  KAMATERA_CLIENT_ID + KAMATERA_SECRET   # Pour OAuth
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Command: list
    parser_list = subparsers.add_parser('list', help='Liste tous les serveurs')
    parser_list.add_argument('--json', action='store_true', help='Sortie en format JSON')

    # Command: details
    parser_details = subparsers.add_parser('details', help='Affiche les détails d\'un serveur')
    parser_details.add_argument('server_id', help='ID du serveur')
    parser_details.add_argument('--json', action='store_true', help='Sortie en format JSON')

    # Command: start
    parser_start = subparsers.add_parser('start', help='Démarre un serveur')
    parser_start.add_argument('server_id', help='ID du serveur')
    parser_start.add_argument('-y', '--yes', action='store_true', help='Confirmer automatiquement')

    # Command: stop
    parser_stop = subparsers.add_parser('stop', help='Arrête un serveur')
    parser_stop.add_argument('server_id', help='ID du serveur')
    parser_stop.add_argument('-y', '--yes', action='store_true', help='Confirmer automatiquement')

    # Command: reboot
    parser_reboot = subparsers.add_parser('reboot', help='Redémarre un serveur')
    parser_reboot.add_argument('server_id', help='ID du serveur')
    parser_reboot.add_argument('-y', '--yes', action='store_true', help='Confirmer automatiquement')

    # Command: destroy
    parser_destroy = subparsers.add_parser('destroy', help='Détruit un serveur (irréversible)')
    parser_destroy.add_argument('server_id', help='ID du serveur')
    parser_destroy.add_argument('-y', '--yes', action='store_true', help='Confirmer automatiquement (dangereux!)')

    args = parser.parse_args()

    # Check if command is provided
    if not args.command:
        parser.print_help()
        return 1

    # Get API key
    api_key = get_api_key()
    if not api_key:
        print_error("Aucune clé API trouvée. Définissez KAMATERA_API_KEY ou KAMATERA_CLIENT_ID + KAMATERA_SECRET")
        return 1

    # Create client
    try:
        client = KamateraCloudManagement(api_key=api_key)
    except Exception as e:
        print_error(f"Impossible de créer le client Kamatera: {str(e)}")
        return 1

    # Route to appropriate command handler
    commands = {
        'list': cmd_list,
        'details': cmd_details,
        'start': cmd_start,
        'stop': cmd_stop,
        'reboot': cmd_reboot,
        'destroy': cmd_destroy,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(client, args)
    else:
        print_error(f"Commande inconnue: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
