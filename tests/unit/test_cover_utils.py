"""Юнит-тесты генератора обложек cover_utils.py."""
import struct

import cover_utils


def test_make_cover_png_has_png_signature():
    png = cover_utils.make_cover_png(1)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert png.endswith(b"IEND\xaeB`\x82")


def test_make_cover_png_default_size_is_200x300():
    png = cover_utils.make_cover_png(1)
    width, height = struct.unpack(">II", png[16:24])
    assert (width, height) == (200, 300)


def test_make_cover_png_custom_size():
    png = cover_utils.make_cover_png(3, width=20, height=30)
    assert struct.unpack(">II", png[16:24]) == (20, 30)


def test_cover_colors_repeat_every_12_books():
    assert cover_utils.make_cover_png(1) == cover_utils.make_cover_png(13)
    assert cover_utils.make_cover_png(1) != cover_utils.make_cover_png(2)


def test_cover_md5_matches_seed_data():
    """MD5 сгенерированной обложки совпадает с хешем из schemas/seed_data.sql."""
    assert cover_utils.cover_md5(1) == "296f5ff741ea2c3d25fd48f6e49b78de"
    assert cover_utils.cover_md5(2) == "10b7c67ff219ceec955affd8626f3749"
