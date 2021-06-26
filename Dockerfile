# base image to start from
FROM nvcr.io/nvidia/deepstream-l4t:5.0.1-20.09-samples

# install python dependencies
RUN apt update -y
RUN apt install -y python3-dev python3-pip \
    python3-numpy python3-opencv \
    python3-gst-1.0 python3-gi

# install gstreamer python dependencies
RUN apt install -y libgirepository1.0-dev gstreamer1.0-rtsp \
    libgstrtspserver-1.0-0 gobject-introspection gir1.2-gst-rtsp-server-1.0 \
    libgstreamer-plugins-base1.0-dev

# install utility tools
RUN apt install -y vim git

# install deepstream python sample apps
ENV DS_PYTHON="/opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps"
RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git $DS_PYTHON
RUN bash -c "cd /opt/nvidia/deepstream/deepstream/lib && python3 setup.py install"

# install bindings to access nvanalytics metadata
RUN pip3 install pybind11
RUN git clone https://github.com/7633/pyds_analytics_meta.git /pyds_analytics_meta && \
    cd /pyds_analytics_meta && git checkout 1f0cccf && \
    bash build.sh

# setup default python and pip alias
RUN echo 'alias python="/usr/bin/python3"' >> /root/.bashrc && \
    echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc

WORKDIR /app
COPY . .

CMD bash