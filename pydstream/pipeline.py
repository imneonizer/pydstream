import sys
import pydstream

class Pipeline:
    from gi.repository import GObject, Gst
    unsupported_config = ["tracker"]

    def __init__(self):
        self.GObject.threads_init()
        self.Gst.init(None)
        self.pipeline = self.Gst.Pipeline()
        
        assert self.pipeline, "Unable to create Pipeline"
    
    def make(self, element, name=None):
        element = self.Gst.ElementFactory.make(element, name or element)
        assert element, "Unable to create Element: {}".format(name)
        return element
    
    def add(self, element, name=None):
        if isinstance(element, str):
            element = self.make(element, name)
        assert element, "Unable to add Element"
        self.pipeline.add(element)
        self.__dict__[name] = element
        return element
    
    def check(self, element):
        assert element, "Element check failed \n"
        return element
    
    def link(self, element_a, element_b):
        element_a = self.__getitem__(element_a)
        element_b = self.__getitem__(element_b)
        element_a.link(element_b)
    
    def add_probe(self, element, callback, pad=None, ptype=None, n=0, separator='.'):
        if separator in element:
            element, pad = element.split(separator)

        ptype = ptype or self.Gst.PadProbeType.BUFFER
        pad = self.__getitem__(element).get_static_pad(pad)
        pad.add_probe(ptype, callback, n)
    
    def set_property(self, element, val=None, key=None, separator='.'):
        if separator in element:
            element, key = element.split(separator)

        if key == "config-file-path" and element in self.unsupported_config:
            # explicitly set properties
            tracker_config = pydstream.read_config(val).get(element)
            for k,v in tracker_config.items():
                self.set_property(element=element, key=k, val=v)
            return

        element = self.__getitem__(element)
        element.set_property(key, val)

    def bus_call(self, bus, message, loop):
        t = message.type
        
        if t == self.Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            self.loop.quit()

        elif t == self.Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            sys.stderr.write("Warning: %s: %s\n" % (err, debug))

        elif t == self.Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            sys.stderr.write("Error: %s: %s\n" % (err, debug))
            self.loop.quit()

        return True
    
    def run(self):
        # create an event loop and feed gstreamer bus mesages to it
        self.loop = self.GObject.MainLoop()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect ("message", self.bus_call, self.loop)
        
        # start play back and listen to events
        print("Starting pipeline")
        self.pipeline.set_state(self.Gst.State.PLAYING)

        try:
            self.loop.run()
        except:
            pass

        self.pipeline.set_state(self.Gst.State.NULL)
    
    def __getitem__(self, key):
        return self.__dict__[key]

pipeline = Pipeline()