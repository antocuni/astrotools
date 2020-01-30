import sys
import cv2
import numpy as np
import time

class VideoFile(object):

    def __init__(self, filename):
        cap = cv2.VideoCapture(filename)
        self.cap = cap

    def read(self):
        # read the next frame
        (grabbed, frame) = self.cap.read()
        if not grabbed:
            return None
        return frame

    def get_frame(self, n):
        """
        Read the frame number n
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        return self.read()

    def get_frame_count(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def close(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, tb):
        self.close()


class MyViewer(object):

    def __init__(self, fname):
        self.fname = fname
        self.title = fname
        self.cap = VideoFile(fname)
        cv2.namedWindow(self.title)
        cv2.createTrackbar('Frame', self.title , 0, self.cap.get_frame_count(), self.update)
        cv2.createTrackbar('Delta', self.title , 0, 1000, self.update)

    @property
    def curframe(self):
        return cv2.getTrackbarPos('Frame', self.title)

    @property
    def delta(self):
        return cv2.getTrackbarPos('Delta', self.title)

    def is_window_visible(self):
        # I don't know why, but WND_PROP_VISIBLE does not seem to work :(
        return cv2.getWindowProperty(self.title, cv2.WND_PROP_AUTOSIZE) == 1

    def run(self):
        fps = 25.0 # seconds
        ms_delay = int(1000/fps) # milliseconds per frame
        with self.cap:
            self.update()
            # loop until the window is closed
            while self.is_window_visible():
                ch = chr(cv2.waitKey(ms_delay) & 0xFF)
                if ch == 'q':
                    break

    def update(self, val=None):
        start = time.time()
        # average all the frames from curframe to curframe+delta
        curframe = self.curframe
        frame = self.cap.get_frame(curframe)
        assert frame is not None
        frame64 = frame.astype(np.float64)
        for i in range(self.delta):
            frame64 += self.cap.get_frame(curframe+i)
        frame64 /= self.delta+1
        frame = frame64.astype(np.uint8)
        end = time.time()
        print('Time to stack %d frames: %.2f ms' % (self.delta, ((end-start)*1000)))
        #
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow(self.title, gray)




def main():
    fname = sys.argv[1]
    viewer = MyViewer(fname)
    viewer.run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
