import hashlib
import struct
import zlib

BOOK_COVER_COLORS = [
    (45, 45, 80),
    (80, 45, 45),
    (45, 80, 45),
    (80, 80, 45),
    (45, 80, 80),
    (80, 45, 80),
    (60, 90, 120),
    (120, 60, 90),
    (90, 120, 60),
    (100, 70, 50),
    (50, 100, 70),
    (70, 50, 100),
]


def make_cover_png(book_id, width=200, height=300):
    rgb = BOOK_COVER_COLORS[int(book_id) % len(BOOK_COVER_COLORS)]

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    row = bytes(rgb) * width
    raw = b"".join(b"\x00" + row for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def cover_md5(book_id):
    return hashlib.md5(make_cover_png(book_id)).hexdigest()
