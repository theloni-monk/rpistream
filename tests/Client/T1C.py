from rpistream.streamclient import Client

client = Client(serverIp="localhost", port = 5000) # Connects to the server
client.startStream() # Starts recieving data and displaying the video
