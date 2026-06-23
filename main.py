"""
main.py — Ana Program
Restoran Sipariş Sistemi — Giriş noktası.
"""
import streamlit as st
from models import MenuItem, Masa, Siparis
from utils import (
    baslik_yazdir, bolum_yazdir,
    para_formatla, giris_al, onayla,
    veri_yukle, veri_kaydet,
    VERI_DOSYASI, AYIRICI_INCE, AYIRICI_KALIN,
)


class Restoran:
    """
    Restoran yönetim sistemi ana sınıfı.

    Bu sınıf, aşağıdaki nesneleri yönetir:
      - menu     : MenuItem listesi
      - masalar  : Masa listesi
      - siparisler: Siparis listesi (açık ve kapalı)

    Tüm değişiklikler anında JSON dosyasına yansıtılır.
    """

    def __init__(self, ad: str = "Ana Mutfak"):
        self.ad = ad
        self.menu: list[MenuItem] = []
        self.masalar: list[Masa] = []
        self.siparisler: list[Siparis] = []
        self._veri_yukle()

    # ─── Veri Kalıcılığı ──────────────────────────────────────

    def _veri_yukle(self) -> None:
        """JSON dosyasından menü, masa ve sipariş verilerini yükler."""
        veri = veri_yukle(VERI_DOSYASI)
        if not veri:
            self._varsayilan_verileri_olustur()
            return

        self.menu = [MenuItem.from_dict(m) for m in veri.get("menu", [])]
        self.masalar = [Masa.from_dict(m) for m in veri.get("masalar", [])]
        self.siparisler = [
            Siparis.from_dict(s, self.menu)
            for s in veri.get("siparisler", [])
        ]
        print(f"\n   Veriler yüklendi "
              f"({len(self.menu)} ürün · {len(self.masalar)} masa · "
              f"{sum(1 for s in self.siparisler if s.durum == 'açık')} açık sipariş)")

    def _veri_kaydet_tum(self) -> None:
        """Tüm veriyi JSON dosyasına yazar."""
        veri = {
            "menu":       [m.to_dict() for m in self.menu],
            "masalar":    [m.to_dict() for m in self.masalar],
            "siparisler": [s.to_dict() for s in self.siparisler],
        }
        if veri_kaydet(veri, VERI_DOSYASI):
            print("   Veriler kaydedildi. ")

    def _varsayilan_verileri_olustur(self) -> None:
        """
        İlk çalıştırmada örnek menü ve masa verileri oluşturur.
        Gerçek bir kurulumda bu veriler yönetici tarafından girilir.
        """
        ornek_menu = [
            # (Ad,                    Kategori,      Fiyat)
            ("Mercimek Çorbası",     "Çorba",        65.00),
            ("Domates Çorbası",      "Çorba",        55.00),
            ("Ezogelin Çorbası",     "Çorba",        60.00),
            ("Iskender Kebap",       "Ana Yemek",   280.00),
            ("Adana Kebap",          "Ana Yemek",   260.00),
            ("Urfa Kebap",           "Ana Yemek",   255.00),
            ("Kuzu Tandır",          "Ana Yemek",   320.00),
            ("Künefe",               "Tatlı",       130.00),
            ("Sütlaç",               "Tatlı",        85.00),
            ("Çay",                  "İçecek",       25.00),
            ("Türk Kahvesi",         "İçecek",       45.00),
            ("Ayran",                "İçecek",       30.00),
            ("Su (0.5L)",            "İçecek",       15.00),
        ]
        for ad, kat, fiyat in ornek_menu:
            self.menu.append(MenuItem(ad, kat, fiyat))

        # 2 kişilik: 1-2, 4 kişilik: 3-6, 6 kişilik: 7-8
        for i in range(1, 9):
            kapasite = 2 if i <= 2 else (6 if i >= 7 else 4)
            self.masalar.append(Masa(i, kapasite))

        self._veri_kaydet_tum()
        print("   Örnek veriler oluşturuldu (13 ürün, 8 masa). ")

    # ─── Yardımcı Arama Metotları ─────────────────────────────

    def _menu_bul(self, item_id: str) -> MenuItem | None:
        return next((m for m in self.menu if m.id == item_id), None)

    def _masa_bul(self, masa_no: int) -> Masa | None:
        return next((m for m in self.masalar if m.numara == masa_no), None)

    def _siparis_bul(self, siparis_id: str) -> Siparis | None:
        return next((s for s in self.siparisler if s.id == siparis_id), None)

    def _aktif_siparis(self, masa_no: int) -> Siparis | None:
        """Masanın açık siparişini bulur."""
        masa = self._masa_bul(masa_no)
        if masa and masa.aktif_siparis_id:
            return self._siparis_bul(masa.aktif_siparis_id)
        return None

    # ─── Menü Görüntüleme ─────────────────────────────────────

    def menu_goster(self) -> None:
        """Menüyü kategorilere göre gruplandırarak yazar."""
        baslik_yazdir(f"  {self.ad} — Menü ")

        # Kategorilere göre grupla (yalnızca mevcut ürünler)
        gruplar: dict[str, list[MenuItem]] = {}
        for kalem in self.menu:
            if kalem.mevcut:
                gruplar.setdefault(kalem.kategori, []).append(kalem)

        for kategori, kalemler in gruplar.items():
            bolum_yazdir(kategori)
            print(f"  {'ID':<10} {'Ürün Adı':<30} {'Fiyat':>10}")
            print(f"  {AYIRICI_INCE}")
            for k in kalemler:
                print(f"  {k.id:<10} {k.ad:<30} {para_formatla(k.fiyat):>10}")

    # ─── Masa Durumu ──────────────────────────────────────────

    def masa_listele(self) -> None:
        """Tüm masaların durumunu tablo biçiminde yazar."""
        baslik_yazdir("  Masa Durumu ")

        bos_sayisi  = sum(1 for m in self.masalar if m.durum == "boş")
        dolu_sayisi = sum(1 for m in self.masalar if m.durum == "dolu")
        rez_sayisi  = sum(1 for m in self.masalar if m.durum == "rezerveli")

        print(f"\n  Toplam {len(self.masalar)} masa  │  "
              f"o Boş: {bos_sayisi}  │  x Dolu: {dolu_sayisi}  │  v Rezerveli: {rez_sayisi}")

        print(f"\n  {'No':>4}  {'Durum':<12} {'Kap.':>5}  {'Sipariş ID':<12}  {'Açılış'}")
        print(f"  {AYIRICI_INCE}")
        for m in self.masalar:
            simge = {"boş": "o", "dolu": "x", "rezerveli": "v"}.get(m.durum, "?")
            sid = m.aktif_siparis_id or "—"
            acilis = ""
            if m.aktif_siparis_id:
                s = self._siparis_bul(m.aktif_siparis_id)
                acilis = s.acilis_zamani if s else ""
            print(f"  {m.numara:>4}  {simge} {m.durum:<10}  {m.kapasite:>2}K  "
                  f"{sid:<12}  {acilis}")

    # ─── Sipariş Aç ───────────────────────────────────────────

    def siparis_ac(self) -> None:
        """
        Boş bir masa için yeni sipariş açar.
        Masa dolu ise hata mesajı gösterir ve çökmez.
        """
        baslik_yazdir("  Yeni Sipariş Aç ")
        self.masa_listele()

        try:
            masa_no = giris_al("Masa numarası", int, 1)
        except KeyboardInterrupt:
            return

        masa = self._masa_bul(masa_no)
        if not masa:
            print(f"  ! Masa {masa_no} mevcut değil.")
            return
        if masa.durum == "dolu":
            print(f"  ! Masa {masa_no} zaten dolu. "
                  "Önce 'Hesap Kes' ile mevcut siparişi kapatın.")
            return

        siparis = Siparis(masa_no)
        masa.doldur(siparis.id)
        self.siparisler.append(siparis)
        self._veri_kaydet_tum()
        print(f"\n    Masa {masa_no} için sipariş açıldı. (ID: {siparis.id})")

        if onayla("Hemen kalem eklemek ister misiniz?"):
            self.kalem_ekle(masa_no=masa_no)

    # ─── Kalem Ekle ───────────────────────────────────────────

    def kalem_ekle(self, masa_no: int | None = None) -> None:
        """
        Açık siparişe menü kalemi ekler.
        Aynı ürün tekrar seçilirse adet toplanır.
        """
        baslik_yazdir("  Siparişe Kalem Ekle ")

        if masa_no is None:
            try:
                masa_no = giris_al("Masa numarası", int, 1)
            except KeyboardInterrupt:
                return

        siparis = self._aktif_siparis(masa_no)
        if not siparis:
            print(f"  ! Masa {masa_no}'de açık sipariş bulunamadı. "
                  "Önce '1) Yeni Sipariş Aç' seçeneğini kullanın.")
            return

        self.menu_goster()
        print(f"\n  (Çıkmak için 'q' girin)")

        while True:
            print(f"\n  {AYIRICI_INCE}")
            menu_id = input("  Ürün ID: ").strip()
            if menu_id.lower() == "q":
                break

            kalem = self._menu_bul(menu_id)
            if not kalem:
                print("  ! Bu ID'ye sahip ürün bulunamadı.")
                continue
            if not kalem.mevcut:
                print(f"  ! '{kalem.ad}' şu an mevcut değil.")
                continue

            try:
                adet = giris_al("Adet", int, 1, 50)
            except KeyboardInterrupt:
                break

            siparis.kalem_ekle(kalem, adet)
            print(f"   {adet}x {kalem.ad} eklendi ->  "
                  f"ara toplam: {para_formatla(siparis.ara_toplam)}")

        self._veri_kaydet_tum()
        print(f"\n  Sipariş güncellendi. "
              f"Genel toplam: {para_formatla(siparis.genel_toplam)}")

    # ─── Siparişi Görüntüle ───────────────────────────────────

    def siparis_goruntule(self) -> None:
        """Belirtilen masanın aktif siparişini adisyon formatında gösterir."""
        baslik_yazdir("  Sipariş Görüntüle ")
        try: 
            masa_no = giris_al("Masa numarası", int, 1)
        except KeyboardInterrupt:
            return

        siparis = self._aktif_siparis(masa_no)
        if not siparis:
            print(f"  ! Masa {masa_no}'de aktif sipariş bulunamadı.")
            return

        self._adisyon_yazdir(siparis, baslik="DETAY / ÖN İZLEME")

    # ─── Kalem Çıkar ──────────────────────────────────────────

    def kalem_kaldir(self) -> None:
        """Açık siparişten belirtilen miktarda ürünü çıkarır."""

        baslik_yazdir("  Siparişten Kalem Çıkar ")
        try:
            masa_no = giris_al("Masa numarası", int, 1)
        except KeyboardInterrupt:
            return

        siparis = self._aktif_siparis(masa_no)
        if not siparis:
            print(f"  ! Masa {masa_no}'de aktif sipariş yok.")
            return

        if not siparis.kalemler:
            print("  ! Sipariş zaten boş.")
            return

        self._siparis_kalemleri_listele(siparis)
        menu_id = input("\n  Çıkarılacak ürün ID: ").strip()

        kalem = next((k for k in siparis.kalemler
                      if k.menu_kalemi.id == menu_id), None)
        if not kalem:
            print("  ! nu ID sipariŞte bulunmadı. ")
            return
        
        mevcut_adet = kalem.adet
        urun_adi = kalem.menu_kalemi.ad
        print(f"    '{urun_adi}' için mevcut adet: {mevcut_adet}")

        secim = input(
            "  Çıkarılacak adet (boş bırakılırsa tümü silinir): "
        ).strip()

        if secim == "":
            adet = None
        else:
            try:
                adet = int(secim)
                if adet <= 0:
                    print("  ! Adet pozitif bir sayı olmalıdır. ")
                    return
            except ValueError:
                print("  ! Geçersiz adet girişi. ")
                return
        
        if siparis.kalem_kaldir(menu_id, adet):
            self._veri_kaydet_tum()
            if adet is None or adet >= mevcut_adet:
                print(f"    '{urun_adi}' siparişten tamamen silindi. ")
            else:
                kalan = mevcut_adet - adet
                print(f"    {adet}x '{urun_adi}' çıkarıldı. "
                      f"Kalan adet: {kalan}")
        else:
            print("  ! Bu ID siparişte bulunamadı.")
    
    def _siparis_kalemleri_listele(self, siparis: Siparis) -> None:
        print(f"\n  masa {siparis.masa_no} - Mevcut Siparis Kalemleri")
        print(f"    {'ID:<10'} {'Ürün':<28} {'Adet':>5}{'Tutar':>12}")
        print(f"    {AYIRICI_INCE}")
        for k in siparis.kalemler:
            print(f"    {k.menu_kalemi.id:<10} {k.menu_kalemi.ad:<28} "
                  f"{k.adet:>5} {para_formatla(k.toplam):>12}")

        
    # ─── Hesap Kes ────────────────────────────────────────────

    def hesap_kes(self) -> None:
        """
        Siparişi kapatır, adisyon yazdırır ve masayı boşaltır.
        Onay alınmadan işlem gerçekleşmez.
        """
        baslik_yazdir("  Hesap Kes ")
        try:
            masa_no = giris_al("Masa numarası", int, 1)
        except KeyboardInterrupt:
            return

        siparis = self._aktif_siparis(masa_no)
        if not siparis:
            print(f"  ! Masa {masa_no}'de aktif sipariş bulunamadı.")
            return
        if not siparis.kalemler:
            print("  ! Sipariş boş; hesap kesilemez.")
            return

        self._adisyon_yazdir(siparis, baslik="FİNAL ADİSYON")

        if onayla("Hesabı onaylıyor musunuz?"):
            siparis.kapat()
            masa = self._masa_bul(masa_no)
            if masa:
                masa.bosalt()
            self._veri_kaydet_tum()
            print(f"\n   Hesap kesildi. Masa {masa_no} boşaltıldı. ")
            print("  Teşekkür ederiz, iyi günler! ")

    def _adisyon_yazdir(self, siparis: Siparis, baslik: str = "ADİSYON") -> None:
        """
        Adisyon çıktısını konsola yazar.
        Hem ön izleme hem de hesap kesme için kullanılır.
        """
        genislik = 52
        cizgi_kalin = "═" * genislik
        cizgi_ince  = "─" * genislik

        print(f"\n  {cizgi_kalin}")
        print(f"  {self.ad:^{genislik}}")
        print(f"  {baslik:^{genislik}}")
        print(f"  {cizgi_ince}")
        print(f"  Masa: {siparis.masa_no:<6}  Sipariş No: {siparis.id}")
        print(f"  Açılış : {siparis.acilis_zamani}")
        if siparis.kapanis_zamani:
            print(f"  Kapanış: {siparis.kapanis_zamani}")
        print(f"  {cizgi_ince}")
        print(f"  {'Ürün':<28} {'Adet':>4} {'Tutar':>12}")
        print(f"  {'-'*28} {'-'*4} {'-'*12}")

        for k in siparis.kalemler:
            print(f"  {k.menu_kalemi.ad:<28} {k.adet:>4} "
                  f"{para_formatla(k.toplam):>12}")

        print(f"  {cizgi_ince}")
        print(f"  {'Ara Toplam':>36} {para_formatla(siparis.açıklama):>12}")
        print(f"  {'KDV (%10)':>36} {para_formatla(siparis.kdv):>12}")
        print(f"  {cizgi_kalin}")
        print(f"  {'GENEL TOPLAM':>36} {para_formatla(siparis.genel_toplam):>12}")
        print(f"  {cizgi_kalin}")

    # ─── Menü Yönetimi ────────────────────────────────────────

    def menu_kalem_ekle(self) -> None:
        """Yönetici tarafından menüye yeni ürün eklenir."""
        baslik_yazdir("  Menüye Yeni Ürün Ekle ")

        ad = input("  Ürün adı      : ").strip()
        if not ad:
            print("  ! Ad boş bırakılamaz.")
            return

        # Mevcut kategorileri göster
        mevcut_katlar = sorted({m.kategori for m in self.menu})
        print(f"  Mevcut kategoriler: {', '.join(mevcut_katlar)}")
        kategori = input("  Kategori       : ").strip()
        if not kategori:
            print("  ! Kategori boş bırakılamaz.")
            return

        try:
            fiyat = giris_al("Fiyat (₺)", float, 0.01)
        except KeyboardInterrupt:
            return

        yeni = MenuItem(ad, kategori, fiyat)
        self.menu.append(yeni)
        self._veri_kaydet_tum()
        print(f"\n   '{ad}' menüye eklendi. (ID: {yeni.id}) ")

    def menu_kalem_duzenle(self) -> None:
        """Mevcut menü kalemine fiyat güncelleme veya gizleme işlemi yapar."""
        baslik_yazdir("   Menü Kalemi Düzenle ")
        self.menu_goster()

        menu_id = input("\n  Düzenlenecek ürün ID: ").strip()
        kalem = self._menu_bul(menu_id)
        if not kalem:
            print("  ! Bu ID'ye sahip ürün bulunamadı.")
            return

        print(f"\n  Seçilen ürün: {kalem.ad}  ->  {para_formatla(kalem.fiyat)}")
        print("  1) Fiyat güncelle")
        print("  2) Ürünü gizle / göster")
        secim = input("  Seçim (1/2): ").strip()

        if secim == "1":
            try:
                yeni_fiyat = giris_al("Yeni fiyat (₺)", float, 0.01)
            except KeyboardInterrupt:
                return
            kalem.fiyat = yeni_fiyat
            self._veri_kaydet_tum()
            print(f"   Fiyat güncellendi → {para_formatla(yeni_fiyat)}")

        elif secim == "2":
            kalem.mevcut = not kalem.mevcut
            durum_str = "görünür " if kalem.mevcut else "gizli "
            self._veri_kaydet_tum()
            print(f"   '{kalem.ad}' artık {durum_str}.")
        else:
            print("  ! Geçersiz seçim.")

    # ─── Satış Raporu ─────────────────────────────────────────

    def rapor_goster(self) -> None:
        """
        Toplam ciro, en çok satan ürünler ve son adisyonları gösterir.
        Yalnızca kapalı siparişler raporda yer alır.
        """
        baslik_yazdir("  Satış Raporu ")

        kapali  = [s for s in self.siparisler if s.durum == "kapalı"]
        acik    = [s for s in self.siparisler if s.durum == "açık"]
        ciro    = sum(s.genel_toplam for s in kapali)

        print(f"\n  Toplam kapalı sipariş  : {len(kapali)}")
        print(f"  Şu an açık sipariş     : {len(acik)}")
        print(f"  Kümülatif ciro (KDV li): {para_formatla(ciro)}")

        # En çok sipariş edilen 5 ürün
        sayim: dict[str, int] = {}
        for s in kapali:
            for k in s.kalemler:
                sayim[k.menu_kalemi.ad] = sayim.get(k.menu_kalemi.ad, 0) + k.adet

        if sayim:
            bolum_yazdir("En Çok Satan 5 Ürün")
            sirali = sorted(sayim.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  {'Sıra':<5} {'Ürün':<30} {'Toplam Adet':>12}")
            print(f"  {AYIRICI_INCE}")
            for sira, (ad, adet) in enumerate(sirali, 1):
                bar = "█" * min(adet, 20)
                print(f"  {sira:<5} {ad:<30} {adet:>6}  {bar}")

        # Son 5 kapalı adisyon
        if kapali:
            bolum_yazdir("Son 5 Kapalı Adisyon")
            print(f"  {'ID':<12} {'Masa':>5} {'K.Toplam':>12}  {'Kapanış'}")
            print(f"  {AYIRICI_INCE}")
            for s in kapali[-5:]:
                print(f"  {s.id:<12} {s.masa_no:>5} "
                      f"{para_formatla(s.genel_toplam):>12}  {s.kapanis_zamani}")
        else:
            print("\n  Henüz kapatılmış sipariş bulunmuyor.")

    # ─── Ana Döngü ────────────────────────────────────────────

    def calistir(self) -> None:
        """
        Ana program döngüsü.
        Kullanıcı '0' girene kadar menüyü tekrar tekrar gösterir.
        Beklenmedik hatalar yakalanır; program çökmez.
        """
        while True:
            baslik_yazdir(f"  {self.ad} — Yönetim Paneli ")
            print("""
  ── Sipariş İşlemleri ────────────────────────
   1) Yeni sipariş aç
   2) Siparişe kalem ekle
   3) Siparişten kalem çıkar
   4) Sipariş / adisyon görüntüle
   5) Hesap kes

  ── Görünüm ──────────────────────────────────
   6) Menüyü görüntüle
   7) Masa durumunu görüntüle
   8) Satış raporu

  ── Yönetim ──────────────────────────────────
   9) Menüye yeni ürün ekle
  10) Menü kalemi düzenle (fiyat / gizle)

   0) Çıkış
  ─────────────────────────────────────────────""")

            secim = input("  Seçiminiz: ").strip()

            try:
                match secim:
                    case "1":  self.siparis_ac()
                    case "2":  self.kalem_ekle()
                    case "3":  self.kalem_kaldir()
                    case "4":  self.siparis_goruntule()
                    case "5":  self.hesap_kes()
                    case "6":  self.menu_goster()
                    case "7":  self.masa_listele()
                    case "8":  self.rapor_goster()
                    case "9":  self.menu_kalem_ekle()
                    case "10": self.menu_kalem_duzenle()
                    case "0":
                        print("\n  Güle güle! Programı kapanıyor... \n")
                        break
                    case _:
                        print("  ! Geçersiz seçim. Lütfen 0-10 arası bir sayı girin.")
            except KeyboardInterrupt:
                print("\n\n  Ctrl+C algılandı. Program sonlandırıldı.")
                break
            except Exception as e:
                # Beklenmedik hatalar programı çökertmez
                print(f"\n  ! Beklenmedik bir hata oluştu: {e}")
                print("  Lütfen tekrar deneyin veya geliştiriciyle iletişime geçin.")

            input("\n  ── [Enter] ile devam edin ──")


# ─── Giriş Noktası ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    restoran = Restoran("Ana Mutfak")
    restoran.calistir()
