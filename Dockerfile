# base image to start from
ARG BASE_IMAGE=nvcr.io/nvidia/deepstream:5.1-21.02-samples
FROM $BASE_IMAGE

# install python and gstreamer-python dependencies
RUN apt update -y && \
    apt install -y python3-dev python3-pip \
    python3-numpy python3-opencv \
    python3-gst-1.0 python3-gi \
    libgirepository1.0-dev gstreamer1.0-rtsp \
    libgstrtspserver-1.0-0 gobject-introspection gir1.2-gst-rtsp-server-1.0 \
    libgstreamer-plugins-base1.0-dev gstreamer1.0-python3-plugin-loader \
    vim git

# install deepstream python sample apps
ENV DS_PYTHON="/opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps"
RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git $DS_PYTHON
RUN bash -c "cd /opt/nvidia/deepstream/deepstream/lib && python3 setup.py install"

# install bindings to access metadata
RUN pip3 install pybind11

# install kafka dependencies
RUN apt update -y && apt install -y \
    libglib2.0 libglib2.0-dev libjansson4  libjansson-dev librdkafka1=0.11.3-1build1

# setup default python and pip alias
RUN echo 'alias python="/usr/bin/python3"' >> /root/.bashrc && \
    echo 'alias pip="/usr/bin/pip3"' >> /root/.bashrc

WORKDIR /app
COPY . .

CMD bash