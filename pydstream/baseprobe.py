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

        self.batch_meta = self.get_batch_meta()
        if not self.batch_meta:
            return Gst.PadProbeReturn.OK
        
        for l_frame in self.iterate(self.batch_meta.frame_meta_list):
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            self.frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            
            # get fps through this probe
            self.pipeline.enable_perf and self.perf.update(self.frame_meta.pad_index)
            
            # user defined callback for processing metadata
            cb_return = self.__callback__()
        
        return cb_return or Gst.PadProbeReturn.OK
    
    def get_batch_meta(self):
        """
        Retrieve batch metadata from the gst_buffer
        Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
        C address of gst_buffer as input, which is obtained with hash(gst_buffer)
        """
        return pyds.gst_buffer_get_nvds_batch_meta(hash(self.info.get_buffer()))
    
    def get_bbox_info(self, obj_meta):
        rect_params = obj_meta.rect_params
        x1,y1,x2,y2 = int(rect_params.left), \
            int(rect_params.top), \
            int(rect_params.left) + int(rect_params.width), \
            int(rect_params.top) + int(rect_params.height)
        return (obj_meta.class_id, x1,y1,x2,y2, round(abs(obj_meta.confidence), 3))
    
    @property
    def obj_meta_list(self):
        return self.cast(self.iterate(self.frame_meta.obj_meta_list), pyds.NvDsObjectMeta.cast)
    
    @property
    def user_meta_list(self):
        return self.cast(self.iterate(self.batch_meta.batch_user_meta_list), pyds.NvDsUserMeta.cast)
    
    def cast(self, meta, cast):
        for i in meta:
            yield cast(i.data)
    
    @property
    def suppress(self):
        return contextlib.suppress(StopIteration)
    
    def iterate(self, obj):
        with self.suppress:
            while obj is not None:
                yield obj
                obj = obj.next