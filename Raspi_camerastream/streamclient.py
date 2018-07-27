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
        #Writing still doesnt work
        self.Write = kwargs.get("WriteFile", False)
        self.writepath = kwargs.get("path", "")
        self.FileFPS = kwargs.get("fileoutFps", 10)
        self.FileName = kwargs.get("fileName", 'outpy.avi')
        self.iRes = kwargs.get("imageResolution", (640, 480))
        self.out = cv2.VideoWriter(
            self.writepath+self.FileName, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.FileFPS, self.iRes)

        self.ip = kwargs.get("serverIp", "18.111.87.85")
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((self.ip, kwargs.get("port", 444)))
        self.D = zstandard.ZstdDecompressor()
        atexit.register(self.close)

    def recv(self, size=1024):
        data = bytearray()
        while 1:
            buffer = self.s.recv(1024)
            data += buffer
            if len(buffer) == 1024:
                pass
            else:
                #print("recv() data ingested")
                return data

    def startStream(self):
        img = np.zeros((3, 3))
        # initial
        prevFrame = np.load(io.BytesIO(self.D.decompress(recv_msg(self.s))))

        while True:
            r = recv_msg(self.s)
            if len(r) == 0:
                continue

            # load decompressed image
            try:  # diff+prevframe
                img = (np.load(io.BytesIO(self.D.decompress(r))) + prevFrame).astype("uint8")

            except Exception as e:
                print(e)

            prevFrame = img
            if self.Write:
                self.out.write(img)

            # show it scaled up
            cv2.imshow("feed", cv2.resize(img, (0, 0), fx=3.0, fy=3.0))
            if cv2.waitKey(1) == 27:
                break  # esc to quit

    def close(self):
        self.out.release()
        self.s.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ianIp = "10.189.81.154"
    rasPiIp = "18.111.87.85"
    client = Client(serverIp=rasPiIp, WriteFile=True, port=5000)
    client.startStream()
