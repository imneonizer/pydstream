import sys
sys.path.append("../../")

import pyds
import pydstream

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
past_tracking_meta = [0]

class Probe(pydstream.BaseProbe):

    def __callback__(self):
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

        # Acquiring a display meta object. The memory ownership remains in
        # the C code so downstream plugins can still access it. Otherwise
        # the garbage collector will claim it when this probe function exits.
        display_meta = pyds.nvds_acquire_display_meta_from_pool(self.batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]
        
        # Setting display text to be shown on screen
        # Note that the pyds module allocates a buffer for the string, and the
        # memory will not be claimed by the garbage collector.
        # Reading the display_text field here will return the C address of the
        # allocated string. Use pyds.get_string() to get the string content.
        py_nvosd_text_params.display_text = "Frame Number = {} Number of Objects = {} Vehicle_count = {} Person_count = {}".format(frame_number, num_rects, obj_counter[PGIE_CLASS_ID_VEHICLE], obj_counter[PGIE_CLASS_ID_PERSON])

        # Now set the offsets where the string should appear
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12

        # Font , font-color and font-size
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        
        # set(red, green, blue, alpha); set to White
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

        # Text background color
        py_nvosd_text_params.set_bg_clr = 1
        
        # set(red, green, blue, alpha); set to Black
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
        
        # Using pyds.get_string() to get display_text as string
        print(pyds.get_string(py_nvosd_text_params.display_text))
        pyds.nvds_add_display_meta_to_frame(self.frame_meta, display_meta)
        
        #past traking meta data
        if (past_tracking_meta[0] == 1):
            for user_meta in self.user_meta_list:
                if (user_meta and user_meta.base_meta.meta_type == pyds.NvDsMetaType.NVDS_TRACKER_PAST_FRAME_META):
                    # Note that user_meta.user_meta_data needs a cast to pyds.NvDsPastFrameObjBatch
                    # The casting is done by pyds.NvDsPastFrameObjBatch.cast()
                    # The casting also keeps ownership of the underlying memory
                    # in the C code, so the Python garbage collector will leave
                    # it alone
                    pPastFrameObjBatch = pyds.NvDsPastFrameObjBatch.cast(user_meta.user_meta_data)
                    
                    for trackobj in pyds.NvDsPastFrameObjBatch.list(pPastFrameObjBatch):
                        print("streamId=",trackobj.streamID)
                        print("surfaceStreamID=",trackobj.surfaceStreamID)
                        for pastframeobj in pyds.NvDsPastFrameObjStream.list(trackobj):
                            print("numobj=",pastframeobj.numObj)
                            print("uniqueId=",pastframeobj.uniqueId)
                            print("classId=",pastframeobj.classId)
                            print("objLabel=",pastframeobj.objLabel)
                            for objlist in pyds.NvDsPastFrameObjList.list(pastframeobj):
                                print('frameNum:', objlist.frameNum)
                                print('tBbox.left:', objlist.tBbox.left)
                                print('tBbox.width:', objlist.tBbox.width)
                                print('tBbox.top:', objlist.tBbox.top)
                                print('tBbox.right:', objlist.tBbox.height)
                                print('confidence:', objlist.confidence)
                                print('age:', objlist.age)

osd_sink_pad_buffer_probe = Probe()