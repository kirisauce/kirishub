#!/usr/bin/env python3
"""Extract the payload archive embedded in the STM32CubeMX2 Linux installer.

The installer is a self-extracting ELF executable that carries its payload as a
gzip-compressed tar archive, with further installer data behind that archive. The
archive is located by content: every gzip header in the installer is tried until
one turns out to carry the payload marker. That archive is then unpacked as a
stream, so the data behind it is never mistaken for part of the archive.
"""

import sys
import tarfile
from collections.abc import Iterator

GZIP_MAGIC = b"\x1f\x8b\x08"
MAGIC_OVERLAP = len(GZIP_MAGIC) - 1
PAYLOAD_MARKER = "data/installation.json"
SCAN_CHUNK = 1 << 22
MARKER_SCAN_LIMIT = 32


def gzip_offsets(path: str) -> Iterator[int]:
    """Yield the offset of every gzip member header in path."""
    offset = 0
    tail = b""
    with open(path, "rb") as file:
        while chunk := file.read(SCAN_CHUNK):
            blob = tail + chunk
            found = blob.find(GZIP_MAGIC)
            while found != -1:
                yield offset - len(tail) + found
                found = blob.find(GZIP_MAGIC, found + 1)
            offset += len(chunk)
            tail = blob[-MAGIC_OVERLAP:]


def payload_offset(path: str) -> int | None:
    """Return the offset of the archive carrying the payload marker, or None."""
    for offset in gzip_offsets(path):
        try:
            with open(path, "rb") as file:
                file.seek(offset)
                with tarfile.open(fileobj=file, mode="r|gz") as archive:
                    for index, member in enumerate(archive):
                        if member.name == PAYLOAD_MARKER:
                            return offset
                        if index >= MARKER_SCAN_LIMIT:
                            break
        except (tarfile.TarError, OSError, EOFError):
            continue
    return None


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <installer> <destination-directory>")

    installer_path, destination = sys.argv[1], sys.argv[2]
    offset = payload_offset(installer_path)
    if offset is None:
        sys.exit(f"{installer_path}: no embedded archive containing {PAYLOAD_MARKER}")

    with open(installer_path, "rb") as file:
        file.seek(offset)
        with tarfile.open(fileobj=file, mode="r|gz") as payload:
            payload.extractall(destination, filter="data")
            entries = len(payload.members)

    print(f"extracted {entries} entries from {installer_path} (payload at offset {offset}) "
          f"to {destination}")


if __name__ == "__main__":
    main()
