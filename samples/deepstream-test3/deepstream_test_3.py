import sys
sys.path.append("../../")

import pyds
import pydstream
from probe import tiler_src_pad_buffer_probe

WIDTH, HEIGHT = (1920, 1080)

uri = [
    'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264',
    'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264'
]

number_sources = len(uri)
pipeline = pydstream.Pipeline()

# create elements
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add("nvmultistreamtiler", "tiler")
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('nveglglessink', 'sink')
pipeline.add('multiuri', uri)
[pipeline.add('queue', f'queue{i}') for i in range(5)]

if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')

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
pipeline.set_property('pgie.config-file-path', 'dstest3_pgie_config.txt')
pipeline.set_property('nvosd.process-mode', 0)
pipeline.set_property('nvosd.display-text', 0)

# adjust batch size based on input sources
pipeline.override_property("pgie.batch-size", number_sources)
pipeline.override_property('streammux.live-source', 1)

# link elements
pipeline.link('streammux.queue0.pgie.queue1.tiler.queue2.nvvidconv.queue3.nvosd')

if pydstream.is_aarch64():
    pipeline.link('nvosd.queue4.transform.sink')
else:
    pipeline.link('nvosd.queue4.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('pgie.src', callback=tiler_src_pad_buffer_probe)

# start the pipeline
pipeline.run()