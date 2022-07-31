from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Separator
# from show_lw import lw
# from show_sw import sw
# from show_beq import beq
# from show_j import Jump
from tkinter import *
import time


class R:
    def __init__(self, isplaying, root, time):
        self.isplaying = isplaying
        self.root = root
        self.time = time

    def update_time(self, current_time):
        if current_time != self.time:
            self.time = current_time

    def show_R(self):
        """下面为在画布上展示R型指令的设计"""
        win = Toplevel()
        canvas = Canvas(win, width=1380, height=800, bg='White')
        canvas.pack(expand=True)
        # 最大帧数
        numIdx = 8
        frames = [PhotoImage(file=r'K:\PycharmProjects\operationloop\operationloop\imgs\mouse_screen\499___43_43_43___187_187_187.gif',
                             format='gif -index %i' % (i)) for i in range(numIdx)]

        # 填充帧内容到frames
        def slow_speed():
            # 减速
            if (self.time <= 1500):
                self.time += 100

        def add_speed():
            # 加速
            if (self.time > 100):
                self.time -= 100

        def test_stop():
            """下面为播放与暂停的界面"""
            btn2.place(x=300, y=740)
            btn3.place(x=500, y=740)
            if self.isplaying == True:
                self.isplaying = False
                counter = '播放'
                btn4.config(text=str(counter))
            else:
                self.isplaying = True
                btn4.config(text=str("暂停"))
                update(self.stop_idx)

        def exit_win():
            self.time = 500
            self.isplaying = False
            win.destroy()

        def update(idx):  # 定时器函数
            frame = frames[idx]
            idx += 1  # 下一帧的序号：
            canvas.create_image(15, 15, anchor=NW, image=frame)
            # label.configure(image = frame) # 显示label方法当前帧的图片
            # 0.1秒(500毫秒)之后继续执行定时器函数(update)
            if self.isplaying:
                self.root.after(self.time, update, idx % numIdx)
            else:
                self.stop_idx = idx

        btn1 = Button(win, text="结束", width=10, height=2, bg='White', fg='black',
                      font='宋体 12 bold', relief='raised', command=exit_win)
        btn2 = Button(win, text="加速", width=10, height=2, bg='White', fg='black',
                      font='宋体 12 bold', relief='raised', command=add_speed)
        btn3 = Button(win, text="减速", width=10, height=2, bg='White', fg='black',
                      font='宋体 12 bold', relief='raised', command=slow_speed)
        btn4 = Button(win, text="播放", width=10, height=2, bg='White', fg='black',
                      font='宋体 12 bold', relief='raised', command=test_stop)
        # btn5 = Button(win, text="绘图", width=10, height=2, bg='White', fg='black',
        #   font='宋体 12 bold', relief='raised', command= paint_photo)

        btn1.place(x=100, y=740)
        btn4.place(x=700, y=740)
        win.after(0, update(0))


class test_menu:
    def __init__(self, root, time):
        self.title = ' 大勇'
        self.root = root
        self.time = time
        self.isplaying = False
        self.stop_idx = 0
        # self.show_about
        # self.minimum
        # self.show_test
        # self.text_exit
        # choose_R = R()
        # btn1 = Button(
        #     self.root, text="R", width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
        #               command=choose_R.show_R)
        # btn1.place(x=200, y=20)
        # label2 = Label(self.root, text=str, wraplength=180)
        # label2.pack()

    def get_time(self):
        return self.time

    def minimum(self):
        self.root.iconify()

    # 让窗口最小化
    def text_exit(self):
        # 弹出式窗口页面
        ret = messagebox.askquestion("EXIT", '确定要离开吗？')
        if ret == 'yes':
            self.root.destroy()

    def show_about(self):
        # 菜单内的那个关于
        root1 = Toplevel()
        root1.title("关于")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = 300
        y = 240
        w = (screen_width - x) / 2
        h = (screen_height - y) / 2
        root1.geometry('%dx%d+%d+%d' % (x, y, w, h))
        label1 = Label(root1, text='gif', fg='black', bg='white')
        label1.pack()
        sep = Separator(root1, orient=HORIZONTAL)
        sep.pack(fill=X, pady=5)
        str1 = "test"
        label2 = Label(root1, text=str1, wraplength=180)
        label2.pack()
        label3 = Label(root1, text='制作时间:2021年6月1日', fg='black', bg='white')
        label3.pack()
        root1.mainloop()

    def show_test(self):
        def rate(current_time):
            ret = messagebox.askokcancel('更改速度', '确定更改速度或者取消？')
            if ret == True:
                self.time -= current_time
                choose_R.update_time(self.time)
                # choose_lw.update_time(self.time)
                # choose_sw.update_time(self.time)
                # choose_beq.update_time(self.time)

        def show_popupmenu(event):
            popmenu.post(event.x_root, event.y_root)

        # 获取窗口的大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.title("模拟数据通路")
        # root.iconbitmap('mystar.ico')
        # 下面为设置窗口的大小，x为宽，y为高,w，h为离左边的位置
        x = 720
        y = 480
        w = (screen_width - x) / 2
        h = (screen_height - y) / 2
        self.root.geometry('%dx%d+%d+%d' % (x, y, w, h))

        # 声明各个类的对象
        time = self.get_time()
        choose_R = R(self.isplaying, self.root, time)
        # choose_lw = lw(self.isplaying, self.root, time)
        # choose_sw = sw(self.isplaying, self.root, time)
        # choose_beq = beq(self.isplaying, self.root, time)
        # choose_j = Jump(self.isplaying, self.root, time)

        btn1 = Button(self.root, text="R", width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
                      command=choose_R.show_R)
        # btn2 = Button(self.root, text="lw", width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
        #               command=choose_lw.show_lw)
        # btn3 = Button(self.root, text="sw", width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
        #               command=choose_sw.show_sw)
        # btn4 = Button(self.root, text='beq', width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
        #               command=choose_beq.show_beq)
        # btn5 = Button(self.root, text='jump', width=15, font='宋体 12 bold', relief='raised', bg='white', fg='blue',
        #               command=choose_j.show_jump)

        menubar = Menu(self.root)
        # 建立菜单类对象，并将此菜单类别命名为File
        filemenu = Menu(menubar)
        menubar.add_cascade(label='菜单', font='宋体 36 bold', menu=filemenu)
        # 在FIle菜单中建立子菜单列表
        findmenu = Menu(filemenu, tearoff=False)
        findmenu.add_command(label='1.0x', command=lambda: rate(0))
        findmenu.add_command(label='1.25x', command=lambda: rate(100))
        findmenu.add_command(label='1.5x', command=lambda: rate(100))
        findmenu.add_command(label='2.0x', command=lambda: rate(200))
        findmenu.add_command(label='0.75x', command=lambda: rate(-200))
        findmenu.add_command(label='0.5x', command=lambda: rate(-400))
        filemenu.add_cascade(label='速度 ', menu=findmenu, command=rate)
        filemenu.add_command(label='关于', command=self.show_about)
        filemenu.add_command(label='退出', command=self.text_exit)
        # 显示菜单对象
        self.root.config(menu=menubar)
        popmenu = Menu(self.root, tearoff=False)
        findmenu1 = Menu(popmenu, tearoff=False)
        # 建立弹出式菜单对象
        findmenu1.add_command(label='1.0x', command=lambda: rate(0))
        findmenu1.add_command(label='1.25x', command=lambda: rate(100))
        findmenu1.add_command(label='1.5x', command=lambda: rate(100))
        findmenu1.add_command(label='2.0x', command=lambda: rate(200))
        findmenu1.add_command(label='0.75x', command=lambda: rate(-200))
        findmenu1.add_command(label='0.5x', command=lambda: rate(-400))
        popmenu.add_cascade(label='速度', menu=findmenu1)
        popmenu.add_command(label='最小化', command=self.minimum)
        popmenu.add_command(label='退出', command=self.text_exit)

        self.root.bind('<Button-3>', show_popupmenu)

        btn1.place(x=200, y=20)
        # btn2.place(x=200, y=80)
        # btn3.place(x=200, y=140)
        # btn4.place(x=200, y=200)
        # btn5.place(x=200, y=260)
        # 程序图标
        # self.root.iconbitmap('D:/Python_code/tk/final/gif/1.ico')
        self.root.mainloop()

from tkinter import *
# 主函数
if __name__=="__main__":
    root = Tk()
    my_menu = test_menu(root,500)
    my_menu.show_test()
