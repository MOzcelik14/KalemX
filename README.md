# KalemX

Linux için açık kaynaklı ekran çizim aracı — **0.1.0-alpha X11 prototipi**.

## Kurulum (Mint / Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
git clone https://github.com/MOzcelik14/KalemX.git
cd KalemX
/usr/bin/python3 -m kalemx
```

Özellikler: şeffaf çizim katmanı, kalem, fosforlu kalem, renk/kalınlık, fare modu, geri al/yinele, temizle ve şeffaf PNG.

**Sınırlamalar:** Yalnızca X11; Wayland ve çoklu monitör henüz yok. Masaüstü ortamlarında gerçek çalıştırma testi yapılmadı. GNOME Wayland için ayrı entegrasyon gerekecek.

GPL-3.0-or-later lisansı hedeflenmektedir; tam lisans metni eklenecek.
