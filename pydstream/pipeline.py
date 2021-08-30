import sys
import math
from .multistream import MultiStream
from .common import read_config, gi

class Pipeline(MultiStream):
    from gi.repository import GObject, Gst
    unsupported_config = ["tracker"]

    def __init__(self):
        self.GObject.threads_init()
        self.Gst.init(None)
        self.pipeline = self.Gst.Pipeline()
        self.islive = False
        self.enable_perf = False
        self.label = {} # to store gie class ids
        assert self.pipeline, "Unable to create Pipeline"
    
    def make(self, element, name=None):
        element = self.Gst.ElementFactory.make(element, name or element)
        assert element, "Unable to create Element: {}".format(name)
        return element
    
    def add(self, element, name):
        if element == 'multiuri' and isinstance(name, (list, tuple)):
            self.add_uri(name)
            return

        if isinstance(element, str):
            element = self.make(element, name)
        assert element, "Unable to add Element"
        assert name not in self.__dict__, f"Element with name: {name} already created"
        
        self.pipeline.add(element)
        self.__dict__[name] = element
        return element

    def check(self, element):
        assert element, "Element check failed \n"
        return element
    
    def link(self, element_a, element_b=None, delimiter="."):
        if (element_b is None) and (delimiter in str(element_a)):
            print("Linking:", element_a.replace(delimiter, " -> "))
            elements = element_a.split(delimiter)
            l = len(elements)
            for i in range(l - 1):
                self.link(elements[i], elements[i+1])
        else:
            if isinstance(element_a, gi.overrides.Gst.Pad) and isinstance(element_a, gi.overrides.Gst.Pad):
                print(f"Linking: {element_a.parent.name} -> {element_b.parent.name}")
            
            if isinstance(element_a, str):
                element_a = self.__getitem__(element_a)
            if isinstance(element_b, str):
                element_b = self.__getitem__(element_b)
            
            element_a.link(element_b)
    
    def add_probe(self, element, callback, pad=None, ptype=None, n=0, delimiter='.'):
        if delimiter in element:
            element, pad = element.split(delimiter)

        callback.pipeline = self
        ptype = ptype or self.Gst.PadProbeType.BUFFER
        pad = self.__getitem__(element).get_static_pad(pad)
        pad.add_probe(ptype, callback, n)
    
    def set_property(self, element, val=None, key=None, delimiter='.'):
        if delimiter in element:
            element, key = element.split(delimiter)

        if key == "config-file-path" and element in self.unsupported_config:
            # explicitly set properties
            tracker_config = read_config(val).get(element)
            for k,v in tracker_config.items():
                self.set_property(element=element, key=k, val=v)
            return

        if key == 'cells' and isinstance(val, int):
            rows = int(math.sqrt(val))
            columns = int(math.ceil((1.0*val)/rows))
            element = self.__getitem__(element)
            element.set_property('rows', rows)
            element.set_property('columns', columns)
            return
        
        if key == "label-file-path":
            with open(val, "r") as f:
                self.label[element] = [x for x in f.read().split("\n") if x]
            return

        element = self.__getitem__(element)
        element.set_property(key, val)

    def override_property(self, element, value):
        orig_val = self.get_property(element)
        if orig_val != value:
            print("WARNING: Overriding {} {} with {}".format(element, orig_val, value))
            self.set_property(element, value)
    
    def get_property(self, element, key=None, delimiter="."):
        if delimiter in element:
            element, key = element.split(delimiter)
        return self.__getitem__(element).get_property(key)

    def bus_call(self, bus, message, loop):
        t = message.type
        
        if t == self.Gst.MessageType.EOS:
            sys.stdout.write("End-of-stream\n")
            loop.quit()

        elif t == self.Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            sys.stderr.write("Warning: %s: %s\n" % (err, debug))

        elif t == self.Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            sys.stderr.write("Error: %s: %s\n" % (err, debug))
            loop.quit()

        return True
    
    def run(self):
        # create an event loop and feed gstreamer bus mesages to it
        loop = self.GObject.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.bus_call, loop)
        
        # start play back and listen to events
        print("Starting pipeline")
        self.pipeline.set_state(self.Gst.State.PLAYING)

        try:
            loop.run()
        except KeyboardInterrupt:
            self.pipeline.set_state(self.Gst.State.NULL)
            loop.quit()

        self.pipeline.set_state(self.Gst.State.NULL)
    
    def __getitem__(self, key):
        return self.__dict__[key]