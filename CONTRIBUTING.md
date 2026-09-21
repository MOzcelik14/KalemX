# Katkı / Contributing

- Issue açmadan önce dağıtım, DE/compositor, XDG_SESSION_TYPE, KalemX
  sürümü, tekrar adımları ve terminal hatalarını hazırla.
- Kaynakta \`python3 -m compileall -q kalemx tests\`,
  \`python3 -m unittest discover -s tests -v\` çalıştır.
- GTK/Gdk/GtkLayerShell sürümlerini karıştırma. İki farklı GI major
  namespace aynı süreçte yüklenmemeli.
- X11 değişikliği için Mint Cinnamon X11, Wayland için native compositor
  üzerinde fare modu ve anotasyon görünürlüğünü test et.
- Release veya güvenlik değişikliklerini main'e hemen göndermek yerine
  PR aç; CI yeşil olmadan tag üretme.
- Proje MIT lisansı altındadır; katkıda bulunurken lisansa uy.
