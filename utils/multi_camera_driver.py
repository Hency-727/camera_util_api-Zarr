'''
Author: HencyCHEN
Date: 2025-07-27 16:03:14
LastEditTime: 2025-07-28 19:13:53
LastEditors: HencyCHEN
Description: Demo to record multi cameras frames with timestamps to zarr /play zarr-format videos
'''

import os
from omegaconf import DictConfig
from utils.camera_driver import CameraDriver, play_frame
from threading import Thread
import sys, termios, tty



class MultiCameraDriver(CameraDriver):
    def __init__(self, camera_indices: list):
        """ Set up multi cameras """
        self.camera_indices = camera_indices
        self.open_nobug = []
        self.cameras = [CameraDriver(camera_index, is_single_camera=False) for camera_index in camera_indices]
        self.check_multi_camera_running()
    def check_multi_camera_running(self) -> bool:
        """ check if cameras open successfully """
        for camera in self.cameras:
            self.open_nobug.append(camera.check_running())
        print(self.open_nobug)
        for i, camera in enumerate(self.cameras):
            if not self.open_nobug[i]:
                for i, camera in enumerate(self.cameras):
                    camera.release()
                    print(f"============== Release Camera {camera.camera_index} ==============")
            elif i == 1:        
                print("============== All cameras are opened successfully ==============")
        
    def record_multi_camera_to_zarr(
        self,
        output_zarr_paths: list,
        num_frames: int = 500,
        compress_level: int = 3,
    ):
        t = Thread(target=self.thread_monitor, daemon=True)
        t.start()

        # multi camera recording
        threads = []
        # self.error_queue = queue.Queue()  # store error information

        try:
            for i, camera in enumerate(self.cameras):
                # print(camera)
                thread = Thread(target=camera.record_camera_to_zarr,
                                args=(output_zarr_paths[i], num_frames, compress_level))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join() 
            
        except RuntimeError as e:
            raise ValueError(f"Unknown error: {e}")
        else:
            t.join()
            print("==================== Finished recording ====================")

    def thread_monitor(self):
        # switch the terminal to character mode
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        print("==================== press 'q' exiting ====================")
        try:
            while True:
                c = self.is_key_pressed()
                if c == 'q':
                    for camera in self.cameras:
                        camera.stop()
                    break
        finally:
            # recover terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("==================== main process : exit ====================")
    def thread_join(self, threads):
        for thread in threads:
            thread.join() 
    def debug_while(self):
        if self.error_queue.empty():
            print('==================== debug while ====================') 
        while not self.error_queue.empty():
            error_message = self.error_queue.get()
            print(error_message)
    
def main(cfg: DictConfig):
    """ Record Mode """
    if cfg.camera_mode == "record":
        if cfg.mode == "is_multi":
            """ Assuming 2 cameras """
            multi_driver = MultiCameraDriver(camera_indices=[cfg.is_multi.record.camera_index_1, cfg.is_multi.record.camera_index_2])  # 假设有两个相机

            output_zarr_paths = [
                os.path.join("data", "multi_cameras", cfg.is_multi.record.sensor_name_1, cfg.is_multi.record.category),
                os.path.join("data", "multi_cameras", cfg.is_multi.record.sensor_name_2, cfg.is_multi.record.category)
            ]
            
            for path in output_zarr_paths:
                os.makedirs(path, exist_ok=True)
            
            existing = []
            for path in output_zarr_paths:
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    if os.path.isdir(full_path) and name.endswith(".zarr"):
                        id_str = name[:-5]  
                        if id_str.isdigit():
                            existing.append(int(id_str))

            next_id = max(existing) + 1 if existing else 1
            session_id = f"{next_id:03d}"

            # set output path
            out_zarr_paths = [
                os.path.join(output_zarr_paths[0], f"{session_id}.zarr"),
                os.path.join(output_zarr_paths[1], f"{session_id}.zarr")
            ]

            print(f"Recording session_id={session_id}")

            if all(multi_driver.open_nobug):
                # time.sleep(2)
                multi_driver.record_multi_camera_to_zarr(
                    output_zarr_paths=out_zarr_paths,
                    num_frames=cfg.is_multi.record.num_frames,
                    compress_level=cfg.is_multi.record.compress_level
                )
            else:
                print(f"=================== Some camera is not open ===================")
    
    elif cfg.camera_mode == "play":
        """ Play Mode """
        play_frame(cfg)
    else:
        raise ValueError(f"Unknown mode: {cfg.camera_mode}")