import socket
import cv2
import camera
import io
import numpy as np
from tempfile import TemporaryFile
import zstandard
import atexit
from netutils import *

class Server:
    def __init__(self,**kwargs):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((kwargs.get("bindto",""), kwargs.get("port",8080)))
        s.listen(10)
        self.s = s
        self.verbose = kwargs.get("verbose",True)
        atexit.register(self.close)

    def serve(self):
        """Find client"""
        while True:
            self.conn, self.clientAddr = self.s.accept()
            if self.verbose:
                print('Connected with ' + self.clientAddr[0] + ':' + str(self.clientAddr[1]))
            return None
                
    def startStream(self,getFrame,args=[]):
        """ Creates videostream, calls getFrame to recieve new frames
        Args:
            getFrame: Function executed to generate image frame 
            args: the argumetns passed to the getFrame function

        Returns:
            void
        """
        #send initial frame
        Sfile=io.BytesIO()
        C=zstandard.ZstdCompressor()
        prevFrame=getFrame(*args)
        np.save(Sfile,prevFrame)
        send_msg(self.conn,C.compress(Sfile.getvalue()))

        while True:
            Tfile=io.BytesIO()
            #fetch the image
            #print ("Fetching frame...")
            img=getFrame(*args)
            #use numpys built in save function to diff with prevframe
            #because we diff it it will compress more
            np.save(Tfile, img-prevFrame)
            #compress it into even less bytes
            b = C.compress(Tfile.getvalue())
            #reassing prev frame
            prevFrame=img
            #send it            
            send_msg(self.conn,b)
            #print("Sent {}KB".format(int(lend/1000)))

    def close(self):
        """Close all connections"""
        self.s.close()

def retrieveImage(cam,imgResize):
    """Basic function for retrieving camera data, for getFrame"""
    image = cv2.resize(cam.image,(0,0),fx=0.5,fy=0.5)
    return image

if __name__ == "__main__":
    cam = camera.Camera(mirror=True)
    resize_cof=0.5 # 480p
    server = Server(port=5000)
    server.serve()
    server.startStream(retrieveImage,[cam,resize_cof])
