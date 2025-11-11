#!/usr/bin/env python3
"""Interface en ligne de commande pour la gestion des serveurs Kamatera.

Ce module fournit une CLI complète pour interagir avec l'API Kamatera.
Il permet de gérer le cycle de vie complet des serveurs : création, démarrage,
arrêt, redémarrage et destruction.

L'authentification peut se faire de deux manières :
    1. Via une clé API directe (KAMATERA_API_KEY)
    2. Via OAuth avec client ID et secret (KAMATERA_CLIENT_ID + KAMATERA_SECRET)

Examples:
    Lister tous les serveurs::
    
        $ python app-cli.py list
    
    Afficher les détails d'un serveur::
    
        $ python app-cli.py details mon-serveur-01
    
    Démarrer un serveur avec confirmation automatique::
    
        $ python app-cli.py start mon-serveur-01 -y
    
    Détruire un serveur (nécessite double confirmation)::
    
        $ python app-cli.py destroy mon-serveur-01

Environment Variables:
    KAMATERA_API_KEY: Clé API Kamatera pour authentification directe
    KAMATERA_CLIENT_ID: Identifiant client pour authentification OAuth
    KAMATERA_SECRET: Secret pour authentification OAuth

Note:
    Les opérations destructives (stop, reboot, destroy) nécessitent une
    confirmation utilisateur sauf si l'option `-y/--yes` est fournie.

"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from kamatera.auth_kamatera import get_kamatera_token
from kamatera.Kamatera_cloud_management import KamateraCloudManagement
from logger import configure_logging, get_logger


# Configuration du logging global
configure_logging()
logger = get_logger(__name__)


# Constantes pour les messages répétitifs
MSG_OPERATION_CANCELLED: str = "Opération annulée"
MSG_SERVER_ID_HELP: str = "ID du serveur"
MSG_AUTO_CONFIRM_HELP: str = "Confirmer automatiquement"


def get_api_key() -> Optional[str]:
    """Récupère les credentials Kamatera depuis les variables d'environnement.
    
    Cette fonction tente d'obtenir une clé API de deux manières :
    1. Directement via la variable KAMATERA_API_KEY
    2. Via un flux OAuth en utilisant KAMATERA_CLIENT_ID et KAMATERA_SECRET
    
    Le token OAuth obtenu est automatiquement stocké dans l'environnement
    pour les appels ultérieurs.
    
    Returns:
        Optional[str]: La clé API si disponible, None en cas d'échec.
        
    Note:
        En cas d'échec de l'authentification OAuth, un message d'erreur
        est loggé mais l'exception n'est pas propagée.
    
    """
    # Tentative 1 : Utiliser la clé API directe
    api_key: Optional[str] = os.getenv("KAMATERA_API_KEY")
    if api_key:
        logger.debug("Using KAMATERA_API_KEY from environment")
        return api_key

    # Tentative 2 : Utiliser le flux OAuth
    client_id: Optional[str] = os.getenv("KAMATERA_CLIENT_ID")
    secret: Optional[str] = os.getenv("KAMATERA_SECRET")
    
    if client_id and secret:
        logger.info("Fetching token using KAMATERA_CLIENT_ID and KAMATERA_SECRET")
        try:
            auth_result: Dict[str, Any] = get_kamatera_token(client_id, secret)
            
            # Vérifier si une erreur est présente
            if auth_result.get("error"):
                logger.error(f"OAuth authentication error: {auth_result['error']}")
                return None
            
            # Extraire le token du dictionnaire de résultat
            token: Optional[str] = auth_result.get("token")
            if token:
                logger.debug("Successfully obtained OAuth token")
                # Stocker le token dans l'environnement pour les appels suivants
                os.environ["KAMATERA_API_KEY"] = token
                return token
            else:
                logger.error("No token found in OAuth response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get token via OAuth: {e}")
            return None

    logger.error("No Kamatera credentials found in environment")
    return None


def print_json(data: Any) -> None:
    """Affiche des données structurées en format JSON lisible.
    
    Args:
        data: Structure de données Python (dict, list, etc.) à sérialiser
              et afficher en JSON formaté.
              
    Note:
        Le JSON est formaté avec une indentation de 2 espaces et
        les caractères Unicode sont préservés (ensure_ascii=False).
    
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_error(message: str) -> None:
    """Affiche un message d'erreur formaté en rouge sur stderr.
    
    Args:
        message: Texte du message d'erreur à afficher.
        
    Note:
        Utilise les codes ANSI pour la couleur rouge (\\033[91m).
        Le message est préfixé par une icône ❌.
    
    """
    print(f"\033[91m❌ Erreur: {message}\033[0m", file=sys.stderr)


def print_success(message: str) -> None:
    """Affiche un message de succès formaté en vert.
    
    Args:
        message: Texte du message de succès à afficher.
        
    Note:
        Utilise les codes ANSI pour la couleur verte (\\033[92m).
        Le message est préfixé par une icône ✅.
    
    """
    print(f"\033[92m✅ {message}\033[0m")


def print_warning(message: str) -> None:
    """Affiche un message d'avertissement formaté en jaune.
    
    Args:
        message: Texte de l'avertissement à afficher.
        
    Note:
        Utilise les codes ANSI pour la couleur jaune (\\033[93m).
        Le message est préfixé par une icône ⚠️.
    
    """
    print(f"\033[93m⚠️  {message}\033[0m")


def print_info(message: str) -> None:
    """Affiche un message d'information formaté en bleu.
    
    Args:
        message: Texte informatif à afficher.
        
    Note:
        Utilise les codes ANSI pour la couleur bleue (\\033[94m).
        Le message est préfixé par une icône ℹ️.
    
    """
    print(f"\033[94mℹ️  {message}\033[0m")


def print_server_table(servers: List[Dict[str, Any]]) -> None:
    """Affiche une liste de serveurs sous forme de tableau formaté.
    
    Le tableau comprend trois colonnes : Nom, ID et Statut.
    Le statut est coloré selon l'état du serveur :
    - Vert pour running/started
    - Rouge pour stopped
    - Jaune pour les autres états
    
    Args:
        servers: Liste de dictionnaires représentant les serveurs.
                 Chaque dictionnaire doit contenir les clés 'name' ou 'label',
                 'id' et 'status'.
                 
    Note:
        Si la liste est vide, un avertissement est affiché au lieu du tableau.
        Les largeurs de colonnes s'ajustent automatiquement au contenu.
    
    """
    if not servers:
        print_warning("Aucun serveur trouvé")
        return

    # Calculer les largeurs de colonnes optimales
    max_name_len: int = max(len(s.get('name', s.get('label', ''))) for s in servers)
    max_id_len: int = max(len(s.get('id', '')) for s in servers)
    max_status_len: int = max(len(s.get('status', '')) for s in servers)
    
    name_width: int = max(max_name_len, 10)
    id_width: int = max(max_id_len, 15)
    status_width: int = max(max_status_len, 10)

    # Afficher l'en-tête du tableau
    separator: str = "=" * (name_width + id_width + status_width + 10)
    print("\n" + separator)
    print(f"{'Nom':<{name_width}} | {'ID':<{id_width}} | {'Statut':<{status_width}}")
    print(separator)

    # Afficher chaque serveur
    for server in servers:
        name: str = server.get('name', server.get('label', 'N/A'))
        server_id: str = server.get('id', 'N/A')
        status: str = server.get('status', 'unknown')
        
        # Colorer le statut selon l'état
        status_colored: str
        if status.lower() in ['running', 'started']:
            status_colored = f"\033[92m{status}\033[0m"
        elif status.lower() == 'stopped':
            status_colored = f"\033[91m{status}\033[0m"
        else:
            status_colored = f"\033[93m{status}\033[0m"
        
        print(f"{name:<{name_width}} | {server_id:<{id_width}} | {status_colored}")

    print(separator + "\n")


def print_server_details(server: Dict[str, Any]) -> None:
    """Affiche les détails complets d'un serveur de manière structurée.
    
    Les valeurs complexes (dictionnaires et listes) sont formatées
    en JSON pour une meilleure lisibilité.
    
    Args:
        server: Dictionnaire contenant toutes les propriétés du serveur.
                Chaque paire clé-valeur est affichée sur une ligne.
                
    Note:
        Les structures imbriquées (dict, list) sont affichées en JSON formaté
        avec une indentation de 2 espaces.
    
    """
    separator: str = "=" * 60
    print("\n" + separator)
    print("DÉTAILS DU SERVEUR")
    print(separator)
    
    for key, value in server.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")
    
    print(separator + "\n")


def confirm_action(message: str) -> bool:
    """Demande une confirmation interactive à l'utilisateur.
    
    Args:
        message: Question ou message à afficher pour demander confirmation.
        
    Returns:
        bool: True si l'utilisateur confirme (oui/o/yes/y), False sinon.
        
    Note:
        La réponse est insensible à la casse et aux espaces.
        Accepte 'oui', 'o', 'yes', 'y' comme réponses positives.
    
    """
    response: str = input(f"{message} (oui/non): ").lower().strip()
    return response in ['oui', 'o', 'yes', 'y']


def cmd_list(client: KamateraCloudManagement, args: argparse.Namespace) -> int:
    """Liste tous les serveurs disponibles dans le compte Kamatera.
    
    Récupère et affiche la liste des serveurs soit sous forme de tableau
    formaté (par défaut), soit en JSON (si --json est spécifié).
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés de la ligne de commande, incluant le flag --json.
        
    Returns:
        int: Code de retour - 0 si succès, 1 en cas d'erreur.
        
    Note:
        En mode tableau, le nombre total de serveurs est affiché à la fin.
    
    """
    try:
        result: Dict[str, Any] = client.list_servers()
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de la récupération des serveurs'))
            return 1
        
        # Extraire la liste des serveurs de la réponse
        servers: Any = result.get('data', [])
        if isinstance(servers, dict):
            servers = servers.get('servers', [])
        
        # Affichage selon le format demandé
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
    """Affiche les détails complets d'un serveur spécifique.
    
    Récupère toutes les informations disponibles pour un serveur donné
    et les affiche soit en format structuré, soit en JSON.
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés contenant server_id et le flag --json.
        
    Returns:
        int: Code de retour - 0 si succès, 1 en cas d'erreur.
        
    """
    try:
        result: Dict[str, Any] = client.get_server_details(args.server_id)
        
        if result.get('status') != 200:
            print_error(result.get('message', 'Erreur lors de la récupération des détails'))
            return 1
        
        server: Dict[str, Any] = result.get('data', {})
        
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
    """Démarre un serveur arrêté.
    
    Envoie une commande de démarrage au serveur spécifié.
    Demande confirmation sauf si --yes est fourni.
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés contenant server_id et le flag --yes.
        
    Returns:
        int: Code de retour - 0 si succès ou annulation, 1 en cas d'erreur.
        
    """
    try:
        # Demander confirmation si nécessaire
        if not args.yes:
            if not confirm_action(f"Démarrer le serveur '{args.server_id}'?"):
                print_warning(MSG_OPERATION_CANCELLED)
                return 0
        
        print_info(f"Démarrage du serveur {args.server_id}...")
        result: Dict[str, Any] = client.start_server(args.server_id)
        
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
    """Arrête un serveur en cours d'exécution.
    
    Envoie une commande d'arrêt au serveur spécifié.
    Demande confirmation sauf si --yes est fourni.
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés contenant server_id et le flag --yes.
        
    Returns:
        int: Code de retour - 0 si succès ou annulation, 1 en cas d'erreur.
        
    Warning:
        L'arrêt brutal d'un serveur peut causer des pertes de données.
        
    """
    try:
        # Demander confirmation si nécessaire
        if not args.yes:
            if not confirm_action(f"Arrêter le serveur '{args.server_id}'?"):
                print_warning(MSG_OPERATION_CANCELLED)
                return 0
        
        print_info(f"Arrêt du serveur {args.server_id}...")
        result: Dict[str, Any] = client.stop_server(args.server_id)
        
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
    """Redémarre un serveur (arrêt puis démarrage).
    
    Effectue un cycle complet de redémarrage du serveur.
    Demande confirmation sauf si --yes est fourni.
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés contenant server_id et le flag --yes.
        
    Returns:
        int: Code de retour - 0 si succès ou annulation, 1 en cas d'erreur.
        
    """
    try:
        # Demander confirmation si nécessaire
        if not args.yes:
            if not confirm_action(f"Redémarrer le serveur '{args.server_id}'?"):
                print_warning(MSG_OPERATION_CANCELLED)
                return 0
        
        print_info(f"Redémarrage du serveur {args.server_id}...")
        result: Dict[str, Any] = client.reboot_server(args.server_id)
        
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
    """Détruit définitivement un serveur.
    
    Cette opération est IRRÉVERSIBLE et supprime complètement le serveur
    ainsi que toutes ses données associées.
    
    Une double confirmation est requise sauf si --yes est fourni.
    
    Args:
        client: Instance configurée du client de gestion Kamatera.
        args: Arguments parsés contenant server_id et le flag --yes.
        
    Returns:
        int: Code de retour - 0 si succès ou annulation, 1 en cas d'erreur.
        
    Warning:
        Cette action est DÉFINITIVE. Toutes les données seront perdues.
        
    """
    try:
        # Double confirmation si mode interactif
        if not args.yes:
            print_warning("⚠️  ATTENTION: Cette action est IRRÉVERSIBLE!")
            if not confirm_action(f"Détruire le serveur '{args.server_id}'?"):
                print_warning(MSG_OPERATION_CANCELLED)
                return 0
            
            # Seconde confirmation pour les opérations destructives
            if not confirm_action("Confirmer la destruction?"):
                print_warning(MSG_OPERATION_CANCELLED)
                return 0
        
        print_info(f"Destruction du serveur {args.server_id}...")
        result: Dict[str, Any] = client.delete_server(args.server_id)
        
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
    """Point d'entrée principal de l'application CLI.
    
    Configure le parser d'arguments, valide les credentials, initialise
    le client Kamatera et route la commande vers le handler approprié.
    
    Returns:
        int: Code de retour du processus :
            - 0 : Succès
            - 1 : Erreur (credentials manquants, commande inconnue, erreur d'exécution)
            
    Note:
        Les variables d'environnement suivantes sont utilisées :
        - KAMATERA_API_KEY (prioritaire)
        - KAMATERA_CLIENT_ID + KAMATERA_SECRET (fallback OAuth)
        
    """
    # Configuration du parser principal
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
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

    # Commande: list
    parser_list = subparsers.add_parser('list', help='Liste tous les serveurs')
    parser_list.add_argument('--json', action='store_true', help='Sortie en format JSON')

    # Commande: details
    parser_details = subparsers.add_parser('details', help='Affiche les détails d\'un serveur')
    parser_details.add_argument('server_id', help=MSG_SERVER_ID_HELP)
    parser_details.add_argument('--json', action='store_true', help='Sortie en format JSON')

    # Commande: start
    parser_start = subparsers.add_parser('start', help='Démarre un serveur')
    parser_start.add_argument('server_id', help=MSG_SERVER_ID_HELP)
    parser_start.add_argument('-y', '--yes', action='store_true', help=MSG_AUTO_CONFIRM_HELP)

    # Commande: stop
    parser_stop = subparsers.add_parser('stop', help='Arrête un serveur')
    parser_stop.add_argument('server_id', help=MSG_SERVER_ID_HELP)
    parser_stop.add_argument('-y', '--yes', action='store_true', help=MSG_AUTO_CONFIRM_HELP)

    # Commande: reboot
    parser_reboot = subparsers.add_parser('reboot', help='Redémarre un serveur')
    parser_reboot.add_argument('server_id', help=MSG_SERVER_ID_HELP)
    parser_reboot.add_argument('-y', '--yes', action='store_true', help=MSG_AUTO_CONFIRM_HELP)

    # Commande: destroy
    parser_destroy = subparsers.add_parser('destroy', help='Détruit un serveur (irréversible)')
    parser_destroy.add_argument('server_id', help=MSG_SERVER_ID_HELP)
    parser_destroy.add_argument('-y', '--yes', action='store_true', 
                                help='Confirmer automatiquement (dangereux!)')

    args: argparse.Namespace = parser.parse_args()

    # Vérifier qu'une commande a été fournie
    if not args.command:
        parser.print_help()
        return 1

    # Récupérer les credentials
    api_key: Optional[str] = get_api_key()
    if not api_key:
        print_error("Aucune clé API trouvée. Définissez KAMATERA_API_KEY ou KAMATERA_CLIENT_ID + KAMATERA_SECRET")
        return 1

    # Créer le client Kamatera
    try:
        client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    except Exception as e:
        print_error(f"Impossible de créer le client Kamatera: {str(e)}")
        return 1

    # Router vers le handler de commande approprié
    commands: Dict[str, Any] = {
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
