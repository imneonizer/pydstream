import platform
import sys

def is_aarch64():
    return platform.uname()[4] == 'aarch64'