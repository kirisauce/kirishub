#!/usr/bin/env python3
"""Extract the largest PNG-compressed frame of an ICO file inside a zip archive."""

import struct
import sys
import zipfile


def ico_frames(ico):
    count = struct.unpack_from('<H', ico, 4)[0]
    for index in range(count):
        entry = 6 + index * 16
        width, height, _, _, _, _, size, offset = struct.unpack_from('<BBBBHHII', ico, entry)
        # A zero dimension encodes 256 pixels in the ICO header.
        yield width or 256, ico[offset:offset + size]


def main():
    archive, destination = sys.argv[1:3]
    with zipfile.ZipFile(archive) as zip_file:
        ico = zip_file.read('izpack/Programmer.ico')
    size, frame = max(
        (candidate for candidate in ico_frames(ico) if candidate[1].startswith(b'\x89PNG\r\n\x1a\n')),
        key=lambda candidate: candidate[0],
    )
    with open(destination, 'wb') as icon:
        icon.write(frame)
    print(f'{destination}: {size}x{size}, {len(frame)} bytes')


if __name__ == '__main__':
    main()
