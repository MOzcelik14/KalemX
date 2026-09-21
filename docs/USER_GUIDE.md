# KalemX kullanım kılavuzu

## Ekran ve fare

KalemX açıldığında şeffaf bir tuval ekranın üzerinde görünür. İlk araç
**Kalem** ve ilk mod **Çizim** modudur. Araç çubuğu üzerinde "Fare moduna geç"
düğmesine basınca çizim durur, pencere altındaki programları tıklayabilirsin;
çizimler kaybolmaz. "Çizime dön" ile devam et. Fare modunda bir çizim aracına
basmak çizim modunu yeniden etkinleştirir.

Layer Shell ile desteklenen Wayland oturumunda araç çubuğu Overlay katmanında,
çizim ise Top katmanındadır; GNOME Wayland desteklenmez.

## Araçlar

- Kalem: serbest çizgi.
- Fosfor: daha geniş ve %35 opaklıkta çizgi.
- Silgi: şeffaf tuvalde mürekkebi **alfa kanalıyla** temizler; beyaz çizmez.
- Çizgi / Ok: sürüklemenin başlangıcı ve bitişi arasında.
- Dikdörtgen / Elips: sürükleyerek sınırlarını oluştur.
- Renk ve kalınlık: sonraki çizgiler için değiştirilir.
- Geri / Yinele: tek çizgiyi veya bütün "Temizle" işlemini geri alabilir.

## Kaydetme

**PNG** şeffaf anotasyonu kaydeder. Tüm masaüstünü veya PDF'yi birlikte
kaydetmek için öncelikle ayrı ekran görüntüsü alıp görüntü düzenleyicide
birleştirmek gerekir. KalemX bu betada ekran görüntüsü veya PDF import etmez.

**Proje Kaydet** taşınabilir JSON biçimli `.kalemx` üretir. Kaydedilmiş
çizimleri `kalemx --open dosya.kalemx` ile yeniden açabilirsin. X11'de
"Proje Aç" dosya seçicisi de vardır. Wayland'da normal dosya seçim
pencereleri Layer Shell'in arkasında kalabildiğinden bu beta otomatik
benzersiz kaydetme adları üretir ve proje açmak için komut satırını kullanır.

## Sorun giderme

```bash
echo "$XDG_SESSION_TYPE"
env | grep '^GDK_BACKEND='
/usr/bin/python3 -m kalemx --version
/usr/bin/python3 -m kalemx
```

- `GtkLayerShell` eksik: dağıtımının GIR typelib paketini kur.
- `zwlr_layer_shell_v1` yok: compositor Layer Shell desteklemiyor.
- Fare modu alttaki uygulamaya geçmiyorsa oturum, compositor ve terminal
  çıktısıyla GitHub Issue aç.
- Çoklu monitörde ikinci ekranda çizemiyorsan bu beta tek ekranla sınırlı.
- Kaydedilmemiş çizimler program kapanınca kaybolur; Proje Kaydet'i kullan.
