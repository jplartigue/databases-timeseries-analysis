#!/bin/bash
# On récupère de le chemin absolu du bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SCRIPT_DIR+='/'

# Récupération du docker-compose.build.yml et de la config d'environnement
docker_compose_build="$SCRIPT_DIR/docker-compose.build.yml"

docker-compose -f $docker_compose_build build


