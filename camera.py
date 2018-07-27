import cv2
import numpy as np
from multiprocessing import Process, Pipe


class Camera:
    def __init__(self, **kwargs):
        self.mirror = kwargs.get("mirror", False)
        self.cam = cv2.VideoCapture(kwargs.get("device", 0))
        self.output = None
        self.paused = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    @property
    def image(self):
        if not self.paused:
            ret_val, img = self.cam.read()
            if self.mirror:
                img = cv2.flip(img, 1)
            self.output = img

        return img
    @property
    def imageNoDistort(self):
        img = self.image

        K = np.array([[1.34747452e+03, 0., 1.28368878e+03],
                      [0., 1.35216936e+03, 9.19253689e+02],
                      [0., 0., 1.]])

        D = np.array([-0.36228031, 0.22272214,
                      0.00182073, 0.00070695, -0.12033373])

        Knew = K.copy()
        Knew[(0, 1), (0, 1)] = 0.4157401081053996 * Knew[(0, 1), (0, 1)]
        imgnew = cv2.undistort(img, K, D, Knew)
        return imgnew

# cv2.waitkey()

if __name__ == "__main__":
    cam = Camera(mirror=True)
    cv2.imwrite("test/test_image.png", cam.image)
