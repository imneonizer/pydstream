import sys
sys.path.append("../../")

import os
import cv2
import numpy as np
import pydstream
import pyds

class Probe(pydstream.BaseProbe):

    def __callback__(self):
        got_visual = False
        frame_number = self.frame_meta.frame_num

        for user_meta in self.user_meta_list:
            # Casting of_user_meta.user_meta_data to pyds.NvDsOpticalFlowMeta
            of_meta = pyds.NvDsOpticalFlowMeta.cast(user_meta.user_meta_data)
            # Get Flow vectors
            flow_vectors = pyds.get_optical_flow_vectors(of_meta)
            # Reshape the obtained flow vectors into proper shape
            flow_vectors = flow_vectors.reshape(of_meta.rows, of_meta.cols, 2)
            # map the flow vectors in HSV color space for visualization
            flow_visual = self.visualize_optical_flowvectors(flow_vectors)
            got_visual = True

        print(f"Frame Number={frame_number}")
        if got_visual:
            path = f"{self.pipeline.folder_name}/stream_{self.frame_meta.pad_index}/frame_{frame_number}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            cv2.imwrite(path, flow_visual)

    def visualize_optical_flowvectors(self, flow):
        """
        Converts the flow u, v vectors into visualization by mapping them into
        grey color space
        :param flow: flow vectors
        :return: bgr image
        """
        shape_visual = (flow.shape[0], flow.shape[1], 3)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv = np.full(shape_visual, 255, dtype=np.uint8)
        hsv[..., 1] = 255
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr = 255 - bgr
        return bgr

ofvisual_queue_src_pad_buffer_probe = Probe()