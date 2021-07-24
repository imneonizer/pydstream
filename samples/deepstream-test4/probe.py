import sys
sys.path.append("../../")

import pyds
import pydstream
from utils import generate_event_msg_meta

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

pgie_classes_str=["Vehicle", "TwoWheeler", "Person","Roadsign"]

class Probe(pydstream.BaseProbe):
    """"
    This probe will extract metadata received on OSD sink pad
    and update params for drawing rectangle, object information etc.
    IMPORTANT NOTE:
    a) probe() callbacks are synchronous and thus holds the buffer
        (info.get_buffer()) from traversing the pipeline until user return.
    b) loops inside probe() callback could be costly in python.
        So users shall optimize according to their use-case.
    """

    def __callback__(self):
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE:0,
            PGIE_CLASS_ID_PERSON:0,
            PGIE_CLASS_ID_BICYCLE:0,
            PGIE_CLASS_ID_ROADSIGN:0
        }
        
        frame_number = self.frame_meta.frame_num
        message_interval = 30
        
        for obj_meta in self.obj_meta_list:
            '''
            print("Frame Number is ", self.frame_meta.frame_num)
            print("Source id is ", self.frame_meta.source_id)
            print("Batch id is ", self.frame_meta.batch_id)
            print("Source Frame Width ", self.frame_meta.source_frame_width)
            print("Source Frame Height ", self.frame_meta.source_frame_height)
            print("Num object meta ", self.frame_meta.num_obj_meta)
            '''

            # Update the object text display
            txt_params = obj_meta.text_params

            # Set display_text. Any existing display_text string will be
            # freed by the bindings module.
            txt_params.display_text = pgie_classes_str[obj_meta.class_id]
            obj_counter[obj_meta.class_id] += 1

            # Font , font-color and font-size
            txt_params.font_params.font_name = "Serif"
            txt_params.font_params.font_size = 10
            # set(red, green, blue, alpha); set to White
            txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0);

            # Text background color
            txt_params.set_bg_clr = 1
            
            # set(red, green, blue, alpha); set to Black
            txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0);

            # Ideally NVDS_EVENT_MSG_META should be attached to buffer by the
            # component implementing detection / recognition logic.
            # Here it demonstrates how to use / attach that meta data.
            if frame_number%message_interval == 0:
                # Allocating an NvDsEventMsgMeta instance and getting reference
                # to it. The underlying memory is not manged by Python so that
                # downstream plugins can access it. Otherwise the garbage collector
                # will free it when this probe exits.
                msg_meta = pyds.alloc_nvds_event_msg_meta()
                msg_meta.bbox.top =  obj_meta.rect_params.top
                msg_meta.bbox.left =  obj_meta.rect_params.left
                msg_meta.bbox.width = obj_meta.rect_params.width
                msg_meta.bbox.height = obj_meta.rect_params.height
                msg_meta.frameId = frame_number
                msg_meta.trackingId = pydstream.long_to_int(obj_meta.object_id)
                msg_meta.confidence = obj_meta.confidence
                msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)
                user_event_meta = pyds.nvds_acquire_user_meta_from_pool(self.batch_meta)
                
                if user_event_meta:
                    user_event_meta.user_meta_data = msg_meta;
                    user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                    # Setting callbacks in the event msg meta. The bindings layer
                    # will wrap these callables in C functions. Currently only one
                    # set of callbacks is supported.
                    # pyds.user_copyfunc(user_event_meta, meta_copy_func) # not supported in DS 5.0
                    # pyds.user_releasefunc(user_event_meta, meta_free_func) # not supported in DS 5.0
                    pyds.nvds_add_user_meta_to_frame(self.frame_meta, user_event_meta)
                else:
                    print("Error in attaching event meta to buffer\n")

        print("Frame Number =",frame_number,"Vehicle Count =",obj_counter[PGIE_CLASS_ID_VEHICLE],"Person Count =",obj_counter[PGIE_CLASS_ID_PERSON])

osd_sink_pad_buffer_probe = Probe()