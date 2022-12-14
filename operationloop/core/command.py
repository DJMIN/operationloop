import os
import shutil
import time
import typing
import keyboard
import pyWinhook
from functools import partial
from operationloop.core.keyboradutils import key_up, key_down
from operationloop.core import keyboradutils
from operationloop.core.screenutils import screen_listen, get_screen_color, get_save_file_path, put_queue, start_queue
from operationloop.core.mouseutils import mouse_ctl_1, mouse_ctl
from operationloop.core.winhooktask import HookManager
from multiprocessing import Pipe

MOUSE_SCREEN_SAVE_PATH = 'mouse_screen'
SHORT_CUT_KEY = 'F12'


class Command:
    WINDOWS_FLAG = '    |wiN|: '

    def __init__(self, device='', params='', time_offset=0.0, windows=''):
        self.device = device
        self.params = self.params_loads(params)
        self.windows = windows
        self.time_offset = time_offset

    @staticmethod
    def params_loads(params):
        new_params = []
        for param in params:
            new_params.append(str(param))
        return new_params

    @property
    def is_mouse_event(self):
        return self.device == Constant.Mouse

    @property
    def is_keyboard_event(self):
        return self.device == Constant.Keyboard

    @property
    def keyboard_event_run_func(self):
        func = {
            Constant.KEY_UP: key_up,
            Constant.KEY_DOWN: key_down,
        }.get(self.params[0], None)

        def null_action():
            return

        if func:
            return partial(func, self.params[1])
        else:
            return null_action

    @property
    def mouse_event_run_func(self):
        func = {
            Constant.MOUSE_LEFT_DOWN: partial(mouse_ctl_1.press, mouse_ctl_1.LEFT),
            Constant.MOUSE_RIGHT_DOWN: partial(mouse_ctl_1.press, mouse_ctl_1.RIGHT),
            Constant.MOUSE_MID_DOWN: partial(mouse_ctl_1.press, mouse_ctl_1.MIDDLE),
            Constant.MOUSE_LEFT_UP: partial(mouse_ctl_1.release, mouse_ctl_1.LEFT),
            Constant.MOUSE_RIGHT_UP: partial(mouse_ctl_1.release, mouse_ctl_1.RIGHT),
            Constant.MOUSE_MID_UP: partial(mouse_ctl_1.release, mouse_ctl_1.MIDDLE),
            Constant.MOUSE_WHEEL: partial(mouse_ctl_1.wheel, self.mouse_wheel_param),
        }.get(self.params[0], None)

        def time_sleep(num=0.03):
            time.sleep(num)
            return func

        if func:
            return time_sleep

    def play(self, skip_move=False, before_press_time=0.03, move_type=1):
        if self.is_mouse_event:
            mouse_event_run_func = self.mouse_event_run_func
            if not skip_move or mouse_event_run_func:
                if move_type == 1:
                    position_now_x, position_now_y = mouse_ctl.position
                    move_x, move_y = self.mouse_position
                    mouse_ctl.move(move_x - position_now_x, move_y - position_now_y)
                else:
                    mouse_ctl_1.move(*self.mouse_position)
            if mouse_event_run_func:
                mouse_event_run_func(before_press_time)()
        elif self.is_keyboard_event:
            self.keyboard_event_run_func()
        # else:

    @property
    def params_format(self):
        return ' '.join(f'{str(p):4s}' for p in self.params)

    @property
    def time_offset_int(self):
        return int(self.time_offset)

    @property
    def keyboard_event(self):
        return self.params[0]

    @property
    def keyboard_key(self):
        return self.params[1]

    @property
    def mouse_position(self):
        return int(self.params[1]), int(self.params[2])

    @property
    def mouse_wheel_param(self):
        return int(self.params[3]) if self.params.__len__() > 3 else 0

    @property
    def rgb(self):
        if self.params.__len__() == 6:
            return int(self.params[3]), int(self.params[4]), int(self.params[5])

    @property
    def time_offset_float(self):
        return self.time_offset - self.time_offset_int

    @property
    def time_offset_float_all(self):
        return float(self.time_offset)

    def __str__(self):
        float_str = f'{self.time_offset_float:.6f}'.split('.')[-1]
        return f"{self.device:2s} {self.time_offset_int:07d}.{float_str} " \
               f"{self.params_format} {self.WINDOWS_FLAG}{self.windows}"

    def __repr__(self):
        return f"device:{self.device:2s} time:{self.time_offset_float:.3f} " \
               f"{repr(self.params_format)} {self.WINDOWS_FLAG}{self.windows}"

    def loads(self, string: str):
        tmp, windows = string.strip().split(self.WINDOWS_FLAG, maxsplit=1)
        device, time_offset, *params = tmp.strip().split()
        self.device = device
        # x, y, r, g, b, wheel_int
        # x, y, wheel_int
        self.params = params
        self.time_offset = float(time_offset)
        self.windows = windows
        return self


class MouseEventType:
    MOUSE_LEFT_DOWN = str(int(pyWinhook.HookConstants.WM_LBUTTONDOWN))
    MOUSE_LEFT_UP = str(int(pyWinhook.HookConstants.WM_LBUTTONUP))
    MOUSE_RIGHT_DOWN = str(int(pyWinhook.HookConstants.WM_RBUTTONDOWN))
    MOUSE_RIGHT_UP = str(int(pyWinhook.HookConstants.WM_RBUTTONUP))
    MOUSE_MID_DOWN = str(int(pyWinhook.HookConstants.WM_MBUTTONDOWN))
    MOUSE_MID_UP = str(int(pyWinhook.HookConstants.WM_MBUTTONUP))
    MOUSE_WHEEL = str(int(pyWinhook.HookConstants.WM_MOUSEWHEEL))


class MouseEventType1:
    MOUSE_LEFT_DOWN = 'mouseleftdown'
    MOUSE_LEFT_UP = 'mouseleftup'
    MOUSE_RIGHT_DOWN = 'mouserightdown'
    MOUSE_RIGHT_UP = 'mouserightup'
    MOUSE_MID_DOWN = 'mousemiddledown'
    MOUSE_MID_UP = 'mousemiddleup'
    MOUSE_WHEEL = 'mousewheel'


class KeyboardEventType:
    KEY_DOWN = 'k_d'
    KEY_UP = 'k_u'


class Constant(MouseEventType, KeyboardEventType):
    Mouse = 'M'
    Keyboard = 'K'
    # Mouse = 'Mouse'
    # Keyboard = 'Keyboard'


def unicode_convert(input_data):
    # ???unicode?????????str
    if isinstance(input_data, dict):
        return {unicode_convert(key): unicode_convert(value) for key, value in input_data.items()}
    elif isinstance(input_data, list):
        return [unicode_convert(element) for element in input_data]
    elif isinstance(input_data, str):
        return input_data
    else:
        return input_data


def format_path(path):
    # ??????????????????????????????,????????????????????????,????????????????????????,??????????????????????????????????????????
    # ???????????????:,?????????????????????????????????
    path = unicode_convert(path)
    if path[2] != ":":
        # ??????????????????????????????????????????
        path = os.path.join(os.path.dirname(__file__), path)

    return path


class CommandList:
    def __init__(self, path='command.txt', pwrite=None, wqueue=None, skip_move=False):
        self.s_time = 0
        # self.path = format_path(path)
        self.path = path
        self.data_list: typing.List[Command] = []
        self.start_time = time.time()
        self.is_running = False
        self.time_offset_this = 0
        self.time_offset_last = 0
        self.hook_listener = None
        # self.skip_move = True
        self.skip_move = skip_move
        self.pwrite = pwrite
        self.wqueue = wqueue
        self.last_time_img = 0
        self.keys_mapping = {}
        self.keys_mapping1 = {}
        # self.log_file = open('log.log', 'w', encoding='utf-8')
        # start_queue()

    def __repr__(self):
        return '\n'.join(str(c) for c in self.data_list)

    def __str__(self):
        if self.data_list:
            return 'CommandList: len:[{}] all_time:{}'.format(
                len(self.data_list),
                self.data_list[-1].time_offset - self.data_list[0].time_offset
            )
        else:
            return 'CommandList: null'

    def clear(self):
        return self.data_list.clear()

    def add(self, device, params, windows, time_offset=0.0, rgb=()):
        self.time_offset_this = self.time_offset_last + time_offset if time_offset else time.time() - self.start_time
        command = Command(device, params + (list(rgb) if rgb else []), self.time_offset_this, windows)
        self.data_list.append(command)
        self.time_offset_last = self.time_offset_this
        return command

    def add_mouse_auto(self, action: int, position=(), rgb=(), windows='', wheel_int=0):
        """
            pyWinhook.HookConstants.WM_MOUSEFIRST,  # 0x0200
            pyWinhook.HookConstants.WM_MOUSEMOVE,  # 0x0200
            pyWinhook.HookConstants.WM_LBUTTONDOWN,  # 0x0201
            pyWinhook.HookConstants.WM_LBUTTONUP,  # 0x0202
            pyWinhook.HookConstants.WM_RBUTTONDOWN,  # 0x0204
            pyWinhook.HookConstants.WM_RBUTTONUP,  # 0x0205
            pyWinhook.HookConstants.WM_MBUTTONDOWN,  # 0x0207
            pyWinhook.HookConstants.WM_MBUTTONUP,  # 0x0208
            pyWinhook.HookConstants.WM_MOUSEWHEEL,  # 0x020A
        """
        return self.add(
            Constant.Mouse, [action, *(position or mouse_ctl_1.get_position()), wheel_int],
            rgb=rgb, windows=windows)

    def add_mouse_click_auto(self, x, y, time_offset=0.07, rgb=(), windows='', wheel_int=0):
        position = (x, y)
        self.add(
            Constant.Mouse,
            [pyWinhook.HookConstants.WM_LBUTTONDOWN, *(position or mouse_ctl_1.get_position()), wheel_int],
            rgb=rgb, windows=windows, time_offset=time_offset)
        self.add(
            Constant.Mouse,
            [pyWinhook.HookConstants.WM_LBUTTONUP, *(position or mouse_ctl_1.get_position()), wheel_int],
            rgb=rgb, windows=windows, time_offset=0.02)

    def add_key_auto(self, action, key_string, scan_code=0, windows=''):
        return self.add(Constant.Keyboard, [action, key_string, scan_code], windows=windows)

    def load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                self.data_list.append(Command().loads(line))

    def dump(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            for command in self.data_list:
                f.write(f'{command}\n')
        print(f'????????????????????????{os.path.realpath(self.path)}')

    def stop_recode(self, use_ui=False):
        self.hook_listener.close(use_ui)
        self.is_running = False

    def stop(self, _event):
        self.is_running = False
        keyboard.unhook(SHORT_CUT_KEY.lower())

    def count(self, command_type):
        return len([ll for ll in self.data_list if ll.params[0] == command_type])

    def replay(self):
        # ??????????????????????????????
        self.s_time = time.time()
        self.is_running = True
        keyboard.hook_key(SHORT_CUT_KEY.lower(), self.stop)

        print(f'??????????????????{os.path.realpath(self.path)}: len:{len(self.data_list)}')
        now_idx = 0
        for idx, command in enumerate(self.data_list):
            now_idx = idx + 1
            if not self.is_running:
                break
            time_sleep = max(0.0, command.time_offset - (time.time() - self.s_time))
            if time_sleep > 0:
                time.sleep(time_sleep)
            print(f'{idx}-------{repr(command)}-  {time_sleep}s')
            command.play(skip_move=self.skip_move)

            # command[2]???????????????????????????????????????????????????,?????????????????????????????????????????????????????????????????????
        log = (f"play: {now_idx}/{len(self.data_list)}    "
               f"L_DOWN:{self.count(Constant.MOUSE_LEFT_DOWN)}    "
               f"R_DOWN:{self.count(Constant.MOUSE_RIGHT_DOWN)}    "
               f"keyboard: {self.count(Constant.KEY_DOWN)}    "
               f"cost: {time.time() - self.s_time:.6f}    "
               f"should: {self.data_list[-1].time_offset_float_all:.6f}")
        print(log)
        self.is_running = False
        return log

    def on_mouse_event(self, event: pyWinhook.MouseEvent):
        x, y = event.Position
        if event.Message not in [pyWinhook.HookConstants.WM_MOUSEMOVE]:
            if (time.time() - self.last_time_img) > 0.3:
                self.last_time_img = time.time()
                rgb = get_screen_color(x, y)
                screen_listen.save_gif_async(
                    # put_queue(
                    f'{len(self.data_list) + 1}', x, y, file_path=MOUSE_SCREEN_SAVE_PATH, rgb=rgb,
                    time_click=time.time())
            else:
                rgb = ()
            command = self.add_mouse_auto(
                event.Message,
                # event.MessageName.replace(' ', ''),
                (x, y),
                rgb=rgb, windows=event.WindowName, wheel_int=event.Wheel)
        elif not self.skip_move:
            command = self.add_mouse_auto(
                event.Message,
                # event.MessageName.replace(' ', ''),
                (x, y), windows=event.WindowName)
        else:
            command = None
        if self.pwrite:
            self.pwrite.send(str(command))
        if self.wqueue:
            self.wqueue.put(str(command))
        return True

    # def append_log(self, string):
    #     self.log_file.write(f'{string}\n')
    #     self.log_file.flush()

    def on_key_event(self, event: pyWinhook.KeyboardEvent):
        if event.ScanCode == keyboradutils.KEY_2_SCAN_CODE[SHORT_CUT_KEY]:
            command = None
            self.stop_recode()
        else:
            # if event.Message in [256, 260]:
                # print(f'{str(event.Message)}\t{event.ScanCode}\t{str(event.Key)}')
            command = self.add_key_auto(
                (KeyboardEventType.KEY_UP if event.Message in [256, 260] else KeyboardEventType.KEY_DOWN),
                event.Key, scan_code=event.ScanCode, windows=event.WindowName
            )

        if self.pwrite:
            self.pwrite.send(str(command))
        if self.wqueue:
            self.wqueue.put(str(command))
        return True

    def recode(self, block=True):
        path = os.path.dirname(get_save_file_path('tmp', MOUSE_SCREEN_SAVE_PATH))
        print(f'????????????????????????{path}')
        if os.path.exists(path) and MOUSE_SCREEN_SAVE_PATH in path:
            shutil.rmtree(path)

        self.s_time = time.time()
        self.is_running = True
        self.hook_listener = HookManager(self.on_mouse_event, self.on_key_event)
        self.hook_listener.start_hook()

        while block and self.is_running:
            time.sleep(1)
        if block:
            self.stop_recode()


def eg_base():
    com_list = CommandList()
    print('starting recode')
    com_list.recode()
    com_list.dump()
    print('starting replay')
    com_list = CommandList()
    com_list.load()
    com_list.replay()


def eg_base_skip():
    com_list = CommandList(skip_move=True)
    print('starting recode')
    com_list.recode()
    com_list.dump()
    print('starting replay')
    com_list = CommandList()
    com_list.load()
    com_list.replay()


def eg_base_run():
    com_list = CommandList(skip_move=False)
    print('starting replay')
    # com_list.load()

    def bit_1(_idx):
        return [
            (1944, 881),
            (1980, 883),
            (2010, 883),
            (2043, 877),
            (2074, 884),
            (2107, 886),
            (2142, 877),
            (2170, 881),
        ][_idx]

    def _down(_bit, num):
        com_list.add_mouse_click_auto(*bit_1(_bit))
        for _i in range(int(num)):
            com_list.add_mouse_click_auto(1971, 814)

    def _ok():
        com_list.add_mouse_click_auto(2123, 816)

    def add(_bit, num):
        com_list.add_mouse_click_auto(*bit_1(_bit))
        for _i in range(int(num)):
            com_list.add_mouse_click_auto(2039, 815)
    malast= '12349876'

    manew = '23512547'
    for bit, ch in enumerate(malast):
        _down(bit, ch)

    for bit, ch in enumerate(manew):
        add(bit, ch)

    _ok()

    com_list.dump()
    com_list.replay()


if __name__ == '__main__':
    # eg_base()
    eg_base_skip()
    # eg_base_run()

    # print(com_list)
    # print(repr(com_list))
