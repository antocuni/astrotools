import math
import cv2
import numpy as np

def rotate(point, radians, origin=(0, 0)):
    """
    Rotate a point around a given point.
    """
    x, y = point
    ox, oy = origin

    qx = ox + math.cos(radians) * (x - ox) + math.sin(radians) * (y - oy)
    qy = oy + -math.sin(radians) * (x - ox) + math.cos(radians) * (y - oy)

    return qx, qy

SKY_ROT_SPEED = (np.pi*2)/(60*60*24) # 360 deg / 24h, radians/s

class CvTrackbar(object):

    def __init__(self, name, win, min, max, callback, default=None):
        self.name = name
        self.win = win
        cv2.createTrackbar(name, win, min, max, callback)
        if default is not None:
            self.value = default

    @property
    def value(self):
        return cv2.getTrackbarPos(self.name, self.win)

    @value.setter
    def value(self, v):
        cv2.setTrackbarPos(self.name, self.win, v)

class Sky(object):

    def __init__(self):
        cv2.namedWindow("sky")
        self.ready = False
        self.north_pole = (500, 500)
        self.tracker = CvTrackbar('tracker', 'sky', 0, 200, self.update, default=100)
        self.speed = CvTrackbar('speed', 'sky', 50, 150, self.update, default=100)
        self.t = CvTrackbar('t', 'sky', 0, 10, self.update, default=1)
        self.ready = True

    def get_tracker_pos(self):
        delta = self.tracker.value - 100
        ox, oy = self.north_pole
        return ox+delta, oy+delta

    def update(self, val=None):
        if not self.ready:
            return

        sky = np.zeros(shape=[1000, 1000, 3], dtype=np.uint8)
        tracker = self.get_tracker_pos()
        speed = self.speed.value / 100.0
        sky[self.north_pole] = [255, 255, 255]
        sky[tracker] = [255, 255, 0]
        P = (200, 200)
        t = np.pi * self.t.value * 10
        for angle in np.arange(0, t, 0.1):
            x, y = rotate(P, angle, self.north_pole)
            x2, y2 = rotate((x, y), -angle*speed, tracker)
            sky[int(x2), int(y2)] = [0, 0, 255]

        cv2.imshow("sky", sky)

    def is_window_visible(self):
        # I don't know why, but WND_PROP_VISIBLE does not seem to work :(
        return cv2.getWindowProperty("sky", cv2.WND_PROP_AUTOSIZE) == 1

    def run(self):
        fps = 25.0 # seconds
        ms_delay = int(1000/fps) # milliseconds per frame
        self.update()
        while self.is_window_visible():
            ch = chr(cv2.waitKey(ms_delay) & 0xFF)
            if ch == 'q':
                break


def main():
    sky = Sky()
    sky.run()

main()
