"""KalemX desktop frontend: shared drawing engine, X11 and Wayland layers."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

import cairo
import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from . import __version__
from .model import Document, Stroke
from .render import surface

COLORS = ("#e53935", "#ffb300", "#43a047", "#1e88e5", "#8e24aa",
          "#ffffff", "#111111")
TOOL_LABELS = {
    "pen": "Kalem", "highlighter": "Fosfor",
    "eraser": "Silgi", "line": "Çizgi", "arrow": "Ok",
    "rectangle": "Dikdörtgen", "ellipse": "Elips",
}
STYLING = b"""
window.kalemx-toolbar { background-color: #20252e; }
.kalemx-toolbar button { background: #343c49; color: #f5f7fb;
  border: 1px solid #526074; border-radius: 7px; padding: 6px 10px; }
.kalemx-toolbar button:checked, .kalemx-toolbar button.suggested-action
  { background: #287d63; color: #ffffff; }
.kalemx-toolbar label { color: #f5f7fb; }
.kalemx-toolbar scale { min-width: 100px; }
"""


def unique_path(kind, extension):
    if kind == "image":
        folder = Path.home() / "Pictures"
    else:
        folder = Path.home() / "Documents"
    if not folder.is_dir():
        folder = Path.home()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return folder / ("kalemx-" + stamp + extension)


class Overlay(Gtk.Window):
    def __init__(self, monitor=None):
        super().__init__(title="KalemX canvas")
        self.is_wayland = monitor is not None
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_app_paintable(True)
        self.set_accept_focus(False)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is None:
            raise RuntimeError("Masaüstü şeffaf pencere (RGBA) sunmuyor.")
        self.set_visual(visual)
        if monitor is None:
            self.set_default_size(screen.get_width(), screen.get_height())
            self.move(0, 0)
        else:
            geo = monitor.get_geometry()
            self.set_default_size(geo.width, geo.height)
        self.document = Document()
        self.current = None
        self.tool = "pen"
        self.color = COLORS[0]
        self.width = 4.0
        self.drawing_enabled = True
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_press)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-release-event", self.on_release)

    def set_drawing_enabled(self, enabled):
        window = self.get_window()
        if window is None:
            raise RuntimeError("KalemX katmanı henüz hazırlanmadı.")
        self.current = None
        # GTK may overwrite directly-set GDK input shapes; use the widget API.
        self.input_shape_combine_region(None if enabled else cairo.Region())
        window.set_pass_through(not enabled)
        self.drawing_enabled = enabled
        self.queue_draw()
        print("KalemX:", "çizim modu" if enabled else "fare modu", flush=True)

    def on_press(self, _widget, event):
        if self.drawing_enabled and event.button == 1:
            self.current = {
                "tool": self.tool, "color": self.color, "width": self.width,
                "points": [(event.x, event.y)],
            }
            self.queue_draw()
        return bool(self.drawing_enabled)

    def on_motion(self, _widget, event):
        if (self.current is not None and
                event.state & Gdk.ModifierType.BUTTON1_MASK and
                len(self.current["points"]) < 100_000):
            self.current["points"].append((event.x, event.y))
            self.queue_draw()
        return bool(self.drawing_enabled)

    def on_release(self, _widget, event):
        if self.current is not None and event.button == 1:
            data = self.current
            self.current = None
            if len(data["points"]) < 100_000:
                data["points"].append((event.x, event.y))
            try:
                self.document.add(Stroke(
                    data["tool"], data["color"], data["width"],
                    tuple(data["points"])))
            except (ValueError, TypeError) as exc:
                print("KalemX: çizgi kaydedilemedi:", exc, file=sys.stderr)
            self.queue_draw()
        return bool(self.drawing_enabled)

    def on_draw(self, _widget, cr):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        if width <= 0 or height <= 0:
            return False
        preview = None
        if self.current:
            data = self.current
            preview = Stroke(data["tool"], data["color"],
                             data["width"], tuple(data["points"]))
        canvas = surface(self.document, width, height, preview)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(canvas, 0, 0)
        cr.paint()
        return False

    def undo(self):
        self.current = None
        if self.document.undo():
            self.queue_draw()

    def redo(self):
        self.current = None
        if self.document.redo():
            self.queue_draw()

    def clear(self):
        self.current = None
        self.document.clear()
        self.queue_draw()

    def export_png(self, path):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        canvas = surface(self.document, width, height)
        canvas.write_to_png(str(path))


class Toolbar(Gtk.Window):
    def __init__(self, overlay):
        super().__init__(title="KalemX")
        self.overlay = overlay
        if not overlay.is_wayland:
            self.set_transient_for(overlay)
        self.set_keep_above(True)
        self.set_resizable(False)
        self.set_border_width(9)
        self.connect("destroy", lambda *_: Gtk.main_quit())
        self.get_style_context().add_class("kalemx-toolbar")
        provider = Gtk.CssProvider()
        provider.load_from_data(STYLING)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        self.add(layout)
        head = Gtk.Box(spacing=8)
        layout.pack_start(head, False, False, 0)
        title = Gtk.Label()
        title.set_markup("<b>KalemX</b>  <small>" + __version__ + "</small>")
        head.pack_start(title, False, False, 3)
        self.mode_button = self.button(
            head, "↖ Fare moduna geç", self.toggle_mode)
        self.buttons = {}
        for group in (
            ("pen", "highlighter", "eraser", "line"),
            ("arrow", "rectangle", "ellipse"),
        ):
            row = Gtk.Box(spacing=5)
            layout.pack_start(row, False, False, 0)
            for tool in group:
                self.buttons[tool] = self.button(
                    row, TOOL_LABELS[tool],
                    lambda _b, t=tool: self.set_tool(t))
        colors = Gtk.Box(spacing=4)
        layout.pack_start(colors, False, False, 0)
        for color in COLORS:
            b = self.button(colors, "●",
                            lambda _b, c=color: self.choose_color(c))
            rgba = Gdk.RGBA()
            rgba.parse(color)
            b.override_color(Gtk.StateFlags.NORMAL, rgba)
            # Some themes ignore override_color, so attach a CSS class as well.
            b.set_tooltip_text(color)
        colors.pack_start(Gtk.Label(label="Kalınlık"), False, False, 4)
        scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 1, 32, 1)
        scale.set_value(self.overlay.width)
        scale.set_size_request(110, -1)
        scale.connect("value-changed",
                      lambda w: setattr(self.overlay, "width", w.get_value()))
        colors.pack_start(scale, False, False, 0)
        actions = Gtk.Box(spacing=5)
        layout.pack_start(actions, False, False, 0)
        self.button(actions, "↶ Geri", lambda *_: overlay.undo())
        self.button(actions, "↷ Yinele", lambda *_: overlay.redo())
        self.button(actions, "Temizle", lambda *_: overlay.clear())
        self.button(actions, "PNG", self.save_png)
        self.button(actions, "Proje Kaydet", self.save_project)
        self.button(actions, "Proje Aç", self.open_project)
        self.button(actions, "Çıkış", lambda *_: Gtk.main_quit())
        self.status = Gtk.Label(label="Kalem hazır • Ekran üstünde çiz")
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        self.status.set_max_width_chars(65)
        layout.pack_start(self.status, False, False, 0)
        self.update_tool_buttons()
        if not self.overlay.is_wayland:
            self.move(32, 32)

    @staticmethod
    def button(box, name, callback):
        b = Gtk.Button(label=name)
        b.connect("clicked", callback)
        box.pack_start(b, False, False, 0)
        return b

    def message(self, value):
        self.status.set_text(str(value))
        print("KalemX:", value, flush=True)

    def update_tool_buttons(self):
        for name, button in self.buttons.items():
            context = button.get_style_context()
            if self.overlay.tool == name:
                context.add_class("suggested-action")
            else:
                context.remove_class("suggested-action")

    def toggle_mode(self, *_):
        try:
            enabled = not self.overlay.drawing_enabled
            self.overlay.set_drawing_enabled(enabled)
        except (RuntimeError, AttributeError) as exc:
            self.message("Fare/çizim geçişi başarısız: " + str(exc))
            return
        self.mode_button.set_label(
            "↖ Fare moduna geç" if enabled else "✎ Çizime dön")
        self.message("Çizim modu" if enabled else "Fare modu • tıklamalar alttaki uygulamada")

    def set_tool(self, tool):
        self.overlay.tool = tool
        self.update_tool_buttons()
        if not self.overlay.drawing_enabled:
            self.toggle_mode()
        self.message("Araç: " + TOOL_LABELS[tool])

    def choose_color(self, color):
        self.overlay.color = color
        self.message("Renk: " + color)

    def choose_path(self, action, title, name, pattern=None):
        # Wayland layer surfaces can occlude ordinary file-picker windows.
        # Automatic paths provide a reliable fallback; --open handles loading.
        if self.overlay.is_wayland:
            return None
        dialog = Gtk.FileChooserDialog(
            title=title, parent=self, action=action)
        dialog.add_buttons(
            "İptal", Gtk.ResponseType.CANCEL,
            "Aç" if action == Gtk.FileChooserAction.OPEN else "Kaydet",
            Gtk.ResponseType.OK)
        if action == Gtk.FileChooserAction.SAVE:
            dialog.set_current_name(name)
            dialog.set_do_overwrite_confirmation(True)
        if pattern:
            selector = Gtk.FileFilter()
            selector.set_name(pattern)
            selector.add_pattern(pattern)
            dialog.add_filter(selector)
        result = dialog.get_filename() if dialog.run() == Gtk.ResponseType.OK else None
        dialog.destroy()
        return Path(result) if result else None

    def save_png(self, *_):
        path = (unique_path("image", ".png") if self.overlay.is_wayland
                else self.choose_path(Gtk.FileChooserAction.SAVE,
                                      "Çizimi PNG kaydet", "kalemx.png"))
        if path is None:
            return
        try:
            self.overlay.export_png(path)
        except (OSError, ValueError, cairo.Error) as exc:
            self.message("PNG kaydedilemedi: " + str(exc))
        else:
            self.message("PNG kaydedildi: " + str(path))

    def save_project(self, *_):
        path = (unique_path("project", ".kalemx") if self.overlay.is_wayland
                else self.choose_path(Gtk.FileChooserAction.SAVE,
                                      "KalemX projesini kaydet", "kalemx.kalemx"))
        if path is None:
            return
        try:
            self.overlay.document.save(path)
        except (OSError, ValueError) as exc:
            self.message("Proje kaydedilemedi: " + str(exc))
        else:
            self.message("Proje kaydedildi: " + str(path))

    def open_project(self, *_):
        path = self.choose_path(Gtk.FileChooserAction.OPEN,
                                "KalemX projesini aç", "", "*.kalemx")
        if path is None:
            if self.overlay.is_wayland:
                self.message("Wayland'da proje açmak için: kalemx --open DOSYA.kalemx")
            return
        try:
            loaded = Document.load(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.message("Proje açılamadı: " + str(exc))
            return
        self.overlay.current = None
        self.overlay.document = loaded
        self.overlay.queue_draw()
        self.message("Proje açıldı: " + str(path))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Linux ekran çizim uygulaması")
    parser.add_argument("--version", action="version", version="KalemX " + __version__)
    parser.add_argument("--open", metavar="DOSYA.kalemx", help="Kayıtlı projeyi aç")
    parser.add_argument("--smoke-test", action="store_true",
                        help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
        from .wayland import (WaylandUnavailable, prepare,
                              configure_overlay, configure_toolbar)
        try:
            layer_shell, monitor = prepare()
            overlay = Overlay(monitor)
            configure_overlay(overlay, layer_shell, monitor)
            overlay.show_all()
            toolbar = Toolbar(overlay)
            configure_toolbar(toolbar, layer_shell, monitor)
        except (WaylandUnavailable, RuntimeError) as exc:
            parser.exit(2, "KalemX Wayland: " + str(exc) + "\n")
    else:
        if not os.environ.get("DISPLAY"):
            parser.exit(2, "KalemX: X11 DISPLAY bulunamadı.\n")
        overlay = Overlay()
        overlay.show_all()
        toolbar = Toolbar(overlay)
    if args.open:
        try:
            overlay.document = Document.load(args.open)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.exit(2, "KalemX: Proje açılamadı: " + str(exc) + "\n")
    toolbar.show_all()
    if args.smoke_test:
        def smoke():
            try:
                overlay.document.add(Stroke("pen", "#e53935", 4, ((10, 10), (45, 45))))
                overlay.queue_draw()
                toolbar.toggle_mode()
                toolbar.toggle_mode()
                with tempfile.TemporaryDirectory() as folder:
                    output = Path(folder) / "smoke.png"
                    overlay.export_png(output)
                    if output.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                        raise AssertionError("PNG header invalid")
                    project = Path(folder) / "smoke.kalemx"
                    overlay.document.save(project)
                    assert Document.load(project).to_dict() == overlay.document.to_dict()
                print("KALEMX_SMOKE_OK", flush=True)
            except Exception:
                import traceback
                traceback.print_exc()
                # A failing smoke run MUST fail CI.
                os._exit(1)
            GLib.idle_add(Gtk.main_quit)
            return False
        GLib.idle_add(smoke)
    Gtk.main()


if __name__ == "__main__":
    main()
