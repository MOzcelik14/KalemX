# Build ve GitHub Releases

Bu repo **MIT lisanslıdır**. Mevcut sürüm `kalemx/__init__.py` ve
`pyproject.toml` arasında eşleşmelidir.

## CI

`.github/workflows/ci.yml` her push/PR ve manuel çalıştırmada
Python derleme, GTK gerektirmeyen model testleri, Cairo testleri,
Xvfb üzerinde gerçek GTK X11 açılış/fare/PNG smoke testi,
desktop dosyası/SVG doğrulaması ve DEB paket kurulumu için dosya
denetimi yapar. Üretilen DEB Actions artifact olarak yüklenir.
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

`.github/workflows/release.yml` `v*` etiketinde çalışır. Etiketi
kaynak sürümüyle karşılaştırır, testleri çalıştırır; `.deb`, wheel,
sdist, kaynak arşivi ve SHA256SUMS üretip GitHub Release'e yükler.
`b`/ `rc` içeren etiketleri pre-release işaretler.

**Release için sıralama:**
1. PR'ı birleştir; CI'nin yeşil olduğundan emin ol.
2. `main` üzerindeki `__version__` ve `pyproject.toml` aynı mı kontrol et.
3. Ana dalda etiket oluştur ve gönder:
   ```bash
   git switch main
   git pull --ff-only origin main
   git tag v0.2.0b1
   git push origin v0.2.0b1
   ```
4. GitHub Actions → Release işinin tamamlandığını doğrula.
5. GitHub Releases altında çıktıları ve SHA256SUMS dosyasını kontrol et.

Etiketi PR'ın test edilmeyen commit'ine değil, onaylanmış main commit'ine
uygula. Etiketi tekrar kullanma; sonraki sürümde numarayı artır.
Private GitHub reposunda Release dosyalarını yalnızca erişimi olanlar görür.
Repo erişimini bilinçli olarak değiştirmedik.

## Python wheel hakkında

Wheel sistem GTK/PyGObject/Cairo kütüphanelerini paketlemez. Venv'de
kullanacaksan `--system-site-packages` ve ilgili dağıtım paketleri
gerekebilir; kullanıcıya kurulum için DEB veya kaynak kod tavsiye edilir.
