"""Dependency-free drawing document and project format.

Rendering is deliberately separate, so history and file validation can be
tested without a graphical session or native GTK packages.
"""
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re

FORMAT_VERSION = 1
TOOLS = frozenset(("pen", "highlighter", "eraser", "line", "rectangle", "ellipse", "arrow"))
_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_STROKES = 20_000
MAX_POINTS = 100_000


def _point(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("Nokta [x, y] biçiminde olmalı.")
    if any(isinstance(n, bool) or not isinstance(n, (int, float)) or
           not math.isfinite(n) or abs(n) > 1_000_000 for n in value):
        raise ValueError("Geçersiz koordinat.")
    return (float(value[0]), float(value[1]))


@dataclass(frozen=True)
class Stroke:
    tool: str
    color: str
    width: float
    points: tuple

    def __post_init__(self):
        if self.tool not in TOOLS:
            raise ValueError("Bilinmeyen araç: " + str(self.tool))
        if not isinstance(self.color, str) or not _COLOR.fullmatch(self.color):
            raise ValueError("Renk #RRGGBB biçiminde olmalı.")
        if (isinstance(self.width, bool) or
                not isinstance(self.width, (int, float)) or
                not math.isfinite(self.width) or not 0.5 <= self.width <= 64):
            raise ValueError("Kalınlık 0.5 ile 64 arasında olmalı.")
        if not self.points or len(self.points) > MAX_POINTS:
            raise ValueError("Nokta sayısı geçersiz.")
        object.__setattr__(self, "points", tuple(_point(p) for p in self.points))

    def as_dict(self):
        return {
            "tool": self.tool, "color": self.color, "width": self.width,
            "points": [list(p) for p in self.points],
        }

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict):
            raise ValueError("Çizgi nesnesi geçersiz.")
        return cls(value.get("tool"), value.get("color"),
                   value.get("width"), value.get("points", ()))


class Document:
    def __init__(self):
        self.strokes = []
        self._undo = []
        self._redo = []

    def add(self, stroke):
        if not isinstance(stroke, Stroke):
            raise TypeError("Stroke bekleniyor.")
        if len(self.strokes) >= MAX_STROKES:
            raise ValueError("Çizim sınırına ulaşıldı.")
        self.strokes.append(stroke)
        self._undo.append(("add", stroke))
        self._redo.clear()

    def clear(self):
        if self.strokes:
            before = tuple(self.strokes)
            self.strokes.clear()
            self._undo.append(("clear", before))
            self._redo.clear()

    def undo(self):
        if not self._undo:
            return False
        action, data = self._undo.pop()
        if action == "add":
            self.strokes.pop()
        else:
            self.strokes.extend(data)
        self._redo.append((action, data))
        return True

    def redo(self):
        if not self._redo:
            return False
        action, data = self._redo.pop()
        if action == "add":
            self.strokes.append(data)
        else:
            self.strokes.clear()
        self._undo.append((action, data))
        return True

    def to_dict(self):
        return {
            "format": "KalemX", "version": FORMAT_VERSION,
            "strokes": [s.as_dict() for s in self.strokes],
        }

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or value.get("format") != "KalemX":
            raise ValueError("Bu dosya KalemX projesi değil.")
        if value.get("version") != FORMAT_VERSION:
            raise ValueError("Desteklenmeyen KalemX proje sürümü.")
        entries = value.get("strokes")
        if not isinstance(entries, list) or len(entries) > MAX_STROKES:
            raise ValueError("Çizgi sayısı geçersiz.")
        document = cls()
        document.strokes = [Stroke.from_dict(entry) for entry in entries]
        return document

    def save(self, path):
        # Store all floats as ordinary JSON numbers and always use UTF-8.
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path):
        # Defensive bound on imported project files.
        path = Path(path)
        if path.stat().st_size > 30_000_000:
            raise ValueError("Proje dosyası 30 MB sınırını aşıyor.")
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
