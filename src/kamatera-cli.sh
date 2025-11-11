#!/bin/bash
# Wrapper script pour faciliter l'utilisation du CLI Kamatera
# Usage: ./kamatera-cli.sh <command> [args...]

cd "$(dirname "$0")"
uv run app-cli.py "$@"
