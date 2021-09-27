import sys
sys.path.append("../../")

import pyds
import pydstream
import argparse
from probe import osd_sink_pad_buffer_probe

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GObject, Gst, GstRtspServer

ap = argparse.ArgumentParser()
ap.add_argument("--display", "-d", type=int, default=0)
ap.add_argument("--updsink_port", type=int, default=5400)
ap.add_argument("--rtsp_port", type=int, default=8554)
ap.add_argument("-c", "--codec", default="H264",
        help="RTSP Streaming Codec H264/H265 , default=H264", 
        choices=['H264','H265'])
args = ap.parse_args()

codec_mapping = {
    "H264":{"rtp": "rtph264pay", "enc": "nvv4l2h264enc"},
    "H265":{"rtp": "rtph265pay", "enc": "nvv4l2h265enc"}
    }

# create elements
pipeline = pydstream.Pipeline()
pipeline.add('filesrc', 'source')
pipeline.add('h264parse', 'h264parser')
pipeline.add('nvv4l2decoder', 'decoder')
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvvideoconvert', 'nvvidconv_postosd')
pipeline.add('nvdsosd', 'nvosd')
pipeline.add('capsfilter', 'caps')
pipeline.add(codec_mapping[args.codec]['enc'], 'encoder')
pipeline.add(codec_mapping[args.codec]['rtp'], 'rtppay')
pipeline.add('tee', 'tee')
pipeline.add('queue', 'queue1')
pipeline.add('queue', 'queue2')
pipeline.add('udpsink', 'udpsink')
if args.display:
    pipeline.add('nveglglessink', 'sink')

if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')
    pipeline.set_property('encoder.preset-level', 1)
    pipeline.set_property('encoder.insert-sps-pps', 1)
    pipeline.set_property('encoder.bufapi-version', 1)

# set elements properties
pipeline.set_property('source.location', '/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264')
pipeline.set_property('streammux.width', 1920)
pipeline.set_property('streammux.height', 1080)
pipeline.set_property('streammux.batch-size', 1)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.set_property('pgie.config-file-path', 'dstest1_pgie_config.txt')

pipeline.set_property('udpsink.host', '224.224.255.255')
pipeline.set_property('udpsink.port', args.updsink_port)
pipeline.set_property('udpsink.async', False)
pipeline.set_property('udpsink.sync', 1)

# link elements
pipeline.link('source.h264parser.decoder')

srcpad = pipeline.decoder.get_static_pad("src")
sinkpad = pipeline.streammux.get_request_pad("sink_0")
pipeline.link(srcpad, sinkpad)

pipeline.link('streammux.pgie.nvvidconv.nvosd.tee')

tee_render_pad = pipeline.tee.get_request_pad('src_%u')
sink_pad = pipeline.queue1.get_static_pad("sink")
pipeline.link(tee_render_pad, sink_pad)

tee_render_pad = pipeline.tee.get_request_pad("src_%u")
sink_pad = pipeline.queue2.get_static_pad("sink")
pipeline.link(tee_render_pad, sink_pad)

pipeline.link('queue1.nvvidconv_postosd.caps.encoder.rtppay.udpsink')

if args.display:
    if pydstream.is_aarch64():
        pipeline.link('queue2.transform.sink')
    else:
        pipeline.link('queue2.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('nvosd.sink', callback=osd_sink_pad_buffer_probe)

# Start streaming
server = GstRtspServer.RTSPServer.new()
server.props.service = "%d" % args.rtsp_port
server.attach(None)
factory = GstRtspServer.RTSPMediaFactory.new()
factory.set_launch( "( udpsrc name=pay0 port=%d buffer-size=524288 caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 \" )" % (args.updsink_port, args.codec))
factory.set_shared(True)
server.get_mount_points().add_factory("/ds-test", factory)
print("\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n" % args.rtsp_port)

# start the pipeline
pipeline.run()