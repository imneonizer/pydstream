# python deepstream_test_4.py --conn-str="192.168.1.20;9092" --no-display

import sys
sys.path.append("../../")

import pyds
import pydstream
import argparse
from probe import osd_sink_pad_buffer_probe

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cfg-file", dest="cfg_file",
                help="Set the adaptor config file. Optional if connection string has relevant  details.", metavar="FILE")
ap.add_argument("-i", "--input-file", dest="input_file", default='/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264',
                help="Set the input H264 file", metavar="FILE")
ap.add_argument("-p", "--proto-lib", dest="proto_lib", default='/opt/nvidia/deepstream/deepstream/lib/libnvds_kafka_proto.so',
                help="Absolute path of adaptor library", metavar="PATH")
ap.add_argument("-cs", "--conn-str", dest="conn_str",
                help="Connection string of backend server. Optional if it is part of config file.", metavar="STR")
ap.add_argument("-s", "--schema-type", dest="schema_type", default=0,
                help="Type of message schema (0=Full, 1=minimal), default=0", metavar="<0|1>")
ap.add_argument("-t", "--topic", dest="topic", default="test",
                help="Name of message topic. Optional if it is part of connection string or config file.", metavar="TOPIC")
ap.add_argument("-nd", "--no-display", action="store_true", dest="no_display", default=False,
                help="Disable display")
args = ap.parse_args()

# create elements
pipeline = pydstream.Pipeline()
pipeline.add('filesrc', 'source')
pipeline.add('h264parse', 'h264parser')
pipeline.add('nvv4l2decoder', 'decoder')
pipeline.add('nvstreammux', 'streammux')
pipeline.add('nvinfer', 'pgie')
pipeline.add('nvvideoconvert', 'nvvidconv')
pipeline.add('nvdsosd', 'nvosd')

pipeline.add('nvmsgconv', 'nvmsgconv')
pipeline.add('nvmsgbroker', 'nvmsgbroker')
pipeline.add('tee', 'tee')
pipeline.add('queue', 'queue1')
pipeline.add('queue', 'queue2')

if args.no_display:
    pipeline.add('fakesink', 'sink')
else:
    pipeline.add('nveglglessink', 'sink')

if pydstream.is_aarch64():
    pipeline.add('nvegltransform', 'transform')

# set elements properties
pipeline.set_property('source.location', args.input_file)
pipeline.set_property('streammux.width', 1920)
pipeline.set_property('streammux.height', 1080)
pipeline.set_property('streammux.batch-size', 1)
pipeline.set_property('streammux.batched-push-timeout', 4000000)
pipeline.override_property('streammux.live-source', 1)

pipeline.set_property('pgie.config-file-path', 'dstest4_pgie_config.txt')
pipeline.set_property('nvmsgconv.config', 'dstest4_msgconv_config.txt')
pipeline.set_property('nvmsgconv.payload-type', args.schema_type)
pipeline.set_property('nvmsgbroker.proto-lib', args.proto_lib)
pipeline.set_property('nvmsgbroker.conn-str', args.conn_str)
pipeline.set_property('nvmsgbroker.sync', False)

if args.cfg_file is not None:
    pipeline.set_property('nvmsgbroker.config', args.cfg_file)

if args.topic is not None:
    pipeline.set_property('nvmsgbroker.topic', args.topic)
    
# link elements
pipeline.link('source.h264parser.decoder')

srcpad = pipeline.decoder.get_static_pad("src")
sinkpad = pipeline.streammux.get_request_pad("sink_0")
pipeline.link(srcpad, sinkpad)

pipeline.link('streammux.pgie.nvvidconv.nvosd.tee')

tee_msg_pad = pipeline.tee.get_request_pad('src_%u')
sink_pad = pipeline.queue1.get_static_pad("sink")
pipeline.link(tee_msg_pad, sink_pad)

tee_render_pad = pipeline.tee.get_request_pad("src_%u")
sink_pad = pipeline.queue2.get_static_pad("sink")
pipeline.link(tee_render_pad, sink_pad)

pipeline.link('queue1.nvmsgconv.nvmsgbroker')

if pydstream.is_aarch64():
    pipeline.link('queue2.transform.sink')
else:
    pipeline.link('queue2.sink')

# Lets add probe to get informed of the meta data generated, we add probe to
# the sink pad of the osd element, since by that time, the buffer would have
# had got all the metadata.
pipeline.add_probe('nvosd.sink', callback=osd_sink_pad_buffer_probe)

# start the pipeline
pipeline.run()