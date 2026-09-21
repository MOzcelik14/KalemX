"""Raster tests for actual transparent erasure and geometry rendering."""
import unittest

from kalemx.model import Document, Stroke

try:
    from kalemx.render import surface
except ImportError:
    surface = None


def alpha(image, x, y):
    offset = y * image.get_stride() + x * 4 + 3
    return image.get_data()[offset]


@unittest.skipIf(surface is None, "Requires distro python3-cairo")
class RenderTests(unittest.TestCase):
    def test_eraser_clears_alpha_not_white(self):
        doc = Document()
        doc.add(Stroke("pen", "#ff0000", 14, ((20, 50), (80, 50))))
        doc.add(Stroke("eraser", "#ffffff", 18, ((50, 10), (50, 90))))
        canvas = surface(doc, 100, 100)
        self.assertGreater(alpha(canvas, 30, 50), 0)
        self.assertEqual(alpha(canvas, 50, 50), 0)
        self.assertEqual(alpha(canvas, 10, 10), 0)

    def test_all_shapes_render(self):
        for tool in ("pen", "highlighter", "eraser", "line",
                     "arrow", "rectangle", "ellipse"):
            with self.subTest(tool=tool):
                doc = Document()
                doc.add(Stroke(tool, "#123456", 3,
                               ((10, 10), (55, 55))))
                canvas = surface(doc, 64, 64)
                self.assertEqual(canvas.get_width(), 64)
                self.assertEqual(canvas.get_height(), 64)

    def test_invalid_canvas_rejected(self):
        with self.assertRaises(ValueError):
            surface(Document(), 0, 20)
        with self.assertRaises(ValueError):
            surface(Document(), 100001, 100001)


if __name__ == "__main__":
    unittest.main()
