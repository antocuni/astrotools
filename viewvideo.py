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

    def getframe(self, n):
        """
        Read the frame number n
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        return self.read()

    def close(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, tb):
        self.close()


def main():
    fname = sys.argv[1]
    with VideoFile(fname) as cap:
        for i in range(1000):
            frame = cap.getframe(i)
            if frame is None:
                break

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
