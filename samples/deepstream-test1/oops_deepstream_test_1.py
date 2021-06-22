import sys
sys.path.append("../../")

import pyds
import pydstream
from pydstream import Gst
from pydstream.pipeline import pipeline
from probe import osd_sink_pad_buffer_probe

# create elements
source = pipeline.make('filesrc', 'file-source')
h264parser = pipeline.make('h264parse', 'h264-parser')
decoder = pipeline.make('nvv4l2decoder', 'nvv4l2-decoder')
streammux = pipeline.make('nvstreammux', 'stream-muxer')
pgie = pipeline.make('nvinfer', 'primary-inference')
nvvidconv = pipeline.make('nvvideoconvert', 'convertor')
nvosd = pipeline.make('nvdsosd', 'onscreendisplay')
transform = pipeline.make('nvegltransform', 'nvegl-transform')
sink = pipeline.make('nveglglessink', 'nvvideo-renderer')

# set element properties
source.set_property('location', '/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264')
streammux.set_property('width', 1920)
streammux.set_property('height', 1080)
streammux.set_property('batch-size', 1)
streammux.set_property('batched-push-timeout', 4000000)
pgie.set_property('config-file-path', './dstest1_pgie_config.txt')

# add elements to pipeline
pipeline.add(source)
pipeline.add(h264parser)
pipeline.add(decoder)
pipeline.add(streammux)
pipeline.add(pgie)
pipeline.add(nvvidconv)
pipeline.add(nvosd)
pipeline.add(sink)
pipeline.add(transform)

# link elements
source.link(h264parser)
h264parser.link(decoder)

sinkpad = pipeline.check(streammux.get_request_pad("sink_0"))
srcpad = pipeline.check(decoder.get_static_pad("src"))
srcpad.link(sinkpad)

streammux.link(pgie)
pgie.link(nvvidconv)
nvvidconv.link(nvosd)

if pydstream.is_aarch64():
    nvosd.link(transform)
    transform.link(sink)
else:
    nvosd.link(sink)

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
osdsinkpad = pipeline.check(nvosd.get_static_pad("sink"))
osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

# start the pipeline
pipeline.run()