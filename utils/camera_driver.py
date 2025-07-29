'''
Author: Hengxiangchen-Hency
Date: 2025-07-25 15:18:52
LastEditTime: 2025-07-29 19:41:56
LastEditors: HencyCHEN
Description: Demo to record one camera frames to zarr /play zarr-format videos
'''
import os
import cv2
import zarr
from numcodecs import Blosc
from omegaconf import DictConfig
import time
from threading import Event, Thread
import queue
import time
import sys, select, termios, tty
import numpy as np
from realsense_driver import RealsenseDriver
class CameraDriver:
    def __init__(self, camera_index: int = 0, is_play_mode: bool = False, is_single_camera: bool = True, is_realsense: bool = True):
        self.camera_index = camera_index
        self.is_realsense = is_realsense
        self.cmd_queue = queue.Queue()
        self._stop_event = Event()  # set to stop recording event
        self.is_play_mode = is_play_mode
        if not self.is_play_mode:
            print(f"============= Record mode, Init camera {self.camera_index}=============") 
            if is_single_camera:
                self.check_running()
            if is_realsense:
                self.realsense = RealsenseDriver()
    def record_single_camera_to_zarr(self,
        output_zarr_path: str,
        num_frames: int = 500,
        compress_level: int = 3
        # error_queue = None
    ):
        t = Thread(target=self.thread_monitor, daemon=True)
        t.start()
        self.record_camera_to_zarr(
            output_zarr_path=output_zarr_path,
            num_frames=num_frames,
            compress_level=compress_level
        )
        t.join()

    def record_camera_to_zarr(
        self,
        output_zarr_path,
        num_frames,
        compress_level,
        # error_queue = None
    ):
        try:
            if self.is_realsense:
                realsense = RealsenseDriver()
                frame = realsense.pipeline.wait_for_frames().get_color_frame()
                if not frame:
                    print("No frame from realsense")
                    realsense.pipeline.stop()
            else:
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.release()
            
            h, w, c = frame.shape

            if os.path.exists(output_zarr_path):
                os.system(f"rm -rf {output_zarr_path}")
            store = zarr.DirectoryStore(output_zarr_path)
            root = zarr.group(store=store, overwrite=True)
            compressor = Blosc(cname='zstd', clevel=compress_level)

            ds = root.create_dataset(
                "frames",
                shape=(num_frames, h, w, c),
                chunks=(1, h, w, c),
                dtype='uint8',
                compressor=compressor
            )

            ds_timestamps = root.create_dataset(
                "timestamps",
                shape=(num_frames,),
                dtype='f8'  # collecting timestamps
            )

            # prev_time = time.time()  # calculate the time of the first frame

            print(f"Starting collecting（at most {num_frames} frames）")
            i = 0


            while not self._stop_event.is_set():
  
                if self.is_realsense:
                    frame = realsense.pipeline.wait_for_frames().get_color_frame()
                    frame = np.asanyarray(frame.get_data())
                else:
                    ret, frame = self.cap.read()
                
                current_time = time.time()

                """ Caclculate FPS """
                # elapsed_time = current_time - prev_time
                # print(f"{self.camera_index} output elapsed time : {elapsed_time}, current time : {current_time}")
                # prev_time = current_time

                h, w = frame.shape[:2]
                scale = 0.2
                new_w, new_h = int(w * scale), int(h * scale)
                frame_resize = cv2.resize(frame, (new_w, new_h))

                if not ret:
                    print("Failed getting the frame!")
                    break
                ds[i] = frame
                ds_timestamps[i] = current_time

                i += 1
                """ Comment out to prevent blocking """
                if self.is_play_mode:
                    cv2.imshow("Camera", frame_resize)

                # key = cv2.waitKey(1) & 0xFF
                # if key == ord('q'):
                #     print("'q', Quit!")
                #     break
                time.sleep(0.01) 

                """ check command to exit """
                try:
                    cmd = self.cmd_queue.get_nowait()
                except queue.Empty:
                    continue

                if cmd == 'stop':
                    print(f"=============== Get stop command, {self.camera_index} ready to exit! ===============")
                    self._stop_event.set()
                else:
                    print(f"unknown command : {cmd}")    
                if i >= num_frames:
                    break

            self.release()
            print(f"Collecting {i} frames into {output_zarr_path}")

        except Exception as e:
            # if error_queue is not None:
            #     error_queue.put(f"camera {self.camera_index} error: {str(e)}")  # put errer message to queue
            raise e
    def stop(self):
        """ Setting stop event """
        # self._stop_event.set()
        self.cmd_queue.put('stop')
    def check_running(self) -> bool:

        if self.is_realsense:
            frame = self.realsense.pipeline.wait_for_frames().get_color_frame()
            if not frame:
                print("No frame from realsense")
                return False
            else:
                return True    

        else:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            else:
                print(f"open camera {self.camera_index}")
                return True
    
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
                    self.stop()
                    break
        finally:
            # recover terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("==================== main process：exit ====================")

    @staticmethod
    def is_key_pressed():
        """ Non-blockingly check if a key was pressed on stdin 
            and return the character pressed 
            (or None if no key was pressed).
        """
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None
    def release(self):
        if self.is_realsense:
            self.realsense.pipeline.stop()
        else:
            self.cap.release()
        # cv2.destroyAllWindows()
        # time.sleep(2)
    def read_and_play_zarr_visual(
        self,
        input_zarr_path: str,
        delay_ms: int = 50
    ):
        dataset_name: str = "frames"
        # prev_time = time.time()

        store = zarr.DirectoryStore(input_zarr_path)
        root = zarr.open(store, mode="r")
        if dataset_name not in root:
            raise KeyError(f"dataset '{dataset_name}' does not exist in zarr store.")
        ds = root[dataset_name]
        n_frames, h, w, c = ds.shape
        print(f"Sum frame num: {n_frames}, resolu: {h}x{w}, 通道: {c}")
        print("Start recording, press 'q' exit")
        for i in range(n_frames):
            # current_time = time.time()
            # elapsed_time = current_time - prev_time
            # print(elapsed_time)
            # prev_time = current_time
            frame = ds[i]
            h, w = frame.shape[:2]
            scale = 0.2
            new_w, new_h = int(w * scale), int(h * scale)
            frame_resize = cv2.resize(frame, (new_w, new_h))
            cv2.imshow("Playback", frame_resize)
            if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

def main(cfg: DictConfig):
    """ Record Mode """
    if cfg.camera_mode == "record":
        if cfg.mode == "is_single":
            driver = CameraDriver(camera_index=cfg.is_single.record.camera_index, is_single_camera=cfg.mode, is_realsense=cfg.is_multi.record.REALSENSE)
            out_dir = os.path.join("data", "single_camera", cfg.is_single.record.sensor_name, cfg.is_single.record.category)
            os.makedirs(out_dir, exist_ok=True)
            """ Automatically detect existing .zarr session folders and generate the next three-digit number """
            existing = []
            """ An empty set returns an empty list [] """
            for name in os.listdir(out_dir):
                path = os.path.join(out_dir, name)
                if os.path.isdir(path) and name.endswith(".zarr"):
                    id_str = name[:-5]
                    if id_str.isdigit():
                        existing.append(int(id_str))
            next_id = max(existing) + 1 if existing else 1
            session_id = f"{next_id:03d}"
            out_zarr = os.path.join(out_dir, f"{session_id}.zarr")
            print(f"Recording session_id={session_id}")
            driver.record_single_camera_to_zarr(
                output_zarr_path=out_zarr,
                num_frames=cfg.is_single.record.num_frames,
                compress_level=cfg.is_single.record.compress_level
            )
    elif cfg.camera_mode == "play":
        play_frame(cfg)  
    else:
        raise ValueError(f"Unknown mode: {cfg.camera_mode}")(f"Unknown mode: {cfg.camera_mode}")
        
def play_frame(cfg: DictConfig):
    """ Play Mode """
    driver = CameraDriver(camera_index=None, is_play_mode=True)
    in_zarr = os.path.join(cfg.play.play_path)
    driver.read_and_play_zarr_visual(
        input_zarr_path=in_zarr,
        # dataset_name=cfg.is_single.play.dataset_name,
        delay_ms=cfg.play.delay_ms
    )
