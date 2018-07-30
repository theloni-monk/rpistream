import socket
import cv2
import rpistream.camera
import io
import numpy as np
from tempfile import TemporaryFile
import zstandard
import atexit
from rpistream.netutils import *


class Server:
    def __init__(self, **kwargs):
        print("Initilizing socket")
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((kwargs.get("bindto", ""), kwargs.get("port", 8080)))
        s.listen(10)
        self.s = s
        self.verbose = kwargs.get("verbose", True)
        atexit.register(self.close)
        print("Server ready")
    
    def log(self,m):
        if self.verbose:
            print(m) #printout if verbose

    def serve(self):
        """Find client"""
        self.log("Searching for client...")
        while True:
            self.conn, self.clientAddr = self.s.accept() #wait for client to query the server for a connection
            self.log('Connected to ' + self.clientAddr[0] + ':' + str(self.clientAddr[1]))
            return None #only connects to one client 

    def startStream(self, getFrame, args=[]):
        """ Creates videostream, calls getFrame to recieve new frames
        Args:
            getFrame: Function executed to generate image frame 
            args: the argumetns passed to the getFrame function

        Returns:
            void
        """
        # send initial frame of intra-frame compression
        Sfile = io.BytesIO()
        C = zstandard.ZstdCompressor()
        prevFrame = getFrame(*args)
        np.save(Sfile, prevFrame)
        send_msg(self.conn, C.compress(Sfile.getvalue()))

        frameno = 0
        while True:
            #instanciate temporary bytearray to send later
            Tfile = io.BytesIO()

            # fetch the image
            self.log("Fetching frame...")
            img = getFrame(*args)
            
            # use numpys built in save function to diff with prevframe
            # because we diff it it will compress more
            np.save(Tfile, img-prevFrame)

            # compress it into even less bytes
            b = C.compress(Tfile.getvalue())

            # saving prev frame
            prevFrame = img

            # send it
            send_msg(self.conn, b)
            if self.verbose:
                self.log("Sent {}KB (frame {})".format(int(len(b)/1000),frameno)) #debugging
                frameno+=1

    def close(self):
        """Close all connections"""
        self.s.close()



#this a helper for the __main__ func
def retrieveImage(cam, imgResize):
    """Basic function for retrieving camera data, for getFrame"""
    image = cv2.resize(cam.image, (0, 0), fx=imgResize, fy=imgResize)
    return image

# runs if you directly run this file
if __name__ == "__main__":
    cam = rpistream.camera.Camera(mirror=True)
    resize_cof = 1  # 960p
    server = Server(port=5000)
    server.serve()
    server.startStream(retrieveImage, [cam, resize_cof])
