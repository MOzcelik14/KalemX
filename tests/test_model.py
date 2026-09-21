"""Run with python3 -m unittest discover -s tests -v."""
import json
import tempfile
from pathlib import Path
import unittest

from kalemx.model import Document, Stroke


def sample(tool="pen", x=2):
    return Stroke(tool, "#12abEF", 4, ((1, 2), (x, 3)))


class DocumentTests(unittest.TestCase):
    def test_undo_redo_and_new_action(self):
        doc = Document()
        doc.add(sample())
        doc.add(sample("arrow"))
        self.assertEqual(len(doc.strokes), 2)
        self.assertTrue(doc.undo())
        self.assertEqual(len(doc.strokes), 1)
        self.assertTrue(doc.redo())
        self.assertEqual(len(doc.strokes), 2)
        doc.undo()
        doc.add(sample("eraser"))
        self.assertFalse(doc.redo())

    def test_clear_is_one_undo_action(self):
        doc = Document()
        doc.add(sample())
        doc.add(sample("ellipse"))
        doc.clear()
        self.assertFalse(doc.strokes)
        doc.undo()
        self.assertEqual(len(doc.strokes), 2)
        doc.redo()
        self.assertFalse(doc.strokes)

    def test_project_roundtrip(self):
        doc = Document()
        for tool in ("pen", "highlighter", "eraser", "line",
                     "rectangle", "ellipse", "arrow"):
            doc.add(sample(tool))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "drawing.kalemx"
            doc.save(path)
            loaded = Document.load(path)
        self.assertEqual(loaded.to_dict(), doc.to_dict())
        self.assertFalse(loaded.undo())

    def test_invalid_projects_rejected(self):
        doc = Document()
        value = doc.to_dict()
        value["version"] = 2
        with self.assertRaises(ValueError):
            Document.from_dict(value)
        value["version"] = 1
        value["strokes"] = [{"tool": "rm -rf", "color": "#ffffff",
                             "width": 4, "points": [[1, 2]]}]
        with self.assertRaises(ValueError):
            Document.from_dict(value)
        value["strokes"][0]["tool"] = "pen"
        value["strokes"][0]["points"] = [[float("nan"), 2]]
        with self.assertRaises(ValueError):
            Document.from_dict(value)

    def test_invalid_stroke_rejected(self):
        for color, width, points in [
            ("white", 4, ((1, 2),)),
            ("#ffffff", -1, ((1, 2),)),
            ("#ffffff", 4, ((1, "2"),)),
            ("#ffffff", 4, ()),
        ]:
            with self.assertRaises(ValueError):
                Stroke("pen", color, width, points)


if __name__ == "__main__":
    unittest.main()
