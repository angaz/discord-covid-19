#!/bin/bash

function print_help {
    echo "Invalid argument"
    echo "Usage: $0 [pull|build|re[create]|run|log[s]]..."
    echo
    echo "    pull            Does a git pull"
    echo "    docker-pull     Does a docker pull"
    echo "    build           Does a docker build"
    echo "    push            Does a docker push"
    echo "    re[create]      Removes the current running docker and runs a new docker"
    echo "    run             Runs a new docker"
    echo "    log[s]          Follows the server logs"
    exit 1
}

CONTAINER_NAME="api_covid19"
IMAGE_NAME="angusd/api_covid19"

PULL=false
DOCKER_PULL=false
BUILD=false
PUSH=false
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
        docker-pull)
            DOCKER_PULL=true
            ;;
        build)
            BUILD=true
            ;;
        push)
            PUSH=true
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

if $DOCKER_PULL; then
    docker pull $IMAGE_NAME

    if [ $? -ne 0 ]; then
        echo "Docker pull failed. Exiting."
        exit 1
    fi
fi

if $BUILD; then
    docker build -f api.Dockerfile -t $IMAGE_NAME .

    if [ $? -ne 0 ]; then
        echo "Docker build failed. Exiting."
        exit 1
    fi
fi

if $PUSH; then
    docker push $IMAGE_NAME

    if [ $? -ne 0 ]; then
        echo "Docker push failed. Exiting."
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
    docker run                  \
        --detach                \
        --name $CONTAINER_NAME  \
        --publish 8080:8080     \
        $IMAGE_NAME

    if [ $? -ne 0 ]; then
        echo "docker run failed. Exiting"
        exit 1
    fi
fi

if $LOGS; then
    docker logs -f $CONTAINER_NAME
fi
