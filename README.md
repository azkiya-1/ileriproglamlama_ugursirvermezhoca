# 🏪 Restoran Sipariş Sistemi

Python ile geliştirilmiş, terminal tabanlı restoran sipariş ve yönetim uygulaması.  
İleri Programlama dersi Final Projesi — Nesne Yönelimli Programlama (OOP).

---

## 📋 Proje Hakkında

Bu uygulama, bir restoranın günlük operasyonlarını yönetmek için tasarlanmıştır.  
Garson veya kasiyer, terminal üzerinden sipariş açabilir, kalem ekleyip çıkarabilir ve hesap kesebilir.  
Tüm veriler `restoran_verisi.json` dosyasında saklandığı için program kapatılıp açıldığında veriler kaybolmaz.

---

## 🗂 Dosya Yapısı

```
restoran_siparis/
├── main.py                  # Restoran sınıfı + ana döngü (giriş noktası)
├── models.py                # Veri sınıfları: MenuItem, SiparisKalemi, Siparis, Masa
├── utils.py                 # Yardımcı fonksiyonlar: dosya I/O, girdi doğrulama, formatlama
├── restoran_verisi.json     # Otomatik oluşturulan kalıcı veri dosyası
├── flowchart.png            # Algoritma akış şeması
├── README.md
└── .gitignore
```

---

## 🧩 Sınıf Yapısı (OOP Tasarımı)

| Sınıf | Dosya | Görev |
|---|---|---|
| `MenuItem` | models.py | Menüdeki bir ürünü tanımlar (ad, kategori, fiyat) |
| `SiparisKalemi` | models.py | Siparişe eklenen ürün + adet çiftini tutar |
| `Siparis` | models.py | Bir masanın açık/kapalı siparişini yönetir |
| `Masa` | models.py | Restorandaki fiziksel masayı temsil eder |
| `Restoran` | main.py | Tüm işlemleri yöneten ana kontrolcü sınıf |

---

## ✅ Teknik Gereksinimler

| Gereksinim | Karşılanma Durumu |
|---|---|
| Python 3.10+ | ✓ `match-case` ve `X \| None` type hint kullanılıyor |
| En az 2 anlamlı sınıf | ✓ 5 sınıf: MenuItem, SiparisKalemi, Siparis, Masa, Restoran |
| Veri kalıcılığı | ✓ JSON ile `to_dict` / `from_dict` döngüsü |
| Hata yönetimi | ✓ `try/except` — ValueError, OSError, KeyboardInterrupt |
| Modüler yapı | ✓ 3 ayrı `.py` dosyası |
| Standart kütüphane | ✓ `json`, `os`, `uuid`, `datetime` |
| Algoritma akış şeması | ✓ `flowchart.png` (README'den bağlantı: aşağıda) |
| README.md | ✓ Bu dosya |

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python **3.10** veya üzeri  
- Ek kütüphane gerekmez (yalnızca standart kütüphane kullanılmıştır)

### Çalıştırma

```bash
# 1. Repoyu klonla
git clone https://github.com/KULLANICI_ADI/restoran-siparis-sistemi.git
cd restoran-siparis-sistemi

# 2. Programı başlat
python main.py
```

İlk çalıştırmada `restoran_verisi.json` otomatik oluşturulur ve 20 örnek ürün ile 8 masa yüklenir.

---

## 🖥 Kullanım Örneği

```
════════════════════════════════════════════════════════════
  🏪  Türk Mutfağı Restoranı — Yönetim Paneli
════════════════════════════════════════════════════════════

  ── Sipariş İşlemleri ────────────────────────
   1) Yeni sipariş aç
   2) Siparişe kalem ekle
   5) Hesap kes
  ...

  Seçiminiz: 1
  Masa numarası: 3
  ✓ Masa 3 için sipariş açıldı. (ID: a1b2c3d4)

  Seçiminiz: 2
  Masa numarası: 3
  Ürün ID: abc12345        ← Iskender Kebap
  Adet: 2
  ✓ 2× Iskender Kebap eklendi

  Seçiminiz: 5
  ════════════════════════════════════════════════════════
           Türk Mutfağı Restoranı
                  FİNAL ADİSYON
  ────────────────────────────────────────────────────────
  Iskender Kebap               x2        616,00 ₺
  ────────────────────────────────────────────────────────
  Ara Toplam                             560,00 ₺
  KDV (%10)                               56,00 ₺
  ════════════════════════════════════════════════════════
  GENEL TOPLAM                           616,00 ₺
  ════════════════════════════════════════════════════════
```

---

## 📊 Algoritma Akış Şeması

![Akış Şeması](flowchart.png)

**Özet akış:**

```
BAŞLA
  └─► JSON yükle  (yoksa → örnek veri oluştur)
  └─► Ana menü döngüsü
        ├─► Sipariş aç   → masa boş mu? → Siparis() + Masa.doldur()
        ├─► Kalem ekle   → menü göster → ID+adet → siparis.kalem_ekle()
        ├─► Kalem çıkar  → ID → siparis.kalem_kaldir()
        ├─► Hesap kes    → adisyon → onay → siparis.kapat() + masa.bosalt()
        ├─► Rapor        → kapalı siparişler → ciro + en çok satan
        └─► Çıkış        → JSON kaydet → BİTİŞ
```

---

## 🗄 Veri Yapısı (JSON)

```json
{
  "menu": [
    { "id": "a1b2c3d4", "ad": "Iskender Kebap", "kategori": "Ana Yemek",
      "fiyat": 280.0, "mevcut": true }
  ],
  "masalar": [
    { "numara": 3, "kapasite": 4, "durum": "boş", "aktif_siparis_id": null }
  ],
  "siparisler": [
    { "id": "x9y8z7w6", "masa_no": 3, "durum": "kapalı",
      "acilis_zamani": "2025-06-01 19:30:00",
      "kapanis_zamani": "2025-06-01 20:15:00",
      "kalemler": [{ "menu_id": "a1b2c3d4", "adet": 2 }] }
  ]
}
```

---

## 👤 Geliştirici

| | |
|---|---|
| **Ders** | İleri Programlama |
| **Öğretim Üyesi** | Dr. Uğur Sırvermez |
| **Dil** | Python 3.10+ |
| **Lisans** | MIT |
