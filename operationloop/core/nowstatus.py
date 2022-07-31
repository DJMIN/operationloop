from operationloop.threadtask import mousetask


class StatusNow:

    @property
    def mouse_point(self):
        return getattr(mousetask, "mouse_x_old"), getattr(mousetask, "mouse_y_old")


if __name__ == '__main__':
    print(StatusNow().mouse_point)