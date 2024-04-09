#import serial
import time


#ser = serial.Serial('/dev/ttyUSB0', 115200)  # Adjust the port name if needed


#ser.write(b'BOOT\n')

# Obtain and print the IP address
import socket
ip_address = socket.gethostbyname(socket.gethostname())
print(ip_address)

# Rest of the code remains unchanged from here onwards...
# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:8000
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

import io
import logging
import socketserver
from http import server
from threading import Condition




from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import controls
from libcamera import Transform


PAGE = """\
<!DOCTYPE html>
<html>
<head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>
    <style>
        body { 
            background-color: #161819; 
            color: white; 
            overflow: hidden; /* Disable scrolling */ 
            margin: 0; /* Remove default margin */
            font-family: Arial, sans-serif; /* Set font family */
            position: relative; /* Add relative positioning to body */
        }
        #container {
            width: 100%; 
            height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center;
            flex-direction: column; /* Center items vertically */
            position: relative; /* Add relative positioning to container */
        }
        #header {
            text-align: center; /* Center header */
            position: absolute; /* Position header absolutely */
            bottom: 10px; /* Adjust bottom position */
            left: 10px; /* Adjust left position */
            z-index: 2; /* Ensure header appears on top of the image */
            padding: 5px 10px; /* Add padding */
            background-color: rgba(0, 0, 0, 0.5); /* Add background color with opacity */
            border: 1px solid transparent; /* Add transparent border */
            border-radius: 5px; /* Add border radius */
            max-width: calc(100% - 20px); /* Ensure header doesn't exceed container width */
        }
        #stream {
            max-width: 100%; 
            max-height: calc(100% - 30px); /* Adjust maximum height to accommodate the header */
            object-fit: contain;
            z-index: 1; /* Ensure image appears behind the header */
        }

        /* Media query for smaller screen devices */
        @media (max-width: 600px) {
            #header {
                font-size: 16px; /* Adjust font size */
                padding: 3px 8px; /* Adjust padding */
            }
        }
    </style>
    <title>Rail Vista</title>
</head>
<body>
    <div id="container">
        <img id="stream" />
        <div id="header">
            <h1>Rail Vista</h1>
        </div>
    </div>

    <script>
        // Dynamically set the image source
        var img = document.getElementById('stream');
        var streamUrl = "stream.mjpg"; // Update if needed
        img.src = streamUrl;
    </script>
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/stream':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()

picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
