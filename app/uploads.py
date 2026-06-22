"""
Provides functions for managing uploaded files.
"""

from os import makedirs, path

from werkzeug.datastructures import FileStorage

from . import const, paths


def add(storage: FileStorage, *args: str) -> str:
    """Save a file uploaded via web form using any additional
    arguments and the file's checksum to create a filename.
    Skip saving if a file with identical name already exists.
    Returns the new name of the file."""

    from mimetypes import guess_extension
    import magic

    data = storage.read()

    if args:
        from zlib import crc32
        from re import sub

        filename_parts = (
            *(sub(const.form.FILE_CHAR_REMOVE_PATTERN, '', arg) for arg in args),
            hex(crc32(data))[2:]
        )
        filename = '.'.join(filename_parts)
    else:
        from hashlib import sha256
        filename = sha256(data).hexdigest()
    extension = guess_extension(magic.from_buffer(data, mime=True))
    if  extension:
        filename = filename + extension
    filepath = path.join(paths.UPLOADS, filename)

    if not path.exists(filepath):
        makedirs(paths.UPLOADS, exist_ok=True)
        with open(filepath, 'wb') as file:
            file.write(data)
    return filename