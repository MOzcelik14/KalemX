"""Wayland Layer Shell integration for KalemX's GTK3 windows.

This backend intentionally refuses unsupported compositors. An ordinary
Wayland toplevel cannot guarantee an always-on-top screen overlay.
"""
import gi


class WaylandUnavailable(RuntimeError):
    """The compositor or session cannot provide an annotation overlay."""


def prepare():
    """Return (GtkLayerShell, first monitor), checking native Wayland support."""
    try:
        gi.require_version("GtkLayerShell", "0.1")
        from gi.repository import Gdk, Gtk, GtkLayerShell
    except (ValueError, ImportError) as exc:
        raise WaylandUnavailable(
            "GTK Layer Shell eksik. Mint/Ubuntu/Debian: "
            "sudo apt install gir1.2-gtklayershell-0.1"
        ) from exc

    # Ensure GDK has opened the user's real display before probing protocols.
    if Gdk.Display.get_default() is None:
        Gtk.init([])
    display = Gdk.Display.get_default()
    if display is None:
        raise WaylandUnavailable("Wayland ekranına bağlanılamadı.")
    if "wayland" not in display.get_type().name.lower():
        raise WaylandUnavailable(
            "GTK, XWayland/X11 üzerinden açıldı. Native Wayland gerekli; "
            "GDK_BACKEND=wayland ayarını kontrol et."
        )
    if not GtkLayerShell.is_supported():
        raise WaylandUnavailable(
            "Bu Wayland masaüstünde zwlr_layer_shell_v1 desteklenmiyor. "
            "GNOME Wayland için ileride ayrı Shell entegrasyonu gerekecek."
        )
    if display.get_n_monitors() < 1:
        raise WaylandUnavailable("Kullanılabilir ekran bulunamadı.")
    return GtkLayerShell, display.get_monitor(0)


def configure_overlay(overlay, layer_shell, monitor):
    """Fill one output with a transparent canvas, without reserving space."""
    ls = layer_shell
    ls.init_for_window(overlay)  # MUST happen before Gtk.Window realization.
    ls.set_namespace(overlay, "kalemx-canvas")
    ls.set_monitor(overlay, monitor)
    ls.set_layer(overlay, ls.Layer.TOP)
    for edge in (ls.Edge.TOP, ls.Edge.BOTTOM, ls.Edge.LEFT, ls.Edge.RIGHT):
        ls.set_anchor(overlay, edge, True)
    ls.set_exclusive_zone(overlay, -1)
    ls.set_keyboard_mode(overlay, ls.KeyboardMode.NONE)


def configure_toolbar(toolbar, layer_shell, monitor):
    """Use the OVERLAY layer so controls remain above the canvas."""
    ls = layer_shell
    toolbar.set_decorated(False)
    ls.init_for_window(toolbar)  # MUST happen before realization.
    ls.set_namespace(toolbar, "kalemx-toolbar")
    ls.set_monitor(toolbar, monitor)
    ls.set_layer(toolbar, ls.Layer.OVERLAY)
    ls.set_anchor(toolbar, ls.Edge.TOP, True)
    ls.set_anchor(toolbar, ls.Edge.LEFT, True)
    ls.set_margin(toolbar, ls.Edge.TOP, 24)
    ls.set_margin(toolbar, ls.Edge.LEFT, 24)
    ls.set_exclusive_zone(toolbar, -1)
    # Older compositors cannot focus a layer surface without stealing focus.
    if ls.get_protocol_version() >= 4:
        ls.set_keyboard_mode(toolbar, ls.KeyboardMode.ON_DEMAND)
    else:
        ls.set_keyboard_mode(toolbar, ls.KeyboardMode.NONE)
