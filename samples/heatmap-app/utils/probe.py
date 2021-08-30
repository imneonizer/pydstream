import sys
sys.path.append("../../")

import pyds
import pydstream
from utils.heatmap import HeatMap
import numpy as np
import cv2

class Probe(pydstream.BaseProbe):
    
    def __callback__(self):
        idx = self.frame_meta.pad_index
        if idx not in self.pipeline.hmap:
            self.pipeline.hmap[idx] = self.pipeline.hmap.get(idx, HeatMap(
                self.pipeline.get_property('streammux.width'),
                self.pipeline.get_property('streammux.height')
            ))
        
        hmap, bbox = self.pipeline.hmap[idx], []
        for obj_meta in self.obj_meta_list:
            class_id, x1,y1,x2,y2, conf = self.get_bbox_info(obj_meta)
            if class_id == 0:
                bbox.append((x1,y1,x2,y2))
        hmap.update(bbox)
        
        frame = pyds.get_nvds_buf_surface(hash(self.info.get_buffer()), self.frame_meta.batch_id)
        frame = np.array(frame, copy=False, order='C')
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        self.pipeline.streamer.send(hmap.get_heatmap(frame), idx=idx)

tiler_sink_pad_buffer_probe = Probe()