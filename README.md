```mermaid
flowchart TD
    Start[BAŞLA] 
    --> Load[Veri Yükle\nrestoran_verisi.json]

    Load --> Check{Veri Var mı?}
    Check -->|Hayır| Default[Örnek Veri Oluştur\n20 Ürün + 8 Masa]
    Check -->|Evet| LoadData[Veri Yükle\nMenu, Masalar, Siparişler]
    Default --> LoadData

    LoadData --> MainMenu[Ana Menü Göster]

    MainMenu --> Choice{Seçim Yap\n0 - 10}

    %% Sipariş İşlemleri
    Choice -->|1| YeniSiparis[1. Yeni Sipariş Aç]
    Choice -->|2| KalemEkle[2. Kalem Ekle]
    Choice -->|3| KalemCikar[3. Kalem Çıkar]
    Choice -->|4| Goruntule[4. Sipariş Görüntüle]
    Choice -->|5| HesapKes[5. Hesap Kes]

    %% Görünüm & Rapor
    Choice -->|6| MenuGoster[6. Menü Görüntüle]
    Choice -->|7| MasaDurum[7. Masa Durumu]
    Choice -->|8| Rapor[8. Satış Raporu]

    %% Yönetim
    Choice -->|9| UrunEkle[9. Yeni Ürün Ekle]
    Choice -->|10| UrunDuzenle[10. Ürün Düzenle]

    Choice -->|0| Cikis[Veri Kaydet → ÇIKIŞ]

    %% Detail Flow
    YeniSiparis --> MasaKontrol{Masa Boş mu?}
    MasaKontrol -->|Hayır| Hata1["Masa zaten dolu!"]
    MasaKontrol -->|Evet| SiparisOlustur[Sipariş Oluştur\n+ Masa Dolu Yap]
    SiparisOlustur --> KalemSor{Kalem eklemek ister misin?}
    KalemSor -->|Evet| KalemEkle
    KalemSor -->|Hayır| Kaydet1[Veri Kaydet]

    KalemEkle --> AktifKontrol{Aktif Sipariş Var mı?}
    AktifKontrol -->|Evet| MenuShow[Menü Göster → ID + Adet → Ekle]
    AktifKontrol -->|Hayır| Hata2["Aktif sipariş yok!"]

    HesapKes --> FinalAdisyon[Final Adisyon Göster]
    FinalAdisyon --> Onay{Onay Verildi mi?}
    Onay -->|Evet| Kapat[Siparişi Kapat\nMasa Boşalt]
    Onay -->|Hayır| Kaydet1

    Kapat --> Kaydet1
    MenuShow --> Kaydet1
    KalemCikar --> Kaydet1

    Hata1 --> MainMenu
    Hata2 --> MainMenu
    Kaydet1 --> MainMenu
    Cikis --> End[PROGRAM SONU]
