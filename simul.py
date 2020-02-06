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

class Sky(object):

    def __init__(self):
        self.north_pole = (500, 500)
        cv2.namedWindow("sky")
        cv2.createTrackbar('tracker', 'sky', 0, 200, self.update)
        cv2.createTrackbar('speed', 'sky', 50, 150, self.update)
        cv2.createTrackbar('t', 'sky', 0, 10, self.update)
        cv2.setTrackbarPos('tracker', 'sky', 100)
        cv2.setTrackbarPos('speed', 'sky', 100)
        cv2.setTrackbarPos('t', 'sky', 1)

    @property
    def tracker(self):
        delta = cv2.getTrackbarPos('tracker', 'sky') - 100
        ox, oy = self.north_pole
        return ox+delta, oy+delta

    @property
    def speed(self):
        return cv2.getTrackbarPos('speed', 'sky')

    @property
    def t(self):
        return cv2.getTrackbarPos('t', 'sky')

    def update(self, val=None):
        sky = np.zeros(shape=[1000, 1000, 3], dtype=np.uint8)
        tracker = self.tracker
        speed = self.speed/100.0
        sky[self.north_pole] = [255, 255, 255]
        sky[tracker] = [255, 255, 0]
        P = (200, 200)
        t = np.pi * self.t * 10
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
