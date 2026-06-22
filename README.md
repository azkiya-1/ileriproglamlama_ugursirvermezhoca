```mermaid
flowchart TD
    Start[BAŞLA] --> Load[Veri Yükle / Örnek Oluştur]
    Load --> Menu[Ana Menü]
    Menu --> Secim{Seçim}
    Secim -->|1-5| SiparisIslemleri[Sipariş İşlemleri\nAç - Ekle - Çıkar - Göster - Hesap Kes]
    Secim -->|6-7| Goruntule[Görüntüleme\nMenü & Masa]
    Secim -->|8| Rapor[Satış Raporu]
    Secim -->|9-10| Yonetim[Yönetim\nMenü Ekle/Düzenle]
    Secim -->|0| Cikis[Veri Kaydet → ÇIKIŞ]
    Kaydet1 --> MainMenu
    Cikis --> End[PROGRAM SONU]
