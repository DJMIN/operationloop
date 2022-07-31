from PIL import Image, ImageSequence, ImageTk
from tkinter import PhotoImage

STR_FRAME_FILENAME = "frame{}.png"  # 每帧图片的文件名格式


class PlayGif(object):
    def __init__(self, file):  # temporary 指临时目录路径，为空时则随机生成
        self.str_path = file
        self.run_update = True
        self.index = 1  # 当前显示图片的帧数
        self.img_gif = Image.open(self.str_path)
        self.intCount = 0  # gif 文件的帧数
        self.file_mem = {}
        self.this_f_idx = 0
        self.decompose_pics()  # 开始分解
        self.width, self.height = self.img_gif.size  # 得到图片的尺寸

    def decompose_pics(self):  # 分解 gif 文件的每一帧到独立的图片文件，存在临时目录中
        for idx, frame in enumerate(ImageSequence.Iterator(self.img_gif)):  # 遍历每帧图片
            # print(frame.fp.tell())
            # a_tmp = Image.open(frame.fp)
            # self.file_mem[idx] = ImageTk.PhotoImage(a_tmp)

            self.file_mem[idx] = PhotoImage(file=self.str_path, format=f'gif -index {idx}')
        self.intCount = len(self.file_mem)  # 得到 gif 的帧数
        self.img_gif.close()

    def get_picture(self, frame=0):  # 返回第 frame 帧的图片(width=0,height=0)
        if frame == 0:
            frame = self.index
        elif frame >= self.intCount:
            frame = self.intCount  # 最后一张
        try:
            self.this_f_idx = frame
            img = self.file_mem[self.this_f_idx - 1]

            # print(self.str_path, frame, img)
            self.index = self.get_next_frame_index()
            return img  # 返回图片

        except Exception as ex:
            print(123123123, type(ex), ex, self.str_path, self.index)
            self.run_update = False

    def get_next_frame_index(self, frame=0):  # 返回下一张的帧数序号
        if frame == 0:
            frame = self.index  # 按当前插入帧数
        if frame == self.intCount:
            return 1  # 返回第1张，即从新开始播放
        else:
            return frame + 1  # 下一张

    def play(self, tk, canvas):  # 开始调用自身实现播放，time 单位为毫秒
        img = self.get_picture()

        def clear_item(item):
            canvas.delete(item)

        def _init():
            for key in [
                # 'image',
                'text1',
                'text2',
                'text3',
            ]:
                if item := getattr(canvas, key, None):
                    clear_item(item)

        if img:
            try:
                _init()
                canvas.image = canvas.create_image(60, 60, image=img)
            except Exception as ex:
                print(1111111111111, type(ex), ex)
                return
            if self.this_f_idx == 1:
                canvas.text1 = canvas.create_text((60, 60), text=f"+", fill="#FFFF66")
                canvas.text2 = canvas.create_text((60, 80), text=f"{self.this_f_idx}/{self.intCount}", fill="#FFFF66")
                canvas.text3 = canvas.create_text((60, 100), text=f"{img.get(60, 60)}", fill="#FFFF66")
            elif self.this_f_idx == self.intCount:
                canvas.text1 = canvas.create_text((60, 60), text=f"+", fill="#33cc33")
                canvas.text2 = canvas.create_text((60, 80), text=f"{self.this_f_idx}/{self.intCount}", fill="#33cc33")
                canvas.text3 = canvas.create_text((60, 100), text=f"{img.get(60, 60)}", fill="#33cc33")
            else:
                canvas.text1 = canvas.create_text((60, 60), text=f"+", fill="#F76727")
                canvas.text2 = canvas.create_text((60, 80), text=f"{self.this_f_idx}/{self.intCount}", fill="#F76727")
                canvas.text3 = canvas.create_text((60, 100), text=f"{img.get(60, 60)}", fill="#F76727")
            # canvas.itemconfig(imgo, iamge=img)
            if self.run_update:
                time_int = 1500 if self.this_f_idx in [self.intCount, 0, 1, 2] else 100
                tk.after(time_int, self.play, tk, canvas)  # 在 time 时间后调用自身
        else:
            return

    def close(self):
        self.run_update = False
        self.img_gif.close()
        for img in self.file_mem.values():
            del img

    def __del__(self):  # 关闭动画文件，删除临时文件及目录
        try:
            self.close()
        except Exception as ex:
            print(22222222222, type(ex), ex)
        return True
        # self.close()


# 初始化窗口宽高
S_WIDTH = 876
S_HEIGHT = 720
# 初始化左边高清大图宽高
I_WIDTH = 710
I_HEIGHT = 682
# 初始化右边缩略图宽高
SUB_WIDTH = 166
SUB_HEIGHT = 166


class ResizePNG:
    def __init__(self, top):
        self.top = top
        self.top.bind('<Configure>', self.window_resize)
        self.label = None
        self.caches = []
        self.cache_paths = []
        self.image_pos = 0

    def load_image(self, position=0):
        if len(self.caches) > 0 and len(self.caches) > position >= 0:
            try:
                image = resize_image(self.cache_paths[position], screen_width=self.top.winfo_width(),
                                     screen_height=self.top.winfo_height())
                photo = ImageTk.PhotoImage(image)
                # 假设这里是使用Label组件显示高清图片
                self.label.config(image=photo)
                self.label.image = photo
                # print(self.caches[position])
            except FileNotFoundError:
                self.reload_caches()
        else:
            photo = None
            self.label.config(image=photo)
            self.label.image = photo

    def reload_caches(self):
        raise NotImplemented

    def window_resize(self, event=None):
        if event is not None:
            # listen events of window resizing.
            # 窗口宽高任一值产生变化，则记录并使展示高清大图自适应窗体调整。
            # 1)
            if self.window_width != self.top.winfo_width() or self.window_height != self.top.winfo_height():
                if self.window_width != self.top.winfo_width():
                    self.window_width = self.top.winfo_width()
                if self.window_height != self.top.winfo_height():
                    self.window_height = self.top.winfo_height()
                # What happens here?
                if self.first_load:
                    self.first_load = False
                else:
                    # 重新设置展示的图片大小
                    self.load_image(self.image_pos)
        '''
        # 2)
        # 其中self.can为self.photo_canvas的容器，self.photo_canvas是显示图像的画布，两者都是Canvas类型。Amaz!22/2/20 Sun.)
        self.win_resized = self.can.winfo_width() != self.win_width or self.can.winfo_height() != self.win_height
        if self.win_resized:
            # Canvas has been resized.
            self.win_width = self.can.winfo_width()
            self.win_height = self.can.winfo_height()
            if self.first_load:
                self.first_load = False
            else:
                self.photo_canvas.config(width=self.win_width)
                self.load_image(self.image_pos)
        '''


def resize_image(path, scale=-1, screen_width=0, screen_height=0):
    image = Image.open(path)
    if scale == -1:
        # 高清大图原始宽高
        raw_width, raw_height = image.size[0], image.size[1]
        # 减去右边缩略图宽的最大宽度，减除工具栏（假设有且高40）的最大高度
        max_width, max_height = max(I_WIDTH, screen_width - SUB_WIDTH), max(I_HEIGHT, screen_height - 40)
        min_height = min(max_height, raw_height)
        # 按比例缩放高清大图
        min_width = int(raw_width * min_height / raw_height)
        # 如果大图超出窗体显示区域，进行第二次（或多次）缩放
        if min_width > max_width:
            min_width = min(max_width, raw_width)
            min_height = int(raw_height * min_width / raw_width)
    return image.resize((min_width, min_height))


# 原文链接：https://blog.csdn.net/qq_21264377/article/details/119900475


def unpack_gif(src):
    # Load Gif
    image = Image.open(src)

    # Get frames and disposal method for each frame
    frames = []
    disposal = []
    for gifFrame in ImageSequence.Iterator(image):
        disposal.append(gifFrame.disposal_method)
        frames.append(gifFrame.convert('P'))

    # Loop through frames, and edit them based on their disposal method
    output = []
    last_frame = None
    for i, loadedFrame in enumerate(frames):
        # Update thisFrame
        this_frame = loadedFrame

        # If the disposal method is 2
        if disposal[i] == 2:
            # Check that this is not the first frame
            if i != 0:
                # Pastes thisFrames opaque pixels over lastFrame and appends lastFrame to output
                last_frame.paste(this_frame, mask=this_frame.convert('RGBA'))
                output.append(last_frame)
            else:
                output.append(this_frame)

        # If the disposal method is 1 or 0
        elif disposal[i] == 1 or disposal[i] == 0:
            # Appends thisFrame to output
            output.append(this_frame)

        # If disposal method if anything other than 2, 1, or 0
        else:
            raise ValueError(
                'Disposal Methods other than 2:Restore to Background,'
                ' 1:Do Not Dispose, and 0:No Disposal are supported at this time')

        # Update lastFrame
        last_frame = loadedFrame

    return output
