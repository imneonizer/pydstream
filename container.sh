#!/bin/bash

# Check if running with root
if  [ "$EUID" -ne 0 ];then
    sudo -E $0 $@;
    exit 1
fi

# select correct dockerfile based on platform
if [ -f "/etc/nv_tegra_release" ];then
    DOCKER_FILE="dockerfile/Dockerfile.l4t"
else
    DOCKER_FILE="dockerfile/Dockerfile.x86"
fi

# function to echo and execute commands
function call {
    echo ">> $1";$1
}

# default container name
NAME="face-recognition-deepstream"

if [[ $1 == "--build" || $1 == "-b" ]];then
    # Build the container
    call "docker build . -t $NAME -f $DOCKER_FILE"
    exit

elif [[ $1 == "--run" || $1 == "-r" ]];then
    # Run a new container
    xhost +
    call "docker run --rm -it --gpus all \
    -v $HOME/Videos:/videos \
    -v `pwd`:/app \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    --net host \
    --name $NAME \
    --hostname $NAME \
    $NAME ${2:-bash}"
    exit

elif [[ $1 == "--attach" || $1 == "-a" ]];then
    # Attach to already running container
    call "docker exec -it $NAME ${2:-bash}"
    exit

elif [[ $1 == "--kill" || $1 == "-k" ]];then
    # Kill any other existing container
    call "docker kill $NAME"
    exit

fi

echo "usage: sudo $0 [--build | --run | --attach | --kill]"