import sys

class Pipeline:
    from gi.repository import GObject, Gst

    def __init__(self):
        self.GObject.threads_init()
        self.Gst.init(None)
        self.pipeline = self.Gst.Pipeline()
        
        if not self.pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")
    
    def make(self, element, name=None):
        if isinstance(element, str):
            element = self.Gst.ElementFactory.make(element, name)
        if not element:
            raise RuntimeError("Unable to create Element: {}".format(name))
        return element
    
    def add(self, element):
        if not element:
            raise RuntimeError("Unable to add Element")
        self.pipeline.add(element)
    
    def check(self, element):
        if not element:
            raise RuntimeError("Element check failed \n")
        return element
    
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

pipeline = Pipeline()