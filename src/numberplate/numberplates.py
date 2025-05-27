import os
from pathlib import Path
import re
import json
import sys

from utils.decorators import singleton

@singleton
class Numberplate:
    ROOT_DIR = Path(sys.prefix).parent 
    NUMBERPLATE_PATH = "./data/numberplates.json"
    
    def __init__(self):
        self.plates = self._load_numberplates()

        self._numberplate = ""
        self.full = False

    def _load_numberplates(self):
        with open(os.path.join(self.ROOT_DIR, self.NUMBERPLATE_PATH), "r") as f:
            return json.load(f)
    
    @property
    def numberplate(self):
        return self._numberplate

    @numberplate.setter
    def numberplate(self, value):
        if not isinstance(value, str):
            raise ValueError("Numberplate must be a string.")
        self._numberplate = value.strip().upper()
        self.validate()
        self.check_if_full()

    def _save_numberplates(self):
        with open(os.path.join(self.ROOT_DIR, self.NUMBERPLATE_PATH), "w") as f:
            json.dump(self.plates, f, indent=2)

    def validate(self):
        pattern = r"^[A-Z]{1,3}-[A-Z]{1,2}-\d{1,4}$"
        return bool(re.match(pattern, self.numberplate))

    def check_if_full(self):
        self.full = self.plates.get(self.numberplate, 0) >= 4


    def add(self):
        if not self.full:
            self.plates[self.numberplate] = self.plates.get(self.numberplate, 0) + 1
            self._save_numberplates()
            self.check_if_full()
            return True
        return False

    def remove(self):
        self.plates[self.numberplate] -= 1
        self._save_numberplates()
        self.check_if_full()