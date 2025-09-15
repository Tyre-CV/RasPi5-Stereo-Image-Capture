import os
from pathlib import Path
import re
import json
import sys

from utils.decorators import singleton

@singleton
class Numberplate:
    """
    Class to manage numberplate entries and their counts.
    Handles loading, saving, validating, and updating numberplate data.
    """
    ROOT_DIR = Path(sys.prefix).parent 
    NUMBERPLATE_PATH = "./data/numberplates.json"
    
    def __init__(self):
        """
        Initialize Numberplate manager by loading existing numberplates.
        Sets up internal state for current numberplate and full status.
        """
        self.plates = self._load_numberplates()

        self._numberplate = ""
        self.full = False

    def _load_numberplates(self):
        """
        Load numberplates from the JSON file.
        Returns:
            dict: Dictionary of numberplates and their counts.
        """
        with open(os.path.join(self.ROOT_DIR, self.NUMBERPLATE_PATH), "r") as f:
            return json.load(f)
    
    @property
    def numberplate(self):
        """
        Get the current numberplate string.
        Returns:
            str: The current numberplate.
        """
        return self._numberplate

    @numberplate.setter
    def numberplate(self, value):
        """
        Set the current numberplate string, validate it, and check if full.
        Args:
            value (str): The numberplate string to set.
        Raises:
            ValueError: If value is not a string.
        """
        if not isinstance(value, str):
            raise ValueError("Numberplate must be a string.")
        self._numberplate = value.strip().upper()
        self.validate()
        self.check_if_full()

    def _save_numberplates(self):
        """
        Save the current numberplates dictionary to the JSON file.
        """
        with open(os.path.join(self.ROOT_DIR, self.NUMBERPLATE_PATH), "w") as f:
            json.dump(self.plates, f, indent=2)

    def validate(self):
        """
        Validate the current numberplate format.
        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r"^[A-Z]{1,3}-[A-Z]{1,2}-\d{1,4}$"
        return bool(re.match(pattern, self.numberplate))

    def check_if_full(self):
        """
        Check if the current numberplate has reached the maximum allowed count (4).
        Sets the 'full' attribute accordingly.
        """
        self.full = self.plates.get(self.numberplate, 0) >= 4


    def add(self):
        """
        Add an occurrence to the current numberplate, if not full.
        Updates the JSON file and full status.
        Returns:
            bool: True if added, False if already full.
        """
        if not self.full:
            self.plates[self.numberplate] = self.plates.get(self.numberplate, 0) + 1
            self._save_numberplates()
            self.check_if_full()
            return True
        return False

    def remove(self):
        """
        Remove an occurrence from the current numberplate.
        Updates the JSON file and full status.
        """
        self.plates[self.numberplate] -= 1
        self._save_numberplates()
        self.check_if_full()