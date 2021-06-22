export DISPLAY=:1
xhost +
sudo docker run --rm -it --gpus all \
    -v /home/$USER/videos:/videos \
    -v `pwd`:/app \
    -e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix --net host \
    --name pydstream --hostname pydstream \
    pydstream bash