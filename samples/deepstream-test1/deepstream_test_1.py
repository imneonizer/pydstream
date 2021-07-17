import sys
sys.path.append("../../")

import pyds
import pydstream
from probe import osd_sink_pad_buffer_probe

# create elements
pipeline = pydstream.Pipeline()
pipeline.add('filesrc', 'source')
pipeline.add('h264parse', 'h264parser')
pipeline.add('nvv4l2decoder', 'decoder')
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('nveglglessink', 'sink')

if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')

# set elements properties
pipeline.set_property('source.location', '/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264')
pipeline.set_property('streammux.width', 1920)
pipeline.set_property('streammux.height', 1080)
pipeline.set_property('streammux.batch-size', 1)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.set_property('pgie.config-file-path', 'dstest1_pgie_config.txt')

# link elements
pipeline.link('source.h264parser.decoder')

sinkpad = pipeline.streammux.get_request_pad("sink_0")
srcpad = pipeline.decoder.get_static_pad("src")
srcpad.link(sinkpad)

pipeline.link('streammux.pgie.nvvidconv.nvosd')

if pydstream.is_aarch64():
    pipeline.link('nvosd.transform.sink')
else:
    pipeline.link('nvosd.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('nvosd.sink', callback=osd_sink_pad_buffer_probe)

# start the pipeline
pipeline.run()