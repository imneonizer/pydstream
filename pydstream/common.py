import platform
import sys
import time
import configparser

def is_aarch64():
    return platform.uname()[4] == 'aarch64'

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

class GETFPS:
    def __init__(self,stream_id):
        self.start_time = time.time()
        self.is_first = True
        self.frame_count = 0
        self.stream_id = stream_id

    def get_fps(self):
        end_time = time.time()
        if(self.is_first):
            self.start_time = end_time
            self.is_first = False

        if(end_time-self.start_time>5):
            print("\n**********************FPS*****************************************")
            print("Fps of stream", self.stream_id, "is ", float(self.frame_count)/5.0)
            print()
            self.frame_count = 0
            self.start_time = end_time
        else:
            self.frame_count=self.frame_count+1

    def print_data(self):
        print('frame_count=',self.frame_count)
        print('start_time=',self.start_time)