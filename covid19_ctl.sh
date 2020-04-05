#!/bin/bash

function print_help {
    echo "Invalid argument $1"
    echo "Usage: $0 [pull|build|re[create]|run|log[s]]..."
    echo
    echo "    pull            Does a git pull"
    echo "    build           Same as 'build-server' and 'build-client' flags"
    echo "    re[create]      Removes the current running docker and runs a new docker"
    echo "    run             Runs a new docker"
    echo "    log[s]          Follows the server logs"
    exit 1
}

CONTAINER_NAME="covid19"
IMAGE_NAME="angusd/covid19"

PULL=false
BUILD=false
RECREATE=false
RUN=false
LOGS=false

if [[ $# -eq 0 ]]; then
    print_help
fi

for flag in $@; do
    case $flag in
        pull)
            PULL=true
            ;;
        build)
            BUILD=true
            ;;
        re|recreate)
            RECREATE=true
            ;;
        run)
            RUN=true
            ;;
        log|logs)
            LOGS=true
            ;;
        *)
            print_help $flag
            ;;
    esac
done


if $PULL; then
    git pull

    if [ $? -ne 0 ]; then
        echo "Git pull failed. Exiting."
        exit 1
    fi
fi

if $BUILD; then
    docker build -t $IMAGE_NAME server

    if [ $? -ne 0 ]; then
        echo "Docker build failed. Exiting."
        exit 1
    fi
fi

if $RECREATE; then
    docker rm -f $CONTAINER_NAME

    if [ $? -ne 0 ]; then
        echo "docker rm failed. Exiting."
        exit 1
    fi
fi

if $RECREATE || $RUN; then
    docker run -d --name $CONTAINER_NAME -p 8080:8080 $IMAGE_NAME

    if [ $? -ne 0 ]; then
        echo "docker run failed. Exiting"
        exit 1
    fi
fi

if $LOGS; then
    docker logs -f $CONTAINER_NAME
fi
