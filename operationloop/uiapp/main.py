import os  # 用于文件操作
import time

import PIL
import keyboard
import win32con
import win32api
import sys
import threading  # 由于键盘和鼠标事件的监听都是阻塞的,所以用两个线程实现
import multiprocessing
import queue
import tkinter  # 绘制操作界面
from tkinter import messagebox
from PIL.Image import open as imread
from PIL.ImageTk import PhotoImage
from win32com.client import GetObject
from operationloop.core.imgutils import PlayGif
from operationloop.uiapp.component import FrameGridBox
from operationloop.core.command import CommandList
from operationloop.core.command import SHORT_CUT_KEY

IMG_PATH = r'./imgs/mouse_screen'
all_tk = None
S_WIDTH = 800
S_HEIGHT = 500


def add_item(father, item, max_row_cnt=5):
    item.grid(column=father.grid_col_idx, row=father.grid_row_idx)
    father.grid_col_idx += 1
    if father.grid_col_idx == max_row_cnt:
        father.grid_col_idx = 0
        father.grid_row_idx += 1
    return item


class TKMain:
    def __init__(self):
        global all_tk
        all_tk = self
        self.top = tkinter.Tk()
        self.top.title('windows操作录制重放工具')
        self.top.wm_title('windows操作录制重放工具')
        # 默认窗口包含标题栏
        self.top.overrideredirect(False)
        # 初始化窗口大小并自适应屏幕居中
        self.top.geometry(str(S_WIDTH) + 'x' + str(S_HEIGHT) + '+'
                          + str((self.top.winfo_screenwidth() - S_WIDTH) // 2) + '+'
                          + str((self.top.winfo_screenheight() - S_HEIGHT) // 2 - 18))

        self.col_idx = 0
        self.row_idx = 0
        self.tmp_l = []
        self.tmp_l_g = []
        self.im = []
        frame1 = FrameGridBox(self.top)
        self.l1 = add_item(frame1, tkinter.Label(frame1, text=f'按{SHORT_CUT_KEY} 开始/退出 录制，暂不支持键盘组合键'))
        self.b1 = add_item(frame1, tkinter.Button(frame1, text='录制', width=7, height=1, command=self.record_opt))
        keyboard.hook_key(SHORT_CUT_KEY.lower(), self.start_recode_shortcut)

        self.b2 = add_item(frame1, tkinter.Button(frame1, text='执行', width=7, height=1, command=self.exec_op))
        self.l3 = add_item(frame1, tkinter.Label(frame1, text='请输入执行次数，默认为1次'))
        self.search = tkinter.StringVar()
        self.count = tkinter.StringVar()
        self.isRunning = False
        self.e1 = add_item(frame1, tkinter.Entry(frame1, textvariable=self.count))
        self.search_box = tkinter.Label(self.top, textvariable=self.search)
        self.search_box.pack()

        self.show_img(IMG_PATH)
        self.canvas = tkinter.Frame(self.top)
        self.canvas.pack(side='bottom')
        self.queue = queue.Queue()
        self.pread, self.pwrite = multiprocessing.Pipe(duplex=False)
        self.command_list = None
        self.t = threading.Thread(target=self.hook_loop)
        self.t.start()
        self.top.bind('<<pyHookEvent>>', self.on_pyhook)
        self.top.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.top.mainloop()
        # start_queue()

    def start_recode_shortcut(self, event):
        print(event.event_type)
        if event.event_type == 'up':
            self.record_opt()

    def on_quit(self):
        self.quit_fun()
        self.top.destroy()

    def on_pyhook(self, event):
        if not self.queue.empty():
            msg = self.queue.get()
            # print(msg)
            self.search.set(str(msg))
            if msg.startswith('M') and (' 513 ' in msg):
                self.top.after(1600, self.show_img, IMG_PATH)

    def quit_fun(self):
        self.pwrite.send('quit')

    def hook_loop(self):
        while 1:
            msg = self.pread.recv()
            # print(msg)
            if type(msg) is str and msg == 'quit':
                print('exiting hook_loop')
                break
            self.top.event_generate('<<pyHookEvent>>', when='tail')

    def do_params(self, filepath):
        source_img = imread(filepath)
        size = source_img.size
        w, h = size
        # 用来判断 刷新显示前 是否改变了图像大小
        change_size = True
        # 图片相对于源图的缩放比例
        upper = 120 / h
        if (w * upper) > 120:
            upper = 120 / w
        new_size = (int(w * upper), int(h * upper))
        img = source_img.resize(new_size)
        if len(self.im) > 17:
            self.im = self.im[1:]
        self.im.append((PhotoImage(img), filepath))

    def do_params1(self, filepath):
        if len(self.im) > 14:
            self.im.pop(0)
        self.im.append(filepath)

    def show_img(self, filepaths):
        self.close_all_t()
        self.canvas = tkinter.Frame(self.top)
        self.canvas.pack(side='bottom')
        # return
        self.tmp_l = []
        self.tmp_l_g = []
        self.im = []
        for root, fs, fns in os.walk(filepaths):
            fns.sort(key=lambda x: int(x.split('_')[0]))
            for fn in fns[-15:]:
                filepath = os.path.join(root, fn)
                if filepath.endswith('.gif'):
                    self.do_params1(filepath)
        row_len = 5
        self.tmp_l = []
        self.tmp_l_g = []
        for idx, im in enumerate(self.im):
            name = os.path.basename(im)
            try:
                idxx, x, y = name.split('___')[0].split('_')
                title = name.split('___')[1].split('.')[0].split('_', maxsplit=3)[-1]
                tit = f'{idx + 1}\n{idxx}: {title}\n{x} {y}'
            except ValueError:
                tit = name
            # tit = name.split('___')[0] + name.split('___')[1]
            l_idx = tkinter.Label(self.canvas, text=tit)
            l_idx.grid(column=idx % row_len, row=idx // row_len * 2)

            l_img = tkinter.Canvas(self.canvas, height=120, width=120)
            # l_img.create_text((60, 60), text="+", fill="#FFF227")
            try:
                gl = PlayGif(im)
                gl.play(self.canvas, l_img)
                self.tmp_l_g.append(gl)
            except PIL.UnidentifiedImageError:
                print(f'文件损毁:{im}')
            l_img.grid(column=idx % row_len, row=idx // row_len * 2 + 1)
            self.tmp_l.append(l_img)
            self.tmp_l.append(l_idx)
            # img = AnimatedGif(self.top, self.canvas, src=im[1])
            # img.grid(column=idx % row_len, row=idx // row_len * 2 + 1)

            # l_img = tkinter.Canvas(self.canvas, height=120, width=120)
            # l_img.create_image(60, 60, image=im[0])
            # l_img.create_text((60, 60), text="+", fill="#FFF227")
            # l_img.grid(column=idx % row_len, row=idx // row_len * 2 + 1)
        self.top.update()

    @staticmethod
    def tip_pop(string):
        tkinter.messagebox.showinfo('提示', string)

    def close_all_t(self):
        while self.tmp_l_g:
            t = self.tmp_l_g.pop()
            try:
                t.close()
                del t
            except AttributeError:
                pass
        while self.tmp_l:
            t = self.tmp_l.pop()
            try:
                t.destroy()
                del t
            except AttributeError:
                pass
        if getattr(self, "canvas", None):
            self.canvas.destroy()
            self.canvas = None

    def record_opt(self):
        self.isRunning = not self.isRunning

        # # 等待线程结束,也就是等待用户按下esc
        if self.isRunning:
            # self.top.iconify()  # 窗口隐藏
            self.command_list = CommandList(pwrite=self.pwrite, wqueue=self.queue, skip_move=False)
            self.close_all_t()
            self.top.update()
            self.command_list.recode(False)
            self.show_img(IMG_PATH)
        else:
            # self.top.deiconify()  # 窗口显现
            self.command_list.stop_recode(use_ui=True)
            self.command_list.dump()
            self.show_img(IMG_PATH)

    def exec_op(self):
        self.top.iconify()  # 窗口隐藏
        run_count = 0
        count = self.count.get()
        self.isRunning = True
        if len(count) == 0:
            count = '1'
        if count.isdigit():
            for i in range(int(count)):
                run_count = i
                self.command_list.replay()
            print("执行成功%d/%d次!" % (run_count, int(count)))
            tkinter.messagebox.showinfo('提示', "执行成功%d/%d次!" % (run_count + 1, int(count)))
        else:
            print("执行失败！请键入数字")
            tkinter.messagebox.showerror('提示', '执行失败！\n请键入数字！')
        self.top.deiconify()  # 窗口显现
        self.isRunning = False


def main():  # 主函数
    # TODO 驱动级键盘输入和监听
    # TODO 鼠标拖动录制和模拟
    # TODO 键盘组合键
    # for i in '123123123123123':
    #     dd(i)
    #     time.sleep(1)
    wmi = GetObject('winmgmts:')
    p_main = os.path.basename(sys.argv[0])
    print("start:", p_main)
    processes = wmi.ExecQuery(f'Select * from Win32_Process where Name = "{p_main}"')
    if len(processes) > 2:
        print(processes)
        win32api.MessageBox(0, f"{p_main}已在后台运行，请勿重复打开", f"{p_main}提示", win32con.MB_OK)
        exit(0)

    main_ui = TKMain()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
