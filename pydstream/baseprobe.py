import pyds
from .common import Gst, Perf
import contextlib

class BaseProbe:
    def __init__(self):
        self.pad_probe_return = Gst.PadProbeReturn.OK
        
    def __call__(self, pad, info, u_data):
        """
        Act as decorator to verify GstBuffer,
        iterate on frame_meta, and handle Gst.PadProbeReturn
        """
        self.pad = pad
        self.info = info
        self.u_data = u_data
        assert self.info.get_buffer(), "Unable to get GstBuffer"
        assert hasattr(self, "__callback__"), "__callback__ is not defined"
        
        l_frame = self.batch_meta.frame_meta_list
        while l_frame is not None:
            try:
                # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
                # The casting is done by pyds.NvDsFrameMeta.cast()
                # The casting also keeps ownership of the underlying memory
                # in the C code, so the Python garbage collector will leave
                # it alone.
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration: break
            
            self.__callback__(frame_meta)

            try:
                l_frame = l_frame.next
            except StopIteration: break
            
        return self.pad_probe_return
    
    @property
    def batch_meta(self):
        """
        Retrieve batch metadata from the gst_buffer
        Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        """
        return pyds.gst_buffer_get_nvds_batch_meta(hash(self.info.get_buffer()))