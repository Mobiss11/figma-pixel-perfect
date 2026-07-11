"""Смоук-тест pixel_diff.py на синтетических картинках."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("PIL")
from PIL import Image, ImageDraw  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "pixel_diff.py"


def run(ref: Path, ren: Path, out: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(ref), str(ren), "--out", str(out)],
        capture_output=True, text=True,
    )


def test_identical_images_pass(tmp_path: Path):
    img = Image.new("RGB", (200, 100), (240, 240, 240))
    a, b, out = tmp_path / "a.png", tmp_path / "b.png", tmp_path / "d.png"
    img.save(a)
    img.save(b)
    res = run(a, b, out)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0.00%" in res.stdout
    assert out.exists()


def test_different_images_fail_and_localize(tmp_path: Path):
    ref = Image.new("RGB", (200, 200), (240, 240, 240))
    ren = ref.copy()
    # «Съехавший блок» в левом верхнем углу
    ImageDraw.Draw(ren).rectangle([0, 0, 60, 60], fill=(255, 0, 0))
    a, b, out = tmp_path / "a.png", tmp_path / "b.png", tmp_path / "d.png"
    ref.save(a)
    ren.save(b)
    res = run(a, b, out)
    assert res.returncode == 1
    assert "строка 1" in res.stdout and "колонка 1" in res.stdout


def test_retina_2x_render_is_normalized(tmp_path: Path):
    ref = Image.new("RGB", (100, 50), (10, 20, 30))
    ren = Image.new("RGB", (200, 100), (10, 20, 30))
    a, b, out = tmp_path / "a.png", tmp_path / "b.png", tmp_path / "d.png"
    ref.save(a)
    ren.save(b)
    res = run(a, b, out)
    assert res.returncode == 0
    assert "привожу" in res.stdout
