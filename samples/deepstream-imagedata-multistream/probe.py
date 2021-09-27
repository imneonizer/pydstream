import sys
sys.path.append("../../")

import pyds
import pydstream
import numpy as np
from collections import defaultdict
import cv2
import os

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
saved_count = defaultdict(int)
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person","RoadSign"]

class Probe(pydstream.BaseProbe):
    
    def __callback__(self):
        frame_number = self.frame_meta.frame_num
        num_rects = self.frame_meta.num_obj_meta
        is_first_obj = True
        save_image = False
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE:0,
            PGIE_CLASS_ID_PERSON:0,
            PGIE_CLASS_ID_BICYCLE:0,
            PGIE_CLASS_ID_ROADSIGN:0
        }
        
        frame_number = self.frame_meta.frame_num
        num_rects = self.frame_meta.num_obj_meta

        for obj_meta in self.obj_meta_list:
            obj_counter[obj_meta.class_id] += 1
            
            if((saved_count[f"stream_{self.frame_meta.pad_index}"]%30==0) and (obj_meta.confidence>0.3 and obj_meta.confidence<0.31)):
                if is_first_obj:
                    is_first_obj = False
                    # Getting Image data using nvbufsurface
                    # the input should be address of buffer and batch_id
                    n_frame = pyds.get_nvds_buf_surface(hash(self.info.get_buffer()), self.frame_meta.batch_id)
                    #convert python array into numy array format.
                    frame_image = np.array(n_frame, copy=True,order='C')
                    #covert the array into cv2 default color format
                    frame_image = cv2.cvtColor(frame_image,cv2.COLOR_RGBA2BGR)

                save_image = True
                frame_image = self.draw_bounding_boxes(frame_image,obj_meta,obj_meta.confidence)
        
        vehicle_count, person_count = obj_counter[PGIE_CLASS_ID_VEHICLE], obj_counter[PGIE_CLASS_ID_PERSON]
        # print(f"Frame Number = {frame_number} Number of Objects = {num_rects} Vehicle_count = {vehicle_count} Person_count = {person_count}")
        
        if save_image:
            path = f"{self.pipeline.folder_name}/stream_{self.frame_meta.pad_index}/frame_{frame_number}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            cv2.imwrite(self.pipeline.folder_name+"/stream_"+str(self.frame_meta.pad_index)+"/frame_"+str(frame_number)+".jpg", frame_image)
        saved_count["stream_"+str(self.frame_meta.pad_index)] += 1        
    
    def draw_bounding_boxes(self, image, obj_meta, confidence):
        confidence = '{0:.2f}'.format(confidence)
        rect_params = obj_meta.rect_params
        top = int(rect_params.top)
        left = int(rect_params.left)
        width = int(rect_params.width)
        height = int(rect_params.height)
        obj_name = self.pipeline.label['pgie'][obj_meta.class_id]
        image = cv2.rectangle(image,(left,top),(left+width,top+height),(0,0,255,0),2)
        image = cv2.putText(image,obj_name+',C='+str(confidence),(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255,0),2)
        return image

tiler_sink_pad_buffer_probe = Probe()