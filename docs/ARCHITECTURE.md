# KalemX teknik mimari

```text
kalemx/
  model.py       # GTK/Cairo bağımsız Stroke, Document, JSON
  render.py      # Cairo tuval, şekiller, alfa silme, PNG
  app.py         # GTK3 araç çubuğu, CLI, olay işleme, X11 overlay
  wayland.py     # GtkLayerShell native Wayland katmanı ve protokol kontrolü
  __main__.py    # python -m kalemx
tests/
  test_model.py  # projeler, girdi doğrulama, undo/redo
  test_render.py # raster çıktısı ve gerçek silgi
scripts/
  build_deb.sh   # Debian/Ubuntu/Mint için yerel Python bağımlılıklı paket
.github/workflows/
  ci.yml         # syntax, unit test, Xvfb smoke, desktop-file, DEB
  release.yml    # etiketli release: DEB/wheel/sdist/source/SHA256
```

## Veri akışı

Ekran fare hareketleri başlangıç/ara/bitiş koordinatlarına çevrilir.
`Stroke` değişmez veri yapısıdır. `Document` ekle/sil/geçmiş işlerini
üstlenir. Her çizimde ve PNG dışa aktarımında `render.surface()` Cairo
ARGB32 yüzeyi oluşturur. Silgi ayrı bir araçtır ve `OPERATOR_CLEAR`
ile önceki çizgilerin alfa kanalını temizler; temizleme işlemi de normal
bir Stroke olduğundan undo/redo ve proje kayıtlarıyla korunur.

JSON dosya sürümü `1`'dir; bilinmeyen araç/format/sürüm reddedilir.
Import boyutu sınırı 30 MB, strok sınırı 20.000, stroke nokta sınırı
100.000'dir. Dosyalar kod olarak çalıştırılmaz.

## Sistem desteği

X11 pencere en üste yerleştirilir, fare modu GTK widget input şekli ve
GDK pass-through kullanır. Wayland compositor desteği önceden doğrulanır;
ayrı araç çubuğu OVERLAY, çizim TOP katmanındadır. GNOME Shell'i
Layer Shell varmış gibi taklit etmek desteklenmiyor.

**GTK3 kararı:** Eski X11 kodu ve GtkLayerShell 0.1 API kararlılığı için
bu beta GTK3 kullanır. GTK4 portu kendi kapsamlı migrasyonunu ve
`gtk4-layer-shell` bağımlılığını gerektirir.

## Güvenlik ve gizlilik

Ekran görüntüsü alınmaz, ağ çağrısı yoktur, proje dosyaları yerel diske
yazılır. Wayland giriş kısıtları bilinçli olarak aşılmaz. Proje içe
aktarımında boyut ve koordinat doğrulaması bulunur.
