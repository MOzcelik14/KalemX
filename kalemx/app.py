"""KalemX X11 screen annotation prototype."""
import os
import sys
from pathlib import Path

import cairo
import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

COLORS = ("#e53935", "#ffb300", "#43a047", "#1e88e5", "#ffffff", "#111111")


class Overlay(Gtk.Window):
    def __init__(self):
        super().__init__(title="KalemX overlay")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_default_size(screen.get_width(), screen.get_height())
        self.move(0, 0)
        self.strokes = []
        self.redo_stack = []
        self.current = None
        self.color = COLORS[0]
        self.width = 4.0
        self.tool = "pen"
        self.drawing_enabled = True
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_press)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-release-event", self.on_release)

    def set_drawing_enabled(self, enabled):
        self.drawing_enabled = enabled
        window = self.get_window()
        if window:
            window.input_shape_combine_region(
                None if enabled else cairo.Region(), 0, 0)

    def on_press(self, _widget, event):
        if self.drawing_enabled and event.button == 1:
            self.current = {
                "tool": self.tool, "color": self.color, "width": self.width,
                "points": [(event.x, event.y)]}
            self.redo_stack.clear()
            self.queue_draw()
        return bool(self.drawing_enabled)

    def on_motion(self, _widget, event):
        if self.current and event.state & Gdk.ModifierType.BUTTON1_MASK:
            self.current["points"].append((event.x, event.y))
            self.queue_draw()
        return bool(self.drawing_enabled)

    def on_release(self, _widget, event):
        if self.current and event.button == 1:
            self.current["points"].append((event.x, event.y))
            self.strokes.append(self.current)
            self.current = None
            self.queue_draw()
        return bool(self.drawing_enabled)

    @staticmethod
    def paint_stroke(cr, stroke):
        rgba = Gdk.RGBA()
        rgba.parse(stroke["color"])
        cr.set_source_rgba(rgba.red, rgba.green, rgba.blue,
                           0.35 if stroke["tool"] == "highlighter" else 1)
        cr.set_line_width(stroke["width"] *
                          (4 if stroke["tool"] == "highlighter" else 1))
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        points = stroke["points"]
        if not points:
            return
        cr.move_to(*points[0])
        if len(points) == 1:
            cr.line_to(points[0][0] + 0.01, points[0][1] + 0.01)
        else:
            for point in points[1:]:
                cr.line_to(*point)
        cr.stroke()

    def render(self, cr):
        for stroke in self.strokes:
            self.paint_stroke(cr, stroke)
        if self.current:
            self.paint_stroke(cr, self.current)

    def on_draw(self, _widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        self.render(cr)
        return False

    def undo(self):
        if self.strokes:
            self.redo_stack.append(self.strokes.pop())
            self.queue_draw()

    def redo(self):
        if self.redo_stack:
            self.strokes.append(self.redo_stack.pop())
            self.queue_draw()

    def clear(self):
        if self.strokes:
            self.redo_stack.extend(reversed(self.strokes))
            self.strokes.clear()
            self.queue_draw()

    def save_png(self, path):
        screen = self.get_screen()
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, screen.get_width(), screen.get_height())
        self.render(cairo.Context(surface))
        surface.write_to_png(str(path))


class Toolbar(Gtk.Window):
    def __init__(self, overlay):
        super().__init__(title="KalemX")
        self.overlay = overlay
        self.set_keep_above(True)
        self.set_resizable(False)
        self.set_border_width(8)
        self.connect("destroy", lambda *_: Gtk.main_quit())
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(root)
        tools = Gtk.Box(spacing=4)
        root.pack_start(tools, False, False, 0)
        self.mode_button = self.button(tools, "Fare modu", self.toggle_mode)
        self.button(tools, "Kalem", lambda *_: self.set_tool("pen"))
        self.button(tools, "Fosforlu", lambda *_: self.set_tool("highlighter"))
        self.button(tools, "Geri al", lambda *_: overlay.undo())
        self.button(tools, "Yinele", lambda *_: overlay.redo())
        self.button(tools, "Temizle", lambda *_: overlay.clear())
        self.button(tools, "PNG", self.save)
        self.button(tools, "Çıkış", lambda *_: Gtk.main_quit())
        colors = Gtk.Box(spacing=4)
        root.pack_start(colors, False, False, 0)
        for color in COLORS:
            button = Gtk.Button(label="●")
            rgba = Gdk.RGBA()
            rgba.parse(color)
            button.override_color(Gtk.StateFlags.NORMAL, rgba)
            button.connect("clicked", lambda _button, c=color: self.choose_color(c))
            colors.pack_start(button, False, False, 0)
        colors.pack_start(Gtk.Label(label="Kalınlık"), False, False, 4)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 24, 1)
        scale.set_value(4)
        scale.set_size_request(110, -1)
        scale.connect("value-changed",
                      lambda widget: setattr(overlay, "width", widget.get_value()))
        colors.pack_start(scale, False, False, 0)
        self.move(60, 50)

    @staticmethod
    def button(box, label, callback):
        button = Gtk.Button(label=label)
        button.connect("clicked", callback)
        box.pack_start(button, False, False, 0)
        return button

    def toggle_mode(self, *_):
        enabled = not self.overlay.drawing_enabled
        self.overlay.set_drawing_enabled(enabled)
        self.mode_button.set_label("Fare modu" if enabled else "Çizim modu")

    def set_tool(self, tool):
        self.overlay.tool = tool

    def choose_color(self, color):
        self.overlay.color = color

    def save(self, *_):
        dialog = Gtk.FileChooserDialog(
            title="Çizimi PNG olarak kaydet", parent=self,
            action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons("İptal", Gtk.ResponseType.CANCEL,
                           "Kaydet", Gtk.ResponseType.OK)
        dialog.set_current_name("kalemx.png")
        dialog.set_do_overwrite_confirmation(True)
        if dialog.run() == Gtk.ResponseType.OK:
            try:
                self.overlay.save_png(Path(dialog.get_filename()))
            except (OSError, cairo.Error) as exc:
                error = Gtk.MessageDialog(
                    transient_for=self, flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.CLOSE, text=str(exc))
                error.run()
                error.destroy()
        dialog.destroy()


def main():
    if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" or not os.environ.get("DISPLAY"):
        print("KalemX 0.1 alpha requires an X11 session.", file=sys.stderr)
        raise SystemExit(2)
    overlay = Overlay()
    overlay.show_all()
    toolbar = Toolbar(overlay)
    toolbar.show_all()
    Gtk.main()
