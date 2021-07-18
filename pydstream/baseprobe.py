import pyds
from .common import Gst, Perf
import contextlib

class BaseProbe:
    def __init__(self):
        self.perf = Perf()
    
    def __call__(self, pad, info, u_data):
        """
        Act as decorator to verify GstBuffer,
        iterate on frame_meta, and handle Gst.PadProbeReturn
        """
        self.pad = pad
        self.info = info
        self.u_data = u_data
        l_frame = self.batch_meta.frame_meta_list
        
        with self.suppress:
            while l_frame is not None:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
                
                # user defined callback for processing metadata
                cb_return = self.__callback__(frame_meta)
                
                # get next frame
                l_frame = l_frame.next
        
        return cb_return or Gst.PadProbeReturn.OK
    
    @property
    def batch_meta(self):
        """
        Retrieve batch metadata from the gst_buffer
        Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        """
        return pyds.gst_buffer_get_nvds_batch_meta(hash(self.info.get_buffer()))
    
    @property
    def suppress(self):
        return contextlib.suppress(StopIteration)