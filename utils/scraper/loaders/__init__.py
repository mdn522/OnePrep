# from . import collegeboard, princetonreview, satmocks
from typing import List

from django.conf import settings

from programs.models import Program

from pathlib import Path


# Abstract loader from file
class Loader:
    program = 'sat'

    module_title = {
        'en': 'English',
        'math': 'Math',
    }

    def get_program(self):
        program = Program.objects.get(name__iexact=self.program)
        return program

    @staticmethod
    def get_file_list(path, glob, base_path: Path = settings.Q_LOADER_BASE_PATH) -> List[Path]:
        data_path = (base_path / path) if base_path else Path('') / 'data' / 'sat' / path

        files = list(data_path.glob(glob))
        return files

    @staticmethod
    def get_file(path, file, base_path = settings.Q_LOADER_BASE_PATH) -> Path:
        data_path = base_path if base_path else Path('') / 'data' / 'sat'
        return data_path / path / file

    def load(self):
        raise NotImplementedError


# registry = {
#     'collegeboard': collegeboard_org
# }
