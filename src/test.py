from picamera2 import Picamera2, Preview
import time

right_cam = Picamera2(0)
left_cam  = Picamera2(1)

# Configure the cameras
right_camera_config = right_cam.create_preview_configuration()
right_cam.configure(right_camera_config)

left_camera_config = left_cam.create_preview_configuration()
left_cam.configure(left_camera_config)

# Start the cameras
right_cam.start()
left_cam.start()

# right_cam.start_preview(Preview.QTGL)
# left_cam.start_preview(Preview.QTGL)

# GUI preview
# picam2.start_preview(Preview.QTGL)
# Non-GUI preview
# picam2.start_preview(Preview.DRM)

time.sleep(2)

# Capture images
right_cam.capture_file("right_test.jpg")
left_cam.capture_file("left_test.jpg")

# Stop the cameras
right_cam.stop()
left_cam.stop()
