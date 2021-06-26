import sys
sys.path.append("../../")

import pyds
import pydstream
import time
perf = pydstream.Perf()

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

class Probe(pydstream.BaseProbe):
    obj_counter = {
        PGIE_CLASS_ID_VEHICLE:0,
        PGIE_CLASS_ID_PERSON:0,
        PGIE_CLASS_ID_BICYCLE:0,
        PGIE_CLASS_ID_ROADSIGN:0
    }
    
    def __callback__(self, frame_meta):
        """
        print("Frame Number is ", frame_meta.frame_num)
        print("Source id is ", frame_meta.source_id)
        print("Batch id is ", frame_meta.batch_id)
        print("Source Frame Width ", frame_meta.source_frame_width)
        print("Source Frame Height ", frame_meta.source_frame_height)
        print("Num object meta ", frame_meta.num_obj_meta)
        """
        
        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta

        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration: break
            
            self.obj_counter[obj_meta.class_id] += 1
            
            try: 
                l_obj = l_obj.next
            except StopIteration: break
        
        vehicle_count, person_count = self.obj_counter[PGIE_CLASS_ID_VEHICLE], self.obj_counter[PGIE_CLASS_ID_PERSON]
        
        """
        display_meta = pyds.nvds_acquire_display_meta_from_pool(self.batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]
        py_nvosd_text_params.display_text = "Frame Number={} Number of Objects={} Vehicle_count={} Person_count={}".format(frame_number, num_rects, vehicle_count, person_count)
        py_nvosd_text_params.x_offset = 10;
        py_nvosd_text_params.y_offset = 12;
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        py_nvosd_text_params.font_params.font_color.red = 1.0
        py_nvosd_text_params.font_params.font_color.green = 1.0
        py_nvosd_text_params.font_params.font_color.blue = 1.0
        py_nvosd_text_params.font_params.font_color.alpha = 1.0
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.red = 0.0
        py_nvosd_text_params.text_bg_clr.green = 0.0
        py_nvosd_text_params.text_bg_clr.blue = 0.0
        py_nvosd_text_params.text_bg_clr.alpha = 1.0
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        """
        
        print(f"Frame Number={frame_number} Number of Objects={num_rects} Vehicle_count={vehicle_count} Person_count={person_count}")
        
        # Get frame rate through this probe
        perf.update(f"stream-{frame_meta.pad_index}")

tiler_src_pad_buffer_probe = Probe()