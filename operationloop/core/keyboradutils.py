from ctypes import windll
import keyboard
import os
import time

# 注册DD DLL，64位python用64位，32位用32位，具体看DD说明文件。
# 测试用免安装版。
# 用哪个就调用哪个的dll文件。
import pyWinhook

dll_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'keyboard.64.dll')
if not os.path.exists(dll_file_path):
    dll_file_path = r'keyboard.64.dll'
dd_dll = windll.LoadLibrary(dll_file_path)
time.sleep(1.5)
if dd_dll.DD_btn(0) != 1:  # DD Initialize
    print("dd_dll err")
    exit(0)
print("dd_dll init OK")

# DD虚拟码，可以用DD内置函数转换。
vk = {
    '5': 205, 'c': 503, 'n': 506, 'z': 501, '3': 203, '1': 201, 'd': 403, '0': 210, 'l': 409, '8': 208, 'w': 302,
    'u': 307, '4': 204, 'e': 303, '[': 311, 'f': 404, 'y': 306, 'x': 502, 'g': 405, 'v': 504, 'r': 304, 'i': 308,
    'a': 401, 'm': 507, 'h': 406, '.': 509, ',': 508, ']': 312, '/': 510, '6': 206, '2': 202, 'b': 505, 'k': 408,
    '7': 207, 'q': 301, "'": 411, '\\': 313, 'j': 407, '`': 200, '9': 209, 'p': 310, 'o': 309, 't': 305, '-': 211,
    '=': 212, 's': 402, ';': 410, 'up': 709, 'down': 711, 'left': 710, 'right': 712, 'ctrl': 600, 'shift': 500,
    'alt': 602, 'esc': 100, 'caps lock': 400, 'space': 603, 'f1': 101, 'f2': 102, 'f3': 103, 'f4': 104, 'f5': 105,
    'f6': 106, 'f7': 107, 'f8': 108, 'f9': 109, 'f10': 110, 'f11': 111, 'f12': 112, 'delete': 706, 'end': 707,
    'page down': 708, 'page up': 705, 'insert': 703, 'home': 704, 'pause': 702, 'scroll lock': 701,
    'print screen': 700, 'backspace': 214, 'tab': 300, 'enter': 313, 'num lock': 810,

    '"': 411, '#': 203, ')': 210, '^': 206, '?': 510, '>': 509, '<': 508, '+': 212, '*': 208, '&': 207,
    '{': 311, '_': 211, '|': 313, '~': 200, ':': 410, '$': 204, '}': 312, '%': 205, '@': 202, '!': 201, '(': 209
}

# 需要组合shift的按键。
vk2 = {'"': "'", '#': '3', ')': '0', '^': '6', '?': '/', '>': '.', '<': ',', '+': '=', '*': '8', '&': '7', '{': '[',
       '_': '-',
       '|': '\\', '~': '`', ':': ';', '$': '4', '}': ']', '%': '5', '@': '2', '!': '1', '(': '9'}

# SCAN_CODE_2_DD = {}
# SCAN_CODE_2_KEY = {}
KEY_2_SCAN_CODE = {}
KEY_2_DD = {}


def init_mapping():
    # global SCAN_CODE_2_DD
    # global SCAN_CODE_2_KEY
    global KEY_2_SCAN_CODE
    global KEY_2_DD
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scancode.csv')
    if not os.path.exists(file_path):
        file_path = 'scancode.csv'
    with open(file_path, 'r') as f_key:
        for line in f_key:
            if line.startswith('#'):
                continue
            dd_code, scan_code, key_name = line.strip().split('\t')
            dd_code = int(dd_code)
            scan_code = int(scan_code)
            if key_name in KEY_2_SCAN_CODE:
                print('conflict', line.strip(), KEY_2_SCAN_CODE[key_name], KEY_2_SCAN_CODE[key_name])
            # SCAN_CODE_2_DD[scan_code] = dd_code
            # SCAN_CODE_2_KEY[scan_code] = key_name
            KEY_2_SCAN_CODE[key_name] = scan_code
            KEY_2_DD[key_name] = dd_code
    print('init_mapping: ', len(KEY_2_SCAN_CODE))


init_mapping()


def down_up(code):
    # 进行一组按键。
    print(vk[code])
    dd_dll.DD_key(vk[code], 1)
    dd_dll.DD_key(vk[code], 2)
    # pyautogui.keyDown(code)
    # pyautogui.keyUp(code)


def dd_key(key):
    # 500是shift键码。
    if key.isupper():
        # 如果是一个大写的玩意。

        # 按下抬起。
        dd_dll.DD_key(500, 1)
        down_up(key.lower())
        dd_dll.DD_key(500, 2)

    elif key in '~!@#$%^&*()_+{}|:"<>?':
        # 如果是需要这样按键的玩意。
        dd_dll.DD_key(500, 1)
        down_up(vk2[key])
        dd_dll.DD_key(500, 2)
    else:
        down_up(key)


def key_up(key):
    # dd_dll.DD_key(vk[key.lower()], 1)
    dd_dll.DD_key(KEY_2_DD[key], 1)


def key_down(key):
    # dd_dll.DD_key(vk[key.lower()], 2)
    dd_dll.DD_key(KEY_2_DD[key], 2)


def key_click_dd_code(key):
    print('dd: d:    ', key)
    dd_dll.DD_key(key, 1)
    time.sleep(0.1)
    # print('dd: u:    ', key)
    dd_dll.DD_key(key, 2)
    time.sleep(0.1)


def on_key_event(event: pyWinhook.KeyboardEvent):
    print('-----------------------------------------------------------------------')
    for func_name in dir(event):
        if "__" in func_name:
            continue
        p = getattr(event, func_name)
        print('func_name', func_name, p)
        if callable(p):
            try:
                print(f'{func_name} {p()}')
            except Exception:
                pass
    return True


# keyboard.hook_key('f11', print)
# keyboard.hook(print)

if __name__ == '__main__':
    keys = [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 200, 201, 202, 203, 204, 205, 206, 207,
        208, 209, 210, 211, 212, 213, 214, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313,
        400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 500, 501, 502, 503, 504, 505, 506, 507, 508,
        509, 510, 511, 600, 601, 602, 603, 604, 605, 606, 607, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709,
        710, 711, 712, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816,
    ]

    for k in keys:
        key_click_dd_code(k)

    # key_click_dd_code(815)
