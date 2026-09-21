# Build ve GitHub Releases

Bu repo **MIT lisanslıdır**. Mevcut sürüm `kalemx/__init__.py` ve
`pyproject.toml` arasında eşleşmelidir.

## CI

`.github/workflows/ci.yml` her push/PR ve manuel çalıştırmada
Python derleme, GTK gerektirmeyen model testleri, Cairo testleri,
Xvfb üzerinde gerçek GTK X11 açılış/fare/PNG smoke testi,
desktop dosyası/SVG doğrulaması, DEB paket denetimi ve wheel/sdist
derlemesi yapar. Üretilen DEB Actions artifact olarak yüklenir.
**Xvfb testleri gerçek Wayland compositör testi değildir.**

## DEB

```bash
sudo apt install dpkg-dev python3
bash scripts/build_deb.sh
dpkg-deb --info dist/kalemx_*_all.deb
sudo apt install ./dist/kalemx_*_all.deb
kalemx --version
```

DEB `Architecture: all` ve sistem Python bağımlılıklarını kullanır;
binary Python paketleri içine gömülmez. Wayland GIR typelib "Recommends"
olup X11 için zorunlu değildir.

## GitHub release otomasyonu

`.github/workflows/release.yml` `main` dalına push yapıldığında,
`v*` etiketi gönderildiğinde veya manuel çalıştırıldığında çalışır.
Sürümün `kalemx/__init__.py` içindeki değerini okur, testleri çalıştırır;
`.deb`, wheel, sdist, kaynak arşivi ve `SHA256SUMS.txt` üretir.
Aynı sürümün Release'i zaten varsa yinelenen yayın yapmaz.

**Otomatik yayın:** Değişiklikler önce CI'dan geçer; yeni sürüm
`__version__` ve `pyproject.toml` dosyalarında birlikte artırılıp
`main` dalına birleştirildiğinde iş akışı `v<SÜRÜM>` etiketi ve Release
oluşturur. `b`, `a` veya `rc` içeren sürümler pre-release işaretlenir.

**Etiketle manuel yayın** hâlâ desteklenir:
```bash
git switch main
git pull --ff-only origin main
git tag "v$(/usr/bin/python3 -c 'from kalemx import __version__; print(__version__)')"
git push origin --tags
```

Mevcut etiketi tekrar kullanma: her yeni dağıtımda sürümü artır.
Release çıktısını GitHub → Releases'ten kontrol et. GitHub,
`~` karakteri taşıyan Debian dosya adlarını indirilebilir asset isminde
nokta olarak normalleştirebilir; paketin içindeki sürümü
`dpkg-deb --info DOSYA.deb` ile görebilirsin.

Private GitHub reposunda Release dosyalarını yalnızca erişimi olanlar görür.
Repo erişimini bilinçli olarak değiştirmedik.

## Python wheel hakkında

Wheel sistem GTK/PyGObject/Cairo kütüphanelerini paketlemez. Venv'de
kullanacaksan `--system-site-packages` ve ilgili dağıtım paketleri
gerekebilir; kullanıcıya kurulum için DEB veya kaynak kod tavsiye edilir.
