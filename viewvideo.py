import sys
import cv2
import numpy as np

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
        self.cap = VideoFile(fname)

    def run(self):
        fps = 25.0 # seconds
        ms_delay = int(1000/fps) # milliseconds per frame
        with self.cap:
            i = 0
            self.show(i)
            while True:
                ch = chr(cv2.waitKey(ms_delay) & 0xFF)
                if ch == 'q':
                    break
                elif ch == '+':
                    i += 1
                    self.show(i)
                elif ch == '-':
                    i -= 1
                    self.show(i)


    def show(self, n):
        print('Frame', n)
        frame = self.cap.get_frame(n)
        assert frame is not None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', gray)



def main():
    fname = sys.argv[1]
    viewer = MyViewer(fname)
    viewer.run()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
