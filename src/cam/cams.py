from picamera2 import Picamera2, Preview
import time
import os
from libcamera import controls

from utils.decorators import singleton


@singleton
class StereoCamera:
    def __init__(self):
        """
        Initialize the stereo camera setup with two Picamera2 instances:
        - right_cam for the right camera (index 0)
        - left_cam for the left camera (index 1)

        Configures and starts both cameras using default preview configurations.
        """
        self.right_cam = Picamera2(0)
        self.left_cam = Picamera2(1)

        # Configure the cameras
        right_config = self.right_cam.create_preview_configuration()
        left_config = self.left_cam.create_preview_configuration()

        self.right_cam.configure(right_config)
        self.left_cam.configure(left_config)

        # Start the cam
        self.right_cam.start()
        self.left_cam.start()  

        # Focus 
        # self.right_cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        # self.left_cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})



    def get_frames(self):
        """
        Capture and return frames from both left and right cameras.
        Returns:
            tuple: (left_frame, right_frame), both as PIL images.
        """
        left_frame = self.left_cam.capture_image()
        right_frame = self.right_cam.capture_image()
        return left_frame, right_frame

    def capture_images(self, left_path="left.jpg", right_path="right.jpg"):
        """
        Capture still images from both cameras and save them to the specified paths
        inside the 'images' folder located at the project root.
        :param left_name (str): Filename for the left camera image.
        .param right_name (str): Filename for the right camera image.
        """
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        images_dir = os.path.join(root_dir, "images")

        left_path = os.path.join(images_dir, left_path)
        right_path = os.path.join(images_dir, right_path)

        self.left_cam.capture_file(left_path)
        self.right_cam.capture_file(right_path)

    def stop(self):
        """
        Stop both camera streams without fully releasing the camera resources.
        """
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
