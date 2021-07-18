#!/bin/bash

# Check if running with root
if  [ "$EUID" -ne 0 ];then
    echo "usage: sudo $0 [--build | --run | --attach | --kill]"
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
NAME="pydstream"

if [[ $1 == "--build" || $1 == "-b" ]];then
    # Build the container
    call "docker build . -t $NAME -f $DOCKER_FILE"

elif [[ $1 == "--run" || $1 == "-r" ]];then
    # Run a new container
    export DISPLAY=:1
    xhost +
    call "docker run --rm -it --gpus all \
    -v /home/$USER/videos:/videos \
    -v `pwd`:/app \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    --net host \
    --name pydstream \
    --hostname pydstream \
    pydstream bash"

elif [[ $1 == "--attach" || $1 == "-a" ]];then
    # Attach to already running container
    call "docker exec -it $NAME bash"

elif [[ $1 == "--kill" || $1 == "-k" ]];then
    # Kill any other existing container
    call "docker kill $NAME"

fi