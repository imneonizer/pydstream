import cv2
import numpy as np
import time

class HeatMap:
    def __init__(self, width, height, name=None, fade_interval=2, blur=75, anneal_blur=35, anneal_brightness=-2, radius=20,  pxstep=150, heatmap_point_color=5, heatmap_merge_thresh=0.3):
        self.width, self.height, name = width, height, name
        # to store raw heatmap data
        self.accum_image = np.zeros((self.height, self.width), np.uint8)
        # to store color mapping of heatmap data
        self.heatmap = np.zeros((self.height, self.width, 3), np.uint8)
        # interval at which headmap will fade
        self.fade_interval = fade_interval
        # amount of blur on registering heatmap point
        self.blur = blur
        # amount of blur for fading heatmap
        self.anneal_blur = anneal_blur
        # amount of brightness for fading heatmap
        self.anneal_brightness = anneal_brightness
        # radius of one heatmap point
        self.radius = radius
        # to store last regstered heatmap point time
        self.register_st = time.time()
        # amount of color to use for plotting one point on heatmap
        self.heatmap_point_color = heatmap_point_color
        # color intensity when adding original frame and heatmap
        self.heatmap_merge_thresh = heatmap_merge_thresh

    def anneal_heatmap(self):
        self.accum_image = self.adjust_brightness_contrast(self.accum_image, brightness=self.anneal_brightness)
        self.accum_image = cv2.blur(self.accum_image, (self.anneal_blur, self.anneal_blur))
    
    def adjust_brightness_contrast(self, image, brightness=0., contrast=0.):
        return cv2.addWeighted(image, 1 + float(contrast) / 100., image, 0, float(brightness))
        
    def get_mask_from_bbox(self, bbox):
        mask = np.zeros((self.height, self.width), np.uint8)
        for (x1, y1, x2, y2) in bbox:
            color = (self.heatmap_point_color, self.heatmap_point_color, self.heatmap_point_color)
            cx, cy, r = x1, y2, self.radius
            mask = cv2.circle(mask, (cx+(r*2), cy), r, color, -1)
        
        return mask
    
    def update(self, bbox):
        if time.time() - self.register_st > self.fade_interval:
            self.register_st = time.time()
            self.anneal_heatmap()
        mask = self.get_mask_from_bbox(bbox)
        self.accum_image = cv2.add(self.accum_image, mask)

    def get_heatmap(self, frame):
        accum_image = cv2.blur(self.accum_image, (self.blur, self.blur), cv2.BORDER_DEFAULT)
        self.heatmap = cv2.applyColorMap(accum_image, cv2.COLORMAP_JET)
        frame = cv2.addWeighted(frame, 1, self.heatmap, self.heatmap_merge_thresh, 0)
        return frame