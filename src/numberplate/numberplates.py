import re
import json
from pathlib import Path

class Numberplate:
    def __init__(self, data_file=None):
        if data_file is None:
            # Get the project root assuming this file is in src/
            project_root = Path(__file__).parent.parent.parent
            self.data_file = project_root / "data" / "numberplates.json"
        else:
            self.data_file = Path(data_file)

        self.plates = self._load_numberplates()

    def _load_numberplates(self):
        if self.data_file.exists():
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {}

    def _save_numberplates(self):
        with open(self.data_file, "w") as f:
            json.dump(self.plates, f, indent=2)

    def validate(self, numberplate: str):
        pattern = r"^[A-Z]{1,3}-[A-Z]{1,2}-\d{1,4}$"
        return bool(re.match(pattern, numberplate))

    def is_full(self, numberplate):
        return self.plates.get(numberplate, 0) >= 4

    def add(self, numberplate):
        if not self.is_full(numberplate):
            self.plates[numberplate] = self.plates.get(numberplate, 0) + 1
            self._save_numberplates()
            return True
        return False