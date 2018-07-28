# RaspiCameraLivestream

### A very simple library built for streaming video from a remote Raspberry Pi server in realtime.

---

## How to install:

### MacOS or linux:

Open your terminal and type:

``` bash
sudo python -m pip install rpistream
```

### Windows:

Open cmd as admin and type:

```cmd
pip install rpistream
```

---

## Examples:

### Streaming from a webcam

Server

```python
from rpistream.camera import camera
from rpistream.streamserver import Server

def retrieveImage(cam,imgResize):
    image = cv2.resize(cam.image,(0,0),fx=imgResize,fy=imgResize)
    return image

cam = rpistream.camera.Camera(mirror=True)
scale=0.5
server = Server(port=5000)
server.serve() # Blocking; waits for a connection before continuing
server.startStream(retrieveImage,[cam,scale]) # Calls retrieveImage(*args) every frame  
```

Client

```python
from rpistream.streamclient import Client

client = Client(serverIp="localhost", WriteFile=True) # Connects to the server
client.startStream() # Starts recieving data and displaying the video
```
