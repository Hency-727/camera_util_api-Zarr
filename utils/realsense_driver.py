'''
Author: HencyCHEN
Date: 2025-07-29 18:53:16
LastEditTime: 2025-07-29 18:55:14
LastEditors: HencyCHEN
Description: 
FilePath: /easy_camera_api-Zarr/utils/realsense_driver.py
Email: hengxiangchen428@gamil.com
可以输入预定的版权声明、个性签名、空行等
'''
import pyrealsense2 as rs
import numpy as np
import cv2
 
class RealsenseDriver:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)
    def get_frame(self):
        try:
            while True:
                # Wait for a coherent pair of frames: depth and color
                self.frames = self.pipeline.wait_for_frames()
                self.depth_frame = self.frames.get_depth_frame()
                self.color_frame = self.frames.get_color_frame()
                if not self.depth_frame or not self.color_frame:
                    continue
                # Convert images to numpy arrays
    
                depth_image = np.asanyarray(self.depth_frame.get_data())
    
                color_image = np.asanyarray(self.color_frame.get_data())
    
                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                # Stack both images horizontally
                images = np.hstack((color_image, depth_colormap))
                # Show images
                cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('RealSense', images)
                key = cv2.waitKey(1)
                # Press esc or 'q' to close the image window
                if key & 0xFF == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    break
        finally:
            # Stop streaming
            self.pipeline.stop()
if __name__ == "__main__":
    # Configure depth and color streams
    realsense_driver = RealsenseDriver()
    realsense_driver.get_frame()
