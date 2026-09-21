# KalemX

Linux için açık kaynaklı ekran çizim aracı — **0.1.0-alpha / Wayland önizlemesi**.

## Destek durumu

| Oturum | Durum |
| --- | --- |
| X11 (Mint Cinnamon dahil) | İlk prototip kullanıcı tarafından çalıştırıldı; korunuyor |
| KDE Plasma Wayland, Sway, Hyprland ve Layer Shell destekleyen diğer compositor'lar | Deneysel GTK3 Layer Shell arka ucu |
| GNOME Wayland | Henüz desteklenmiyor: GNOME Shell entegrasyonu gerekli |
| Birden fazla monitör | Henüz desteklenmiyor; Wayland'da ilk monitör seçilir |

Wayland desteği tüm masaüstlerini kapsamaz. KalemX, `zwlr_layer_shell_v1`
olmadan bir XWayland penceresiyle sahte "ekran üstü" desteğine geçmez.

## Kurulum (Mint / Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
# Wayland oturumu için ek olarak:
sudo apt install gir1.2-gtklayershell-0.1

git clone https://github.com/MOzcelik14/KalemX.git
cd KalemX
/usr/bin/python3 -m kalemx
```

Bu özellik dalını denemek için mevcut yerel repoda:

```bash
cd ~/KalemX
git fetch origin
git switch --track origin/feat/wayland-layer-shell
/usr/bin/python3 -m kalemx
```

**Wayland testini gerçek bir Wayland oturumunda yap.** `echo "$XDG_SESSION_TYPE"`
ile oturumu kontrol edebilirsin; X11'den Wayland'a yalnızca ortam değişkeni
atarak geçmek mümkün değildir. GTK'nin native Wayland arka ucu aranır.

## Özellikler

Şeffaf çizim katmanı, kalem, fosforlu kalem, renk ve kalınlık, fare modu,
geri al/yinele, temizle, şeffaf PNG. X11'de PNG dosya seçicisi açılır.
Wayland'da (normal dosya seçicisinin katmanın altında kalmaması için) PNG,
`~/Pictures/kalemx-*.png` dosyasına kaydedilir; `Pictures` yoksa ev dizini kullanılır.

## Bilinen sınırlar

- İlk Wayland uygulaması **henüz gerçek Wayland oturumunda test edilmedi**.
- Wayland protokolü ve katman davranışı masaüstüne göre değişebilir.
- GNOME Wayland'da destek yok. X11 ile aynı güvenilirlik henüz doğrulanmadı.
- İlk monitörle sınırlı; monitör bağlama/çıkarma, ölçeklendirme ve pen-tablet
  davranışları daha sonra ele alınacak.
- Gerçek alfa silgisi, PDF, portal tabanlı dosya seçicisi henüz uygulanmadı.

## Kaynaklar

- GTK3 Layer Shell: https://github.com/wmww/gtk-layer-shell
- Ubuntu paket: https://packages.ubuntu.com/noble/gir1.2-gtklayershell-0.1

GPL-3.0-or-later lisansı hedeflenmektedir; tam lisans metni eklenecek.
