from picamera2 import Picamera2, Preview
import time

from utils.decorators import singleton


@singleton
class StereoCamera:
    def __init__(self):
        self.right_cam = Picamera2(0)
        self.left_cam = Picamera2(1)

        # Configure the cameras
        right_config = self.right_cam.create_video_configuration()
        left_config = self.left_cam.create_video_configuration()

        self.right_cam.configure(right_config)
        self.left_cam.configure(left_config)

        # Start the cam
        self.right_cam.start()
        self.left_cam.start()   

    def get_frames(self):
        left_frame = self.left_cam.capture_array()
        right_frame = self.right_cam.capture_array()
        return left_frame, right_frame

    def capture_images(self, left_path="left.jpg", right_path="right.jpg"):
        self.left_cam.capture_file(left_path)
        self.right_cam.capture_file(right_path)

    def stop(self):
        self.left_cam.stop()
        self.right_cam.stop()

    def close(self):
        """
        Fully release the cameras.
        After calling this, you can create a fresh StereoCamera()
        """
        # stop if needed
        try:
            self.left_cam.stop()
            self.right_cam.stop()
        except Exception:
            pass

        # close handles
        try:
            self.left_cam.close()
            self.right_cam.close()
        except Exception:
            pass

        # remove from singleton cache so next .StereoCamera() is fresh
        from utils.decorators import _instances  # adjust name to however your decorator stores instances
        _instances.pop(self.__class__, None)

    def __del__(self):
        # last-ditch cleanup
        self.close()


if __name__ == "__main__":
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

    left_cam.close()
    right_cam.close()
