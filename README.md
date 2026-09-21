# KalemX

**Linux için ekran üzerinde çizim / screen annotation for Linux.**
Kalem, fosforlu kalem, gerçek alfa silgisi, geometrik şekiller, fare modu,
geri al/yinele, şeffaf PNG ve yeniden açılabilir proje dosyaları.

**Durum: 0.2.0b1 (beta adayı).** GTK3/Cairo tabanlıdır; GTK3 bu sürümde
bilinçli tercihtir çünkü var olan X11 prototipi ve GTK3 Layer Shell
entegrasyonunu korur. GTK4 portu ayrı bir değişiklik olacaktır.

## Uyumlu ortamlar / Compatibility

| Ortam | Durum |
| --- | --- |
| Linux Mint Cinnamon X11 | İlk prototip kullanıcı tarafından doğrulandı; beta regresyon testi gerekli |
| GNOME / KDE / XFCE / MATE / LXQt X11 | X11 katmanı; bütün sürümlerde gerçek masaüstü testi yapılmadı |
| KDE Plasma Wayland, Sway, Hyprland, diğer zwlr_layer_shell_v1 compositor'ları | Yerel Layer Shell backend, **deneysel** |
| GNOME Wayland | **Desteklenmiyor**. GNOME Shell entegrasyonu gerekir |
| Cinnamon Wayland | Layer Shell desteğine ve oturuma bağlı; doğrulanmadı |
| Çoklu ekran | Bu beta ilk ekranla sınırlıdır |

Bu uygulama bir XWayland penceresi açıp tüm Wayland masaüstlerinde çalıştığını
iddia etmez. Wayland katmanı, desteklenmeyen compositor'da açıklayıcı hata verir.
[Destek tablosu](docs/COMPATIBILITY.md).

## Kurulum / Install

**Mint, Ubuntu ve Debian için en kolay yol:** Bir GitHub Release altında
yayımlanan \`kalemx_*_all.deb\` paketini indir, sonra:

\`\`\`bash
sudo apt install ./kalemx_*_all.deb
kalemx
\`\`\`

DEB dosyası oluşmadan önce, kaynak koddan denemek için:

\`\`\`bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
# Yalnızca desteklenen Wayland oturumları için:
sudo apt install gir1.2-gtklayershell-0.1

git clone https://github.com/MOzcelik14/KalemX.git
cd KalemX
/usr/bin/python3 -m kalemx
\`\`\`

Var olan repoda beta dalını denemek için \`git fetch origin && git switch --track origin/feat/production-foundation\` komutunu kullan. Dal yerelde varsa \`git switch feat/production-foundation && git pull --ff-only\`.

**Arch tabanlı**: \`sudo pacman -S python-gobject python-cairo gtk3 gtk-layer-shell\`.
GtkLayerShell için GIR typelib paketinin yüklü olduğunu denetle.
**Fedora tabanlı**: \`sudo dnf install python3-gobject python3-cairo gtk3 gtk-layer-shell\`;
GIR typelib dağıtıma göre ayrı paket olabilir. Bu iki dağıtımda DEB kurulmaz:
deponun kökünde \`python3 -m kalemx\` çalıştır.

## Kullanım

Programın üstteki araç çubuğundan kalem / fosfor / silgi / çizgi / ok /
dikdörtgen / elips seç; fare modunda çizimler görünmeye devam eder ve
tıklamalar alttaki uygulamaya geçer. **PNG yalnızca çizim katmanını dışa
aktarır; masaüstünün ekran görüntüsünü kaydetmez.**

**Proje Kaydet**: düzenlenebilir \`.kalemx\` JSON çizim belgesi.
**Proje Aç**: X11 üzerinde dosya seçici ile; Wayland'da
\`kalemx --open /dosya/yolu.kalemx\`. Wayland'da kaydetme konumları:
\`~/Pictures\` (PNG) ve \`~/Documents\` (proje); bu dizinler yoksa ev dizini.

Diğer komutlar:

\`\`\`bash
kalemx --version
kalemx --help
kalemx --open ~/Documents/ornek.kalemx
\`\`\`

## Belgeler

- [Kullanım kılavuzu](docs/USER_GUIDE.md)
- [Uyumluluk ve bilinen sınırlar](docs/COMPATIBILITY.md)
- [Teknik mimari](docs/ARCHITECTURE.md)
- [Paketleme, CI ve release](docs/RELEASE.md)
- [Katkı rehberi](CONTRIBUTING.md)
- [Değişiklik geçmişi](CHANGELOG.md)

## Lisans

MIT © 2026 Murat Özçelik. Bkz. [LICENSE](LICENSE).
