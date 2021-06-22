import platform
import sys
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