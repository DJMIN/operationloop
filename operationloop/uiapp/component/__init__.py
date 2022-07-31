import tkinter


class FrameGridBox(tkinter.Frame):
    def __init__(self, master=None, cnf=None, **kw):
        if not cnf:
            cnf = {}
        super().__init__(master=master, cnf=cnf, **kw)
        self.pack(side='top')
        self.grid_col_idx = 0
        self.grid_row_idx = 0


class AnimatedGifList:
    def __init__(self, home, root, src):
        self.home = home
        self.root = root

        # Load Frames
        self.image_path = src
        self.frames = []
        self.duration = []
        for frame in unpack_gif(self.image_path):
            self.duration.append(frame.info['duration'])
            self.frames.append(frame)
        self.counter = 0
        self.image = self.frames[self.counter]

        # Create Label
        self.label = tkinter.Canvas(self.root, height=120, width=120)
        # Start Animation
        self.__step_frame()

    def __step_frame(self):
        # Update Frame
        # self.label.config(image=self.frames[self.counter])

        img = self.label.create_image(60, 60, image=PhotoImage(self.image))
        self.label.create_text((60, 60), text="+", fill="#FFF227")
        self.label.itemconfig(img, image=PhotoImage(self.image))
        self.image = self.frames[self.counter]

        # Loop Counter
        self.counter += 1
        if self.counter >= len(self.frames):
            self.counter = 0

        # Queue Frame Update
        self.home.update()
        self.home.after(self.duration[self.counter], lambda: self.__step_frame())

    # def pack(self, **kwargs):
    #     self.label.pack(**kwargs)

    def grid(self, **kwargs):
        self.label.grid(**kwargs)
