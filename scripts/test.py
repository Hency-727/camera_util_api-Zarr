
'''
Author: HencyCHEN
Date: 2025-07-25 16:11:34
LastEditTime: 2025-07-28 18:06:09
LastEditors: HencyCHEN
Description: main function for one camera
'''

import cv2

def test():


    # cap = cv2.VideoCapture(camera_index)
    # flag = check_running()
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    # cap = cv2.VideoCapture(camera_index)
    # print(f"================== {flag} ==================")
    # if not cap.isOpened():
    #     raise Exception("Failed to open camera!")   
                    
    ret, frame = cap.read()
    if not ret:
        cap.release()
    
    h, w, c = frame.shape

    while True:

        ret, frame = cap.read()

        h, w = frame.shape[:2]
        scale = 0.2
        new_w, new_h = int(w * scale), int(h * scale)
        frame_resize = cv2.resize(frame, (new_w, new_h))

        if not ret:
            print("Failed getting the frame!")
            break
        """ Comment out to prevent blocking """
        cv2.imshow("Camera", frame_resize)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("'q', Quit!")
            break
    cap.release()

import threading
import queue
import sys
import select
import termios
import tty
import time

class Worker:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self._stop = threading.Event()

    def run(self):
        """子线程主循环：每秒打印一次计数，并检查命令"""
        count = 0
        print("Worker：启动循环，等待命令…")
        while not self._stop.is_set():
            print(f"Worker：工作中，count = {count}")
            count += 1
            time.sleep(1)

            # 检查命令
            try:
                cmd = self.cmd_queue.get_nowait()
            except queue.Empty:
                continue

            if cmd == 'stop':
                print("Worker：收到 stop，准备退出")
                self._stop.set()
            elif cmd == 'pause':
                print("Worker：收到 pause，暂停 3 秒")
                time.sleep(3)
            else:
                print(f"Worker：未知命令 {cmd}")

        print("Worker：已退出循环")

    def stop(self):
        """外部调用，发送 stop 命令"""
        self.cmd_queue.put('stop')


def get_key_nonblocking(timeout=0.1):
    dr, _, _ = select.select([sys.stdin], [], [], timeout)
    if dr:
        return sys.stdin.read(1)
    return None

def main():
    worker = Worker()
    t = threading.Thread(target=worker.run, daemon=True)
    t.start()

    # 切换终端到字符模式
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    print("主程序：按 'p' 暂停，按 'q' 停止并退出")

    try:
        while not worker._stop.is_set():
            c = get_key_nonblocking()
            if c == 'p':
                print("主程序：检测到 'p'，发送 pause")
                worker.cmd_queue.put('pause')
            elif c == 'q':
                print("主程序：检测到 'q'，发送 stop")
                worker.stop()
                break
            time.sleep(0.1)
    finally:
        # 恢复终端设置
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("主程序：终端恢复原始模式，等待 Worker 结束…")
        t.join()
        print("主程序：退出")


class test:
    def __init__(self):
        self.a = 1
        self.change_num(self)
    @staticmethod
    def change_num(a):
        a.a = 2

def while_continue_test():
    while True:
        # print("while_continue_test")
        time.sleep(1)
        continue
        print("while_continue_test")

if __name__ == "__main__":
    # 1. load config from config.yaml
    # test()
    # main()
    # while_continue_test()
    t = test()
    print(t.a)