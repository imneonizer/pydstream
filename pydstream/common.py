import sys
import platform
sys.path.append('/opt/nvidia/deepstream/deepstream/lib')

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

import platform
import sys
import time
import configparser
import ctypes

def is_aarch64():
    return platform.uname()[4] == 'aarch64'

def long_to_int(l):
    value = ctypes.c_int(l & 0xffffffff).value
    return value

def read_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)

    def _eval(s):
        try:
            return eval(s)
        except:
            return s

    config_args = {}
    for element in parser.sections():
        config_args[element] = {}
        for name, value in parser.items(element):
            config_args[element][name] = _eval(value)

    return config_args

class Fps:
    """class to store fps of a stream"""
    def __init__(self, name, interval=5):
        self.name = name
        self.frame_count = 0
        self.interval = interval
        self.st = time.time()
        self.fps = 0

    def update(self):
        et = time.time()
        if et - self.st > self.interval:
            self.st = et
            self.fps = round(self.frame_count / self.interval, 2)
            self.frame_count = 0
        else:
            self.frame_count += 1

class Perf:
    def __init__(self, interval=5):
        self.streams = {}
        self.interval = interval
        self.st = time.time()
        self.isfirst = True

    def update(self, name, stdout=True):
        try:
            self.streams[name].update()
            if stdout and (time.time() - self.st > self.interval):
                self.st = time.time()
                
                if self.isfirst:
                    self.isfirst = False; return
                
                print("\n**********************FPS*****************************************")
                for (name, stream) in sorted(self.streams.items(), key=lambda x:x[0]):
                    print(f"FPS of stream {stream.name} is {stream.fps}")
        except:
            self.streams[name] = Fps(name)
            return self.update(name)

perf = Perf()