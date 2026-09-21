# Masaüstü uyumluluğu

Bu belge "kurulur" ile "ekranın üstünde çalışır" kavramlarını ayırır.
Python ve GTK'nin bulunması genel ekran çizimi için yeterli değildir.

| Oturum | Yöntem | Durum |
| --- | --- | --- |
| Cinnamon X11 | GTK3 şeffaf en üst pencere, X11 input region | İlk prototip denenmiş; yeni betayı tekrar test et |
| GNOME X11 | Aynı X11 backend | Henüz bağımsız test yapılmadı |
| KDE Plasma X11 | Aynı X11 backend | Henüz bağımsız test yapılmadı |
| XFCE/MATE/LXQt X11 | Aynı X11 backend | Henüz bağımsız test yapılmadı |
| KDE Plasma Wayland | GTK Layer Shell / zwlr_layer_shell_v1 | Deneysel; kullanıcı testi gerekli |
| Sway/Hyprland | GTK Layer Shell / zwlr_layer_shell_v1 | Deneysel; kullanıcı testi gerekli |
| GNOME Wayland | Layer Shell desteklemiyor | Desteklenmiyor |
| Diğer Wayland compositor'lar | Protokol sorgusu | Desteğe bağlı; doğrulanmadı |

**XWayland, native Wayland katmanının alternatifi değildir.** Ekranın
üzerinde kalma ve alttaki uygulamalara tıklama ayrı ayrı compositor
entegrasyonu gerektirir. `GDK_BACKEND=x11` zorlaması GNOME Wayland için
çözüm diye önerilmez.

**Beta sınırları:** İlk monitör, yerel koordinatlar, hotplug ve kesirli
ölçeklendirme testleri yapılmadı. Global klavye kısayolu, PDF importu,
screenshot, tablet basıncı ve GNOME Shell eklentisi henüz yoktur.

Upstream referansları:
- https://github.com/wmww/gtk-layer-shell
- https://docs.gtk.org/gdk3/method.Window.set_pass_through.html
- https://docs.gtk.org/gtk3/method.Widget.input_shape_combine_region.html
