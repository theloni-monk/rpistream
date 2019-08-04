import cv2
import numpy as np
from multiprocessing import Process, Pipe


class Camera:
    def __init__(self, **kwargs):
        self.mirror = kwargs.get("mirror", False)
        self.deviceId=kwargs.get("device", 0)
        self.cam = cv2.VideoCapture(self.deviceId) #captures from the first webcam it sees by default
        
        self.trueRes=(int(self.cam.get(3)),int(self.cam.get(4)))
        self.sRes = self.trueRes
        self.output = None

    def setRes(self,res):
        """Actually just adjust internal scale value"""
        self.sRes = (int(res[0]),int(res[1]))

    def getFps(self):
        try:
            return self.cam.get(5)
        except: # error type unclear: it is a underlying opencv error
            return None

    @property
    def image(self):
        ret_val, img = self.cam.read()
        if not ret_val:
            raise Exception("Unable to retrieve image from camera")
        if self.mirror:
            img = cv2.flip(img, 1)
        self.output = cv2.resize(img, self.sRes)
        return self.output

if __name__ == "__main__":
    cam = Camera(mirror=True)
    cv2.imwrite("test/test_image.png", cam.image)
