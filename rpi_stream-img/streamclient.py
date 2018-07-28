import socket
import numpy as np
import io
import cv2
# zstd might work on other computers but only zstandard will work with mine
import zstandard
import atexit
from netutils import *


class Client:

    def __init__(self, **kwargs):
        # output file seems to be corrupted: likely due to output file stream not being closed correctly
        self.Write = kwargs.get("WriteFile", False)
        self.writepath = kwargs.get("path", "")
        self.FileFPS = kwargs.get("fileoutFps", 10)
        self.FileName = kwargs.get("fileName", 'outpy')
        self.iRes = kwargs.get("imageResolution", (1280, 960))
        self.viewScale = kwawrgs.get("viewscale", 1.0)
        self.out = cv2.VideoWriter(
            self.writepath+self.FileName+'.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.FileFPS, self.iRes)

        self.ip = kwargs.get("serverIp", "18.111.87.85")
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((self.ip, kwargs.get("port", 8080)))
        self.D = zstandard.ZstdDecompressor()
        self.viewScale = kwargs.get("viewScale", 1)
        atexit.register(self.close)

    def recv(self, size=1024):
        """Recieves a single frame
        Args:
            size: how big a frame should be
                default: 1024
        returns:
            single data frame
        """
        data = bytearray()
        while 1:
            buffer = self.s.recv(1024)
            data += buffer
            if len(buffer) == 1024:
                pass
            else:
                return data

    def startStream(self):
        """Decodes files from stream and displays them"""
        img = np.zeros((3, 3))
        # initial
        prevFrame = np.load(io.BytesIO(self.D.decompress(recv_msg(self.s))))

        while True:
            r = recv_msg(self.s)
            if len(r) == 0:
                continue

            # load decompressed image
            try:  # diff+prevframe
                img = (np.load(io.BytesIO(self.D.decompress(r))) +
                       prevFrame).astype("uint8")

            except Exception as e:
                print(e)

            prevFrame = img
            if self.Write:
                self.out.write(img)

            # show it scaled up
            cv2.imshow("feed", cv2.resize(
                img, (0, 0), fx=self.viewScale, fy=self.viewScale))
            if cv2.waitKey(1) == 27:
                break  # esc to quit

    def close(self):
        """Closes socket and opencv instances"""
        self.out.release()
        self.s.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    client = Client(serverIp="localhost", WriteFile=True)
    client.startStream()
