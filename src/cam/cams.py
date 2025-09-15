import uuid
from picamera2 import Picamera2, Preview
import time
import os
from libcamera import controls
from pathlib import Path
from utils.decorators import singleton
import sys
import json



@singleton
class StereoCamera:
    ROOT_DIR = Path(sys.prefix).parent
    IMAGE_PATH = "./data/images"
    CONFIG_PATH = "./data/cam_configs"

    CONTROLS = {
            'Sharpness': float,
            'NoiseReductionMode': int,
            'Contrast': float,
            'AnalogueGain': float,
            'ExposureTime': int
        }

    current_controls = {}
    current_config = None

    def __init__(self):
        """
        Initialize the stereo camera setup with two Picamera2 instances:
        - right_cam for the right camera (index 0)
        - left_cam for the left camera (index 1)

        Configures and starts both cameras using default preview configurations.
        """
        # Kill all existing camera instances
        try:
            Picamera2.close_all()
        except Exception as e:
            print(f"Error closing existing cameras: {e}")

        self.right_cam = Picamera2(0)
        self.left_cam = Picamera2(1)

        self.last_captured = [None, None]  # Store last captured images for potential delete


        # Configure the cameras
        # preview_config = picam2.create_preview_configuration()
        # capture_config = picam2.create_still_configuration()
        self.right_config = self.right_cam.create_still_configuration()
        self.left_config = self.left_cam.create_still_configuration()
        # print(right_config)

        self.right_cam.configure(self.right_config)
        self.left_cam.configure(self.left_config)

        # Start the cam
        # self.right_cam.start()
        # self.left_cam.start()

        # Focus has to be set manulally for each camera

    def start_cameras(self):
        """
        Start both the right and left cameras.
        """
        self.right_cam.start()
        self.left_cam.start()

    def stop_cameras(self):
        """
        Stop both the right and left cameras.
        """
        self.right_cam.stop()
        self.left_cam.stop()


    def adjust_config(self, controls_dict={}):
        """
        Adjust camera configuration controls for both cameras.
        Casts values to the correct type as defined in CONTROLS.
        Args:
            controls_dict (dict): Dictionary of control names and their values.
        """
        for control, value in controls_dict.items():
            if control in self.CONTROLS:
                try:
                    controls_dict[control] = self.CONTROLS[control](value)
                except ValueError as e:
                    print(f"Error converting {control} to {self.CONTROLS[control]}: {e}")
                    continue
        self.current_controls = controls_dict
        self.right_cam.set_controls(self.current_controls)
        self.left_cam.set_controls(self.current_controls)

    def get_cam_dims(self):
        """
        Get the dimensions of the left and right camera images.
        Returns:
            dict: Dictionary with 'left' and 'right' keys and their image sizes.
        """
        return dict(
            left=self.left_config['main']['size'],
            right=self.right_config['main']['size']
        )

    def get_camera_options(self):
        """
        Get min, max, and default values for camera controls.
        Returns:
            dict: Dictionary of control options for each control in CONTROLS.
        """
        return {
            control: {
                'min': self.left_cam.camera_controls[control][0],
                'max': self.left_cam.camera_controls[control][1],
                'default': self.left_cam.camera_controls[control][2]
            } for control in self.CONTROLS.keys() if control in self.left_cam.camera_controls
        }

    def get_control_controls(self):
        """
        Get all available camera controls for both left and right cameras.
        Returns:
            dict: Dictionary with 'left_cam' and 'right_cam' keys and their controls.
        """
        return dict(
            left_cam=self.left_cam.camera_controls,
            right_cam=self.right_cam.camera_controls
        )

    def can_delete_last_images(self):
        """
        Check if the last captured images can be deleted.
        Returns:
            bool: True if both last captured images exist, False otherwise.
        """
        if self.last_captured[0] is None or self.last_captured[1] is None:
            return False
        return True

    def delete_last_images(self, numberplate):
        """
        Delete the last captured images from both cameras.
        This method assumes that the last captured images are stored in self.last_captured.
        """
        if not self.can_delete_last_images():
            return False

        try:
            # Try to remove the files
            os.remove(self.last_captured[0])
            os.remove(self.last_captured[1])
            # Adjust numberplate count
            numberplate.remove()
            # Clear History
            self.last_captured = [None, None]
            return True
        except Exception as e:
            print(f"Error deleting images: {e}")
            return False

    def get_preview(self):
        """
        Capture and return frames from both left and right cameras.
        Returns:
            tuple: (left_frame, right_frame), both as PIL images.
        """
        self.start_cameras()

        left_frame = self.left_cam.capture_image()
        right_frame = self.right_cam.capture_image()

        self.stop_cameras()
        
        return left_frame, right_frame
    

    def capture_images(self, label, numberplate):
        """
        Capture images from both cameras and save them with a unique filename.
        Args:
            label (str): Label to include in the filename.
            numberplate: Numberplate object to update image count/history.
        Returns:
            list: List of file paths to the last captured images, or None if not captured.
        """
        self.start_cameras()

        images_dir = os.path.join(self.ROOT_DIR, self.IMAGE_PATH)
        unique_id = str(uuid.uuid4())

        left_filename = f"{unique_id}_{label}_L.png"
        right_filename = f"{unique_id}_{label}_R.png"

        left_path = os.path.join(images_dir, left_filename)
        right_path = os.path.join(images_dir, right_filename)

        if not numberplate.full:
            # Numberplates
            numberplate.add()
            # Image-History
            self.last_captured = [left_path, right_path]


            # Capture images
            self.left_cam.capture_file(left_path)
            self.right_cam.capture_file(right_path)

            self.stop_cameras()

            return self.last_captured
        
        self.stop_cameras()



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


    def save_cam_config(self, name=str(uuid.uuid4())[:8]):
        """
        Save the current camera controls to a configuration file.
        Args:
            name (str): Name to use for the config file (default: random uuid).
        """
        settings_file = os.path.join(self.ROOT_DIR, self.CONFIG_PATH, f'camera_settings_{name}.json')
        with open(settings_file, 'w') as f:
            json.dump(self.current_controls, f, indent=4)

    def get_saved_configs(self):
        """
        Get all saved camera configuration files in the config directory.
        Returns:
            list: List of config filenames.
        """
        config_dir = os.path.join(self.ROOT_DIR, self.CONFIG_PATH)
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]

        return config_files

    def load_config(self, config_name):
        """
        Load a camera configuration from a file and apply it to both cameras.
        Args:
            config_name (str): Name of the config file to load.
        Returns:
            dict: The loaded configuration data.
        Raises:
            FileNotFoundError: If the config file does not exist.
        """
        config_dir = os.path.join(self.ROOT_DIR, self.CONFIG_PATH)
        config_file = os.path.join(config_dir, config_name)
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file {config_name} does not exist.")
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        self.adjust_config(config_data)
        self.current_config = config_name
        return config_data

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
