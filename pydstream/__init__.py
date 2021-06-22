import sys
import platform
sys.path.append('/opt/nvidia/deepstream/deepstream/lib')

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from .pipeline import Pipeline, pipeline
from .common import is_aarch64, read_config

