"""
Provides functions for managing uploaded files.
"""

from os import makedirs, path

from werkzeug.datastructures import FileStorage

from . import paths


def add(storage: FileStorage) -> str:
    """Save a file uploaded via web form using its checksum as filename
    unless a file with identical name already exists.
    Returns the new name of the file."""
    from hashlib import sha256

    data = storage.read()
    filename = sha256(data).hexdigest()
    filepath = path.join(paths.UPLOADS, filename)

    if not path.exists(filepath):
        makedirs(paths.UPLOADS, exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(data)
    return filename