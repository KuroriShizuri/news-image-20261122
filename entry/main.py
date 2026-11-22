# SPDX-License-Identifier: MIT
"""Copy the bundled front-page artwork to the output directory.

Reads entry.png from this script's own directory. The file is a JPEG
(the competition accepts a whole PNG or JPEG named entry.png) of
exactly 1024x1024 pixels and at most 1 MiB. Validates it (JPEG magic
bytes and dimensions read from the SOF marker), refuses it when it is
over the 1 MiB cap, copies it to $MAKEFUN_OUTPUT_DIR/entry.png
(/output by default) after checking the output directory is writable,
then re-validates the copy itself (magic bytes and dimensions) and
verifies it by file size and SHA-256 digest, printing the byte count
and digest.

Python 3.13, standard library only, no network.
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
JPEG_MAGIC = b"\xff\xd8\xff"
EXPECTED_SIZE = (1024, 1024)
MAX_ENTRY_BYTES = 1048576  # competition cap: the image must be at most 1 MiB


def read_dimensions(path):
    """Return (width, height) of the JPEG at path, after magic check."""
    with open(path, "rb") as fh:
        header = fh.read(3)
        if header != JPEG_MAGIC:
            raise ValueError("not a JPEG file: bad magic bytes")
        # Scan markers for a Start Of Frame segment (SOF0/SOF1/SOF2).
        while True:
            byte = fh.read(1)
            if not byte:
                raise ValueError("not a JPEG file: no SOF marker found")
            if byte != b"\xff":
                continue
            marker = fh.read(1)
            if marker in (b"\xd8", b"\xd9", b"\x01") or (
                b"\xd0" <= marker <= b"\xd7"
            ):
                continue
            length = struct.unpack(">H", fh.read(2))[0]
            if marker in (b"\xc0", b"\xc1", b"\xc2"):
                segment = fh.read(5)
                height, width = struct.unpack(">xHH", segment)
                return width, height
            fh.seek(length - 2, 1)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    width, height = read_dimensions(SOURCE)
    if (width, height) != EXPECTED_SIZE:
        raise ValueError(
            "entry.png must be 1024x1024, got %dx%d" % (width, height)
        )
    source_size = os.path.getsize(SOURCE)
    if source_size > MAX_ENTRY_BYTES:
        raise ValueError(
            "entry.png is %d bytes, over the 1 MiB (%d byte) competition cap"
            % (source_size, MAX_ENTRY_BYTES)
        )
    source_hash = sha256_of(SOURCE)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    if not os.path.isdir(out_dir) or not os.access(out_dir, os.W_OK):
        raise ValueError(
            "output directory %s is not a writable directory" % out_dir
        )
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)

    # Re-validate the copy itself: a truncated or corrupted write must
    # fail here, not pass on size/digest luck alone.
    dest_width, dest_height = read_dimensions(dest)
    if (dest_width, dest_height) != EXPECTED_SIZE:
        raise ValueError(
            "copied entry.png must be 1024x1024, got %dx%d"
            % (dest_width, dest_height)
        )

    dest_size = os.path.getsize(dest)
    dest_hash = sha256_of(dest)
    if dest_size != source_size or dest_hash != source_hash:
        raise ValueError("copy verification failed: size or SHA-256 mismatch")
    print("wrote %s (%d bytes, sha256 %s)" % (dest, dest_size, dest_hash))
    return 0


if __name__ == "__main__":
    sys.exit(main())
