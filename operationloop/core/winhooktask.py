import threading
import pythoncom
import time
import pyWinhook as pyHook
import ctypes

user32 = ctypes.windll.user32


class HookManager:
    def __init__(self, on_mouse_event, on_key_event):
        self.start_time = 0
        self.on_mouse_event = on_mouse_event
        self.on_key_event = on_key_event
        self.hm = pyHook.HookManager()

    def run_hook(self, use_ui=False):  # 用于开始按键的监听
        self.start_time = time.time()  # 初始化开始时间
        # 进行监听
        # 创建一个“钩子”管理对象

        # 监听所有鼠标事件
        self.hm.MouseAll = self.on_mouse_event
        self.hm.KeyAll = self.on_key_event
        # 设置鼠标“钩子”
        self.hm.HookMouse()
        # hm.start()
        self.hm.HookKeyboard()

        # # 进入循环，如不手动关闭，程序将一直处于监听状态
        if not use_ui:
            getattr(pythoncom, 'PumpMessages')()
        print('stop HookMouse HookKeyboard')

    def close(self, use_ui=False):
        self.hm.UnhookKeyboard()
        self.hm.UnhookMouse()
        if not use_ui:
            user32.PostQuitMessage(0)

    def start_hook(self, use_ui=False):
        # key_listen_thread = threading.Thread(target=start_key_listen_pynput)  # 创建用于监听按键的线程
        listen_thread = threading.Thread(target=self.run_hook)  # 创建用于监听按键的线程
        # 运行线程
        listen_thread.start()


if __name__ == '__main__':
    pass