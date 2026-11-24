#!/usr/bin/env python3
"""Deliver the 23 November 2026 news poster for this make.fun entry.

The repository keeps the finished poster in ``entry.png`` beside this
file.  When the grader runs the program, it streams that picture into
``entry.png`` inside the output directory (``$MAKEFUN_OUTPUT_DIR``
when set, otherwise ``/output``) and then proves the delivered bytes
are the stored bytes: the picture's opening bytes are checked before
the copy starts, and the SHA-256 of the written file must equal the
SHA-256 of the stored one.  Everything runs offline on the standard
library alone, and the output never changes between runs.
"""

import hashlib
import os
import sys
from pathlib import Path

# A PNG opens with this fixed eight-byte signature; a JPEG opens with
# the start-of-image marker followed by a third 0xFF byte.  The poster
# bundled here is a JPEG, but the entry file is named entry.png either
# way, so both openings are accepted.
OPENINGS = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")
BLOCK = 32 * 1024


def poster_path() -> Path:
    """The picture stored in the repository, next to this program."""
    return Path(__file__).parent.resolve() / "entry.png"


def opens_like_image(path: Path) -> bool:
    """True when the file starts with a PNG or JPEG opening."""
    with open(path, "rb") as handle:
        head = handle.read(8)
    return any(head.startswith(opening) for opening in OPENINGS)


def sha256_of(path: Path) -> str:
    """Hex SHA-256 of a file, fed to the hasher one block at a time."""
    total = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(BLOCK), b""):
            total.update(block)
    return total.hexdigest()


def deliver(source: Path, target: Path) -> int:
    """Stream the poster to a staging file beside the target.

    The copy lands in ``<target>.part`` first and is only moved over
    the target once it is complete, so an interrupted run never leaves
    a half-written entry.png behind.  Returns the bytes copied.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + ".part")
    copied = 0
    with open(source, "rb") as fin, open(staging, "wb") as fout:
        for block in iter(lambda: fin.read(BLOCK), b""):
            fout.write(block)
            copied += len(block)
    os.replace(staging, target)
    return copied


def run() -> int:
    source = poster_path()
    if not opens_like_image(source):
        print(f"refusing to deliver {source}: not a PNG or JPEG", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target = out_dir / "entry.png"
    copied = deliver(source, target)
    if copied != source.stat().st_size:
        print("delivered file is shorter or longer than the stored poster", file=sys.stderr)
        return 1
    if sha256_of(target) != sha256_of(source):
        print("delivered file does not match the stored poster", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
