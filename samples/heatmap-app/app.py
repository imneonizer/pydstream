from os import pipe
import sys
sys.path.append("../../")

import pyds
import pydstream
import argparse
from utils.probe import tiler_sink_pad_buffer_probe
from utils.stream_server import StreamServer

ap = argparse.ArgumentParser()
ap.add_argument("--display", "-d", type=int, default=0)
args = ap.parse_args()

uri = [
    'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.mp4',
    # 'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.mp4'
]

WIDTH, HEIGHT = (1920, 1080)
number_sources = len(uri)
pipeline = pydstream.Pipeline()

# heatmap
pipeline.hmap = {}
pipeline.streamer = StreamServer(zmq_port=5544)
pipeline.enable_perf = True

# create elements
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add("nvmultistreamtiler", "tiler")
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('multiuri', uri)
pipeline.add(('nveglglessink' if args.display else 'fakesink'), 'sink')

pipeline.add('nvvideoconvert', 'nvvidconv1')
pipeline.add("capsfilter", "filter1")
pipeline.set_property("filter1.caps", pipeline.Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA"))

if not pydstream.is_aarch64():
    # Use CUDA unified memory in the pipeline so frames
    # can be easily accessed on CPU in Python.
    mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
    pipeline.set_property("streammux.nvbuf-memory-type", mem_type)
    pipeline.set_property("nvvidconv.nvbuf-memory-type", mem_type)
    pipeline.set_property("nvvidconv1.nvbuf-memory-type", mem_type)
    pipeline.set_property("tiler.nvbuf-memory-type", mem_type)

# set elements properties
pipeline.set_property('streammux.width', WIDTH)
pipeline.set_property('streammux.height', HEIGHT)
pipeline.set_property('streammux.batch-size', number_sources)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.set_property('streammux.live-source', pipeline.islive)
pipeline.set_property("tiler.width", WIDTH)
pipeline.set_property("tiler.height", HEIGHT)
pipeline.set_property("tiler.cells", number_sources)
pipeline.set_property("sink.qos", 0)
pipeline.set_property('pgie.config-file-path', 'configs/pgie.cfg')
pipeline.set_property('pgie.label-file-path', 'configs/labels.txt')
pipeline.set_property('nvosd.process-mode', 0)
pipeline.set_property('nvosd.display-text', 0)

# adjust batch size based on input sources
pipeline.override_property("pgie.batch-size", number_sources)

# link elements
pipeline.link('streammux.pgie.nvvidconv1.filter1.tiler.nvvidconv.nvosd')

if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')
    pipeline.link('nvosd.transform.sink')
else:
    pipeline.link('nvosd.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('tiler.sink', callback=tiler_sink_pad_buffer_probe)

import sys
import subprocess as sp
sp.Popen(f"{sys.executable} utils/stream_client.py", shell=True)

# start the pipeline
pipeline.run()