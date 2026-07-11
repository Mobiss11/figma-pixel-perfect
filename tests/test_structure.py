"""Проверки структуры скилла figma-pixel-perfect.

Запуск: pytest figma-pixel-perfect/tests/
"""

from __future__ import annotations

import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_PATH = SKILL_DIR / "SKILL.md"


def test_skill_md_exists():
    assert SKILL_PATH.exists(), "SKILL.md должен лежать в корне папки скилла"


def test_frontmatter_valid():
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert content.startswith("---\n"), "SKILL.md должен начинаться с frontmatter"
    head = content[:800]
    assert "\nname:" in head, "В frontmatter должно быть поле name"
    assert "\ndescription:" in head, "В frontmatter должно быть поле description"


def test_name_matches_folder():
    content = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^name:\s*(\S+)", content, re.MULTILINE)
    assert m, "Поле name не найдено"
    assert m.group(1) == SKILL_DIR.name, "name должен совпадать с именем папки"


def test_description_length():
    content = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    assert m and len(m.group(1)) >= 30, "description короче 30 символов"


def test_bundled_files_exist():
    assert (SKILL_DIR / "scripts" / "pixel_diff.py").exists()
    assert (SKILL_DIR / "references" / "mcp-tools.md").exists()


def test_skill_references_resolve():
    """Все относительные markdown-ссылки из SKILL.md указывают на живые файлы."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    for target in re.findall(r"\]\((?!http)([^)#]+)\)", content):
        assert (SKILL_DIR / target).exists(), f"Битая ссылка в SKILL.md: {target}"
