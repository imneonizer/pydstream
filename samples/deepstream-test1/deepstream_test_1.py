import sys
sys.path.append("../../")

import pyds
import pydstream
from pydstream.pipeline import pipeline
from probe import osd_sink_pad_buffer_probe

# create elements
pipeline.add('filesrc', 'source')
pipeline.add('h264parse', 'h264parser')
pipeline.add('nvv4l2decoder', 'decoder')
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('nvegltransform', 'transform')
pipeline.add('nveglglessink', 'sink')

# set elements properties
pipeline.source.set_property('location', '/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264')
pipeline.streammux.set_property('width', 1920)
pipeline.streammux.set_property('height', 1080)
pipeline.streammux.set_property('batch-size', 1)
pipeline.streammux.set_property('batched-push-timeout', 4000000)
pipeline.pgie.set_property('config-file-path', './dstest1_pgie_config.txt')

# link elements
pipeline.link('source', 'h264parser')
pipeline.link('h264parser', 'decoder')

sinkpad = pipeline.streammux.get_request_pad("sink_0")
srcpad = pipeline.decoder.get_static_pad("src")
srcpad.link(sinkpad)

pipeline.link('streammux', 'pgie')
pipeline.link('pgie', 'nvvidconv')
pipeline.link('nvvidconv', 'nvosd')

if pydstream.is_aarch64():
    pipeline.link('nvosd', 'transform')
    pipeline.link('transform', 'sink')
else:
    pipeline.link('nvosd', 'sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
osdsinkpad = pipeline.nvosd.get_static_pad("sink")
osdsinkpad.add_probe(pipeline.Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

# start the pipeline
pipeline.run()