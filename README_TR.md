# Akıllı CCTV Güvenlik ve Bölge İhlal Alarmı (YOLO & Telegram)

[English](README.md) | [Türkçe](README_TR.md)

Bu proje, bilgisayar kamerası (webcam) veya bir video dosyasını gerçek zamanlı izleyerek, kullanıcı tarafından ekranda belirlenen özel bir yasaklı bölgeye (polygon) girildiğinde uyarı veren bir güvenlik yazılımıdır. Tespit edilen ihlaller, fotoğrafı ile birlikte anında bir Telegram Botu aracılığıyla alıcıya mesaj olarak iletilir.

## Proje Yapısı

*   `main.py`: Uygulamanın giriş noktasıdır. Ekran cizim arayüzünü açar, video akış döngüsünü başlatır ve koordinatları yönetir.
*   `detector.py`: YOLOv8 modelini kullanarak nesneleri tespit eden ve bu nesnelerin çizilen alanın içinde olup olmadığını kontrol eden (`cv2.pointPolygonTest` ile) modüldür.
*   `telegram_notifier.py`: İhlal durumlarında Telegram API kullanarak fotoğraf ve mesaj gönderimini yöneten asenkron tasarımlı modüldür.
*   `config.json`: Telegram bilgileri, model yolu ve algılanan bölge noktaları (koordinatları) gibi ayarları tutar.
*   `alerts/`: İhlal anında kaydedilen alarmlı karelerin saklandığı klasördür.

## Kurulum ve Bağımlılıklar

Proje için gerekli olan `ultralytics` (YOLO) ve `opencv-python` kütüphanelerinin kurulu olduğundan emin olun:

```bash
pip install ultralytics opencv-python requests numpy
```

## Telegram Bot Entegrasyonu (Adım Adım)

Sistemin Telegram bildirimleri gönderebilmesi için bir bota ve alıcı ID'sine ihtiyacınız vardır:

1.  **Bot Oluşturma:** Telegram uygulamasında **@BotFather**'ı aratın ve sohbet başlatın. `/newbot` komutunu gönderin. Botunuza bir isim ve kullanıcı adı verin. BotFather size bir **API Token** verecektir.
2.  **Chat ID Alma:** Yeni oluşturduğunuz botu Telegram'da aratarak `/start` komutu ile başlatın. Ardından tarayıcınızdan şu adrese gidin (Token kısmına kendi bot tokeninizi yazın):
    `https://api.telegram.org/bot<TOKENINIZ>/getUpdates`
    Buradaki JSON çıktısında `"chat":{"id":XXXXXXXXX...}` kısmındaki chat ID numarasını kopyalayın.
3.  **Config Girişi:** `config.json` dosyasını açıp `telegram_token` ve `telegram_chat_id` değerlerini kendinize göre güncelleyin.

## Nasıl Çalıştırılır?

Projeyi başlatmak için dizin içerisinden `main.py` dosyasını çalıştırın:

```bash
python main.py
```

### Kullanım Kılavuzu:
*   **Güvenlik Bölgesi Çizimi:** Program ilk açıldığında veya bölge tanımlı olmadığında karşınıza gelen ilk kare üzerinde farenin sol tuşuyla tıklamalar yaparak sınırları belirleyin.
*   **Seçimleri Sıfırlamak:** Çizdiğiniz alanı beğenmediyseniz **`c`** tuşuna basarak sıfırlayabilirsiniz.
*   **Çizimi Kaydetmek:** Çizimi tamamladıktan sonra **`s`** veya **`ENTER`** tuşuna basarak kaydedin. Bu koordinatlar `config.json` dosyasına otomatik yazılacaktır.
*   **Bölgeyi Yeniden Çizmek:** Program çalışırken alanı değiştirmek isterseniz **`r`** tuşuna basarak çizim ekranını tekrar açabilirsiniz.
*   **Çıkış:** Programı sonlandırmak için **`q`** tuşuna basın.
