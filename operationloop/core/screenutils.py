import queue

import win32gui
import ctypes
import time
import os
import threading
import win32api
# import win32con
# import win32ui
import imageio
import numpy as np
import mss
import multiprocessing

from ctypes import wintypes
import mouse

# from PIL import ImageSequence, ImageTk
from PIL import Image

user32 = ctypes.WinDLL('user32', use_last_error=True)
# 注册user32中的GetDC参数和返回值
user32.GetDC.restype = wintypes.HDC
user32.GetDC.argtypes = (wintypes.HWND,)

gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
# 注册GetPixel中的GetPixel参数和返回值
gdi32.GetPixel.restype = wintypes.COLORREF
gdi32.GetPixel.argtypes = (wintypes.HDC, ctypes.c_int, ctypes.c_int)

BASE_SAVE_FILE_PATH = r'./imgs'
TMPGIF_PATH = r'./tmpgif'
# 获取监控器信息
moniter_dev = win32api.EnumDisplayMonitors(None, None)
M_w = moniter_dev[0][2][2]
M_h = moniter_dev[0][2][3]

PROCESS_PER_MONITOR_DPI_AWARE = 2  # 解决由于屏幕分辨率缩放导致的，pynput监听鼠标位置不准的问题
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)


def save_to_pbm(filename, save_filename=None):
    if not save_filename:
        save_filename = filename.split('.')[0] + '.pbm'
    im = Image.open(filename)
    im.save(save_filename)


def get_hwnds():
    hwnds = []
    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), hwnds)
    return hwnds


def save_to_gif(filenames, save_filename=None, duration=0.2):
    if not save_filename:
        save_filename = filenames[0]
    save_filename = save_filename.split('.')[0] + '.gif'
    fns = np.stack(
        [imageio.v3.imread(name) for name in filenames],
        axis=0)
    imageio.v3.imwrite(
        save_filename, fns, duration=duration)


class Screen:
    def __init__(self, q=None):
        self.now_screen_dc = None
        self.history_screen_data = []
        self.history_rgb_data = []
        self.history_title_data = []
        self.history_point_data = []
        self.int_time = 0.1
        self._cat_img_queue = q
        self.t_saves = []
        self.t_run = None

    @property
    def cat_img_queue(self):
        if not self._cat_img_queue:
            self._cat_img_queue = queue.Queue()
        return self._cat_img_queue

    def start_all(self):
        self.t_run = threading.Thread(target=self.run_recode_screen, daemon=True)
        self.t_run.start()
        for idx in range(4):
            t = threading.Thread(target=self.run_save_gif_task, daemon=True)
            t.start()
            self.t_saves.append(t)
        print('Screen hook init')

    def run_recode_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            while True:
                start = time.time()
                sct_img = sct.grab(monitor)
                # print(f'截图到内存耗时{ time.time() - start:.3f}s')
                # title = get_active_window_attr()['title']
                # r, g, b = get_screen_color(*mouse.get_position())

                if self.history_screen_data.__len__() > 40:
                    self.history_screen_data.pop(0)
                    # self.history_rgb_data.pop(0)
                    # self.history_title_data.pop(0)
                    # self.history_point_data.pop(0)
                self.history_screen_data.append(sct_img)
                # self.history_rgb_data.append((r, g, b))
                # self.history_title_data.append(title)
                # self.history_point_data.append(mouse.get_position())
                time.sleep(self.int_time)

                # for num, monitor in enumerate(sct.monitors[1:], 1):
                #     # Get raw pixels from the screen
                #     sct_img = sct.grab(monitor)
                #     if self.history_screen_data.__len__() > 20:
                #         self.history_screen_data.pop(0)
                #     self.history_screen_data.append(sct_img)

    def run_save_gif_task(self):
        while True:
            args, kwargs = self.cat_img_queue.get()
            self.save_gif(*args, **kwargs)

    def save_gif_async(self, *args, **kwargs):
        self.cat_img_queue.put((args, kwargs))

    def save_gif(self, filename, x, y, limit_area=60, frame_num=40, file_path='', rgb=()):
        start = time.time()
        screen_data = []
        for img in self.history_screen_data[-frame_num:]:
            box = (x - limit_area, y - limit_area,
                   x + limit_area, y + limit_area)  # 将要裁剪的图片块距原图左边界距左边距离，上边界距上边距离，右边界距左边距离，下边界距上边的距离。
            rect_on_big = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX").crop(box)
            result_image = Image.new('RGB', (limit_area * 2, limit_area * 2), (0, 0, 0, 0))
            box = (0, 0, limit_area * 2, limit_area * 2)
            result_image.paste(rect_on_big, box, mask=0)
            screen_data.append(result_image)
        if screen_data:
            fs = np.stack(screen_data, axis=0)
            rgb = '_'.join(str(it) for it in rgb)
            _rgb = '_'.join(str(it) for it in screen_data[0].getpixel((limit_area, limit_area)))
            file_save_path = get_save_file_path(f'{filename}___{_rgb}___{rgb}.gif', file_path)
            imageio.v3.imwrite(file_save_path, fs, extension=".gif", duration=self.int_time)
            print(f'内存截图到文件耗时{time.time() - start:.3f}s {file_save_path}')

            return file_save_path

        # tmp_imgs = []
        # for i, img in enumerate(screen_data):
        #     # Create the Image
        #     img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        #     # The same, but less efficient:
        #     # img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        #     tmp_imgs.append(img)
        #
        #     # # And save it!
        #     # output = "monitor-{}.png".format(num)
        #     # img.save(filename)
        #     # print(output)


q_s = queue.Queue()


def _run(_q_s):
    Screen(_q_s)
    while True:
        time.sleep(1)


def start_queue():
    global q_s
    p = multiprocessing.Process(target=_run, args=(q_s,), daemon=True)
    p.start()


def put_queue(*args, **kwargs):
    q_s.put((args, kwargs))


screen_listen = Screen()
screen_listen.start_all()
# start_queue()


def get_save_file_path(file_name, file_path=''):
    base_path = os.path.join(os.path.realpath(BASE_SAVE_FILE_PATH), file_path)
    file_path_all = os.path.join(base_path, file_name)
    file_path_base = os.path.dirname(file_path_all)
    if not os.path.exists(file_path_base):
        os.makedirs(file_path_base)
    return file_path_all


def get_screen_color(x, y):
    hdc = user32.GetDC(None)
    color = gdi32.GetPixel(hdc, x, y)
    r = color & 0xFF
    g = color >> 8 & 0xFF
    b = color >> 16 & 0xFF
    return r, g, b


def gbk2utf8(s):
    # return s.decode('gbk').encode('utf-8')
    return s.encode('utf-8')


def get_active_window_attr():
    # hwnd = win32gui.GetForegroundWindow()

    hwnd = win32gui.GetActiveWindow()

    # hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    # # 根据窗口句柄获取窗口的设备上下文DC(Device Context)
    # hwndDC = win32gui.GetWindowDC(hwnd)

    return get_window_attr(hwnd)


def get_window_attr(hwnd):
    """
    显示窗口的属性
    :return:
    """
    if not hwnd:
        return {'title': '未知'}

    # print("窗口句柄:", hwnd)
    # print("窗口标题:", str(title, encoding="utf-8"))#字节流转字符串
    # print("窗口类名:", clsname)

    # 中文系统默认title是gb2312的编码
    title = win32gui.GetWindowText(hwnd)
    title = gbk2utf8(title)
    return {"hwnd": hwnd, "title": str(title, encoding="utf-8")}  # 返回窗口标题字符串


# threading.Thread(target=cat_img_by_queue).start()

if __name__ == '__main__':
    # for i in range(10):
    #     print(i)
    #     screen_listen.save_gif(f'{i}', 50, 80)
    #     # for ii in range(100):
    #     #     print(ii)
    #     time.sleep(1)
    pass
