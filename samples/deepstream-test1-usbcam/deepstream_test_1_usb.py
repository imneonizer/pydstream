import sys
sys.path.append("../../")

import pyds
import pydstream
import argparse
from probe import osd_sink_pad_buffer_probe

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--device", default="/dev/video0", help="Path to USB device")
ap.add_argument("-f", "--framerate", default="30", help="Camera Framerates")
args = ap.parse_args()

# create elements
pipeline = pydstream.Pipeline()
pipeline.add('v4l2src', 'source')
pipeline.add('capsfilter', 'v4l2src_caps')

# Adding videoconvert -> nvvideoconvert as not all
# raw formats are supported by nvvideoconvert;
# Say YUYV is unsupported - which is the common
# raw format for many logi usb cams
# In case we have a camera with raw format supported in
# nvvideoconvert, GStreamer plugins' capability negotiation
# shall be intelligent enough to reduce compute by
# videoconvert doing passthrough (TODO we need to confirm this)

# videoconvert to make sure a superset of raw formats are supported
pipeline.add('videoconvert', 'convertor_src1')

# nvvideoconvert to convert incoming raw buffers to NVMM Mem (NvBufSurface API)
pipeline.add('nvvideoconvert', 'convertor_src2')
pipeline.add('capsfilter', 'nvmm_caps')

# Create nvstreammux instance to form batches from one or more sources.
pipeline.add('nvstreammux', 'streammux')

# Use nvinfer to run inferencing on camera's output,
# behaviour of inferencing is set through config file
pipeline.add('nvinfer', 'pgie')

# Use convertor to convert from NV12 to RGBA as required by nvosd
pipeline.add('nvvideoconvert', 'nvvidconv')

# Create OSD to draw on the converted RGBA buffer
pipeline.add('nvdsosd', 'nvosd')

# Finally render the osd output
if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')
pipeline.add('nveglglessink', 'sink')

# set elements properties
pipeline.set_property('source.device', args.device)
pipeline.set_property('v4l2src_caps.caps', pipeline.Gst.Caps.from_string(f"video/x-raw, framerate={args.framerate}/1"))
pipeline.set_property('nvmm_caps.caps', pipeline.Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
pipeline.set_property('streammux.width', 1920)
pipeline.set_property('streammux.height', 1080)
pipeline.set_property('streammux.batch-size', 1)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.set_property('pgie.config-file-path', 'dstest1_pgie_config.txt')
pipeline.set_property('sink.sync', False)

# link elements
pipeline.link('source.v4l2src_caps.convertor_src1.convertor_src2.nvmm_caps')

srcpad = pipeline.nvmm_caps.get_static_pad("src")
sinkpad = pipeline.streammux.get_request_pad("sink_0")
pipeline.link(srcpad, sinkpad)

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