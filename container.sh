#!/bin/bash

if  [ "$EUID" -ne 0 ];then
    echo "usage: sudo $0 [--build | --run | --attach | --kill]"
    exit 1
fi

NAME="pydstream"

function call {
    echo ">> $1";$1
}

if [[ $1 == "--build" || $1 == "-b" ]];then
    call "docker build . -t $NAME"

elif [[ $1 == "--run" || $1 == "-r" ]];then
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
    call "docker exec -it $NAME bash"

elif [[ $1 == "--kill" || $1 == "-k" ]];then
    call "docker kill $NAME"

fi