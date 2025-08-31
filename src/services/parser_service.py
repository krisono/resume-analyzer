from __future__ import annotations
from typing import Tuple
from ..utils.file_utils import read_file_content

def parse_file_to_text(file_storage) -> Tuple[str, str]:
    return read_file_content(file_storage)