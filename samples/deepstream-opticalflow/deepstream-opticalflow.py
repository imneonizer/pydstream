# This code is not tested because
# Optical Flow SDK is not supported on GeForce GTX 1650.
# https://forums.developer.nvidia.com/t/optical-flow-sdk-with-non-turing-gpu/71714/7

import sys
sys.path.append("../../")

import pyds
import pydstream
from probe import ofvisual_queue_src_pad_buffer_probe

uri = [
    'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.mp4',
    'file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.mp4'
]

WIDTH, HEIGHT = (1920, 1080)
number_sources = len(uri)
pipeline = pydstream.Pipeline()
pipeline.enable_perf = True
pipeline.folder_name = "output"

# create elements
pipeline.add('nvstreammux', 'streammux')
pipeline.add('multiuri', uri)
pipeline.add("nvmultistreamtiler", "tiler")
pipeline.add("nvof", "nvof")
pipeline.add("nvofvisual", "nvofvisual")
pipeline.add("queue", "of_queue")
pipeline.add("queue", "ofvisual_queue")
pipeline.add("queue", "queue")
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add("capsfilter", "capsfilter")
pipeline.add('avenc_mpeg4', 'encoder')
pipeline.add('mpeg4videoparse', 'codeparser')
pipeline.add('qtmux', 'container')
pipeline.add('filesink', 'sink')

# set elements properties
pipeline.set_property("capsfilter.caps", pipeline.Gst.Caps.from_string("video/x-raw, format=I420"))
pipeline.set_property('sink.location', "./out.mp4")
pipeline.set_property('sink.sync', 0)
pipeline.set_property('streammux.width', WIDTH)
pipeline.set_property('streammux.height', HEIGHT)
pipeline.set_property('streammux.batch-size', number_sources)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.set_property('streammux.live-source', pipeline.islive)
pipeline.set_property("tiler.width", WIDTH)
pipeline.set_property("tiler.height", HEIGHT)
pipeline.set_property("tiler.cells", number_sources)
pipeline.set_property("sink.qos", 0)

# link elements
pipeline.link('streammux.nvof.of_queue.nvofvisual.ofvisual_queue.tiler.nvosd.queue.nvvidconv.capsfilter.encoder.codeparser.container.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('ofvisual_queue.src', callback=ofvisual_queue_src_pad_buffer_probe)

# start the pipeline
pipeline.run()