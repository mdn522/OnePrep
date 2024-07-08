# from . import collegeboard, princetonreview, satmocks
from typing import List

from programs.models import Program

from pathlib import Path


# Abstract loader from file
class Loader:
    def get_program(self):
        program = Program.objects.get(name__iexact=self.program)
        return program

    @staticmethod
    def get_file_list(path, glob, base_path: Path = None) -> List[Path]:
        data_path = (base_path / path) if base_path else Path('') / 'data' / 'sat' / path

        files = list(data_path.glob(glob))
        return files

    @staticmethod
    def get_file(path, file, base_path=None) -> Path:
        data_path = base_path if base_path else Path('') / 'data' / 'sat'
        return data_path / path / file

    def load(self):
        raise NotImplementedError


# registry = {
#     'collegeboard': collegeboard_org
# }
