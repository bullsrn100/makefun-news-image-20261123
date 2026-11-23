"""make.fun entry: news-image-20261123.

Writes the bundled news-summary image to /output/entry.png.

The image is stored in this repository as entry.png; the program
copies it byte for byte, so every run produces identical output.
No network access is used. The bundled file is a JPEG (the rules
allow PNG or JPEG under the name entry.png), so the program checks
for the JPEG start marker before copying.

Revision 1: validate that the bundled file really is a JPEG or PNG
image before copying, and copy in chunks while counting the bytes,
so a truncated copy is detected instead of silently accepted.

Revision 2: after copying, verify the output's SHA-256 digest
against the source image, so any corruption in the written file
fails the run instead of producing a silently wrong entry.
"""

import hashlib
import os
from pathlib import Path

JPEG_START = b"\xff\xd8\xff"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHUNK_SIZE = 64 * 1024


def bundled_image() -> Path:
    """Return the path of the image stored next to this program."""
    return Path(__file__).resolve().with_name("entry.png")


def check_image(path: Path) -> int:
    """Return the file size, raising ValueError if it is not a PNG or JPEG."""
    with path.open("rb") as fh:
        header = fh.read(len(PNG_SIGNATURE))
    if not (header.startswith(JPEG_START) or header == PNG_SIGNATURE):
        raise ValueError(f"{path} is not a PNG or JPEG image")
    return path.stat().st_size


def copy_image(src: Path, dst: Path) -> int:
    """Copy src to dst in chunks; return the number of bytes written."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with src.open("rb") as fin, dst.open("wb") as fout:
        while chunk := fin.read(CHUNK_SIZE):
            fout.write(chunk)
            written += len(chunk)
    return written


def digest(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, read in chunks."""
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    src = bundled_image()
    expected = check_image(src)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dst = out_dir / "entry.png"
    written = copy_image(src, dst)
    if written != expected:
        raise ValueError(f"copied {written} bytes, expected {expected}")
    if digest(dst) != digest(src):
        raise ValueError("output digest does not match the bundled image")


if __name__ == "__main__":
    main()
