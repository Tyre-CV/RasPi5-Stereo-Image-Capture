# RasPi5-Stereo-Image-Capture
On RasPi create the venv with `--system-site-packages` to ensure picamera2 is available

Killing capture streams:
```
pkill rpicam-hello
```
```
pkill libcamera
```

Preview Video-Feed:
```
rpicam-hello -t 0 --camera 0
```
```
rpicam-hello -t 0 --camera 1
```
