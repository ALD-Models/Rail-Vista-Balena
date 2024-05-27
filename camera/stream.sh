#!/bin/bash

# Reload udev rules
udevadm control --reload

# List available cameras
libcamera-hello --list-cameras -n -v

# Get the local IP address
local_ip=$(hostname -I | awk '{print $1}')

# Define the port
PORT=90

# Log the server listening port and browser address to the console
echo "Server listening on port ${PORT}"
echo "You can view the stream at http://${local_ip}:${PORT}/stream"

while true; do
    # Start streaming from the camera using libcamera and pipe the output to FFmpeg
    libcamera-vid --output=pipe:0 --raw --codec=mjpeg --nopreview --timeout 0 --frames 0 | \
    ffmpeg -hide_banner -i pipe:0 -c:v copy -f mjpeg -q:v 5 -r 30 -s 640x480 -bufsize 1024k \
      -vf fps=10 -listen 1 -f mjpeg "http://0.0.0.0:${PORT}/stream" >/dev/null 2>&1
done
