"""
models.py — Veri Modelleri
Restoran Sipariş Sistemi için temel sınıflar:
  MenuItem       : Menüdeki bir ürün (yemek, içecek, vb.)
  SiparisKalemi  : Siparişe eklenen tek bir kalem (ürün + adet)
  Siparis        : Bir masanın açık veya kapalı siparişi
  Masa           : Restorandaki fiziksel masa
"""

import uuid
from datetime import datetime


class MenuItem:
    """
    Menüdeki bir ürünü temsil eder.

    Attributes:
        id       : Otomatik üretilen benzersiz kimlik (4 karakter)
        ad       : Ürün adı
        kategori : Ürün kategorisi (Çorba, Ana Yemek, Tatlı vb.)
        fiyat    : KDV dahil birim fiyat (₺)
        mevcut   : False ise menüde gösterilmez / sipariş alınamaz
    """

    def __init__(self, ad: str, kategori: str, fiyat: float,
                 item_id: str = None):
        self.id: str = item_id or str(uuid.uuid4())[:4]
        self.ad: str = ad
        self.kategori: str = kategori
        self.fiyat: float = fiyat
        self.mevcut: bool = True

    # ── Serileştirme ──────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "ad":       self.ad,
            "kategori": self.kategori,
            "fiyat":    self.fiyat,
            "mevcut":   self.mevcut,
        }

    @classmethod
    def from_dict(cls, veri: dict) -> "MenuItem":
        kalem = cls(veri["ad"], veri["kategori"], veri["fiyat"], veri["id"])
        kalem.mevcut = veri.get("mevcut", True)
        return kalem

    def __str__(self) -> str:
        durum = "v" if self.mevcut else "x"
        return (f"[{durum}] {self.id:<10} {self.ad:<28} "
                f"{self.kategori:<15} {self.fiyat:.2f} ₺")


# ─────────────────────────────────────────────────────────────────────────────


class SiparisKalemi:
    """
    Bir siparişe eklenen tek bir kalem (ürün + adet çifti).

    Attributes:
        menu_kalemi : İlgili MenuItem nesnesi
        adet        : Kaç adet sipariş edildiği >= 1)
    """

    def __init__(self, menu_kalemi: MenuItem, adet: int = 1):
        self.menu_kalemi: MenuItem = menu_kalemi
        self.adet: int = adet

    @property
    def toplam(self) -> float:
        """Bu kalemin toplam tutarı (birim fiyat x adet)."""
        return self.menu_kalemi.fiyat * self.adet

    # ── Serileştirme ──────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"menu_id": self.menu_kalemi.id, "adet": self.adet}

    def __str__(self) -> str:
        return (f"  {self.menu_kalemi.ad:<28} x{self.adet:<3} "
                f"{self.toplam:>10.2f} ₺")


# ─────────────────────────────────────────────────────────────────────────────


class Siparis:

    KDV_ORANI = 0.10   # %10

    def __init__(self, masa_no: int, siparis_id: str = None):
        self.id: str = siparis_id or str(uuid.uuid4())[:8]
        self.masa_no: int = masa_no
        self.kalemler: list[SiparisKalemi] = []
        self.durum: str = "açık"
        self.acilis_zamani: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.kapanis_zamani: str | None = None

    # ── Kalem İşlemleri ───────────────────────────────────────

    def kalem_ekle(self, menu_kalemi: MenuItem, adet: int = 1) -> None:
        """
        Siparişe kalem ekler.
        Aynı ürün zaten varsa adetini artırır; yoksa yeni kalem oluşturur.
        """
        for k in self.kalemler:
            if k.menu_kalemi.id == menu_kalemi.id:
                k.adet += adet
                return
        self.kalemler.append(SiparisKalemi(menu_kalemi, adet))

    def kalem_kaldir(self, menu_id: str, adet: int | None = None) -> bool:
        """
        Belirtilen menu_id'ye sahip kalemden adet kadar çıkarır.
        """
        for i, k in enumerate(self.kalemler):
            if k.menu_kalemi.id == menu_id:
                if adet is None or adet >= k.adet:
                    self.kalemler.pop(i)
                else:
                    k.adet -= adet
                return True
        return False

    # ── Tutar Hesaplamaları ───────────────────────────────────

    @property
    def ara_toplam(self) -> float:
        """toplam."""
        return sum(k.toplam for k in self.kalemler)
    
    @property
    def kdv(self) -> float:
        """Hesaplanan KDV tutarı."""
        return self.ara_toplam * self.KDV_ORANI
    
    @property
    def açıklama(self) -> float:
        """KDV hariç tutar"""
        return self.ara_toplam - self.kdv

    @property
    def genel_toplam(self) -> float:
        """KDV dahil ödenecek tutar."""
        return self.ara_toplam

    # ── Durum Yönetimi ────────────────────────────────────────

    def kapat(self) -> None:
        """Siparişi kapatır ve kapanış zamanını kaydeder."""
        self.durum = "kapalı"
        self.kapanis_zamani = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Serileştirme ──────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "masa_no":        self.masa_no,
            "kalemler":       [k.to_dict() for k in self.kalemler],
            "durum":          self.durum,
            "acilis_zamani":  self.acilis_zamani,
            "kapanis_zamani": self.kapanis_zamani,
        }

    @classmethod
    def from_dict(cls, veri: dict, menu_listesi: list) -> "Siparis":
        siparis = cls(veri["masa_no"], veri["id"])
        siparis.durum = veri["durum"]
        siparis.acilis_zamani = veri["acilis_zamani"]
        siparis.kapanis_zamani = veri.get("kapanis_zamani")

        menu_map = {m.id: m for m in menu_listesi}
        for k_veri in veri.get("kalemler", []):
            if k_veri["menu_id"] in menu_map:
                siparis.kalemler.append(
                    SiparisKalemi(menu_map[k_veri["menu_id"]], k_veri["adet"])
                )
        return siparis


# ─────────────────────────────────────────────────────────────────────────────


class Masa:
    """
    Restorandaki fiziksel bir masayı temsil eder.

    Attributes:
        numara           : Masa numarası (benzersiz)
        kapasite         : Maksimum oturabilecek kişi sayısı
        durum            : 'boş' | 'dolu' | 'rezerveli'
        aktif_siparis_id : Masa doluyken açık siparişin ID'si
    """

    GECERLI_DURUMLAR = frozenset({"boş", "dolu", "rezerveli"})

    def __init__(self, numara: int, kapasite: int = 4):
        self.numara: int = numara
        self.kapasite: int = kapasite
        self.durum: str = "boş"
        self.aktif_siparis_id: str | None = None

    # ── Durum Yönetimi ────────────────────────────────────────

    def doldur(self, siparis_id: str) -> None:
        """Masayı dolu olarak işaretler ve siparişle ilişkilendirir."""
        self.durum = "dolu"
        self.aktif_siparis_id = siparis_id

    def bosalt(self) -> None:
        """Masayı boşaltır, sipariş bağlantısını kaldırır."""
        self.durum = "boş"
        self.aktif_siparis_id = None

    # ── Serileştirme ──────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "numara":           self.numara,
            "kapasite":         self.kapasite,
            "durum":            self.durum,
            "aktif_siparis_id": self.aktif_siparis_id,
        }

    @classmethod
    def from_dict(cls, veri: dict) -> "Masa":
        masa = cls(veri["numara"], veri["kapasite"])
        masa.durum = veri.get("durum", "boş")
        masa.aktif_siparis_id = veri.get("aktif_siparis_id")
        return masa

    def __str__(self) -> str:
        simge = {"boş": "○", "dolu": "●", "rezerveli": "◎"}.get(self.durum, "?")
        sid = self.aktif_siparis_id or "—"
        return (f"  Masa {self.numara:>2}  {simge} {self.durum:<10} "
                f" {self.kapasite} kişilik   sipariş: {sid}")
