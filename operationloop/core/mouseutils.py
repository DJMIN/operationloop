import pynput
import mouse
import pyWinhook as pyHook
from operationloop.core.screenutils import get_window_attr, get_hwnds

mouse_ctl_1 = mouse
mouse_ctl = pynput.mouse.Controller()


mouse_x_old = None
mouse_y_old = None
mouse_t_old = None
flag = 0
cnt = 0
hwnds = []
now_event = None

FIND_WINDOW_NAME = 'operationloop'


def get_mouse_position():
    return mouse_ctl_1.get_position()


def on_mouse_event(event: pyHook.MouseEvent):
    global flag
    global cnt
    global hwnds
    global now_event

    # 监听鼠标事件
    # if event.Position == (0, 0): 区域放大点好了
    # print(event.Position, event.Message)
    if event.Position[0] < 3 and event.Position[1] < 3 and flag == 0:
        flag = 1
        cnt = 0
        if not hwnds:
            hwnds = get_hwnds()
        for h in hwnds:
            string = get_window_attr(h)
            if FIND_WINDOW_NAME in string:
                cnt = cnt + 1
        flag = 0
    else:
        if hwnds:
            hwnds.clear()

    # 返回 True 以便将事件传给其它处理程序
    # 注意，这儿如果返回 False ，则鼠标事件将被全部拦截
    # 也就是说你的鼠标看起来会僵在那儿，似乎失去响应了
    return True
