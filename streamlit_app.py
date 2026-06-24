import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import json
import os
from typing import List, Dict, Optional

VERI_DOSYASI = "restoran_verisi.json"
AYIRICI_INCE = "─" * 50

def para_formatla(tutar: float) -> str:
    return f"₺{tutar:,.2f}"

def veri_yukle(dosya: str) -> dict:
    if os.path.exists(dosya):
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def veri_kaydet(veri: dict, dosya: str) -> bool:
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

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
st.set_page_config(page_title="Ana Mutfak POS", layout="wide", page_icon="🍽️")

if 'restoran' not in st.session_state:
    restoran = type('Restoran', (), {})() 
    restoran.ad = "Ana Mutfak"
    restoran.menu: List[MenuItem] = []
    restoran.masalar: List[Masa] = []
    restoran.siparisler: List[Siparis] = []

    veri = veri_yukle(VERI_DOSYASI)
    if veri:
        restoran.menu = [MenuItem.from_dict(m) for m in veri.get("menu", [])]
        restoran.masalar = [Masa.from_dict(m) for m in veri.get("masalar", [])]
        restoran.siparisler = [
            Siparis.from_dict(s, restoran.menu) for s in veri.get("siparisler", [])
        ]
    else:
        ornek_menu = [
            ("Mercimek Çorbası", "Çorba", 65.00), ("Domates Çorbası", "Çorba", 55.00),
            ("Ezogelin Çorbası", "Çorba", 60.00), ("Iskender Kebap", "Ana Yemek", 280.00),
            ("Adana Kebap", "Ana Yemek", 260.00), ("Urfa Kebap", "Ana Yemek", 255.00),
            ("Kuzu Tandır", "Ana Yemek", 320.00), ("Künefe", "Tatlı", 130.00),
            ("Sütlaç", "Tatlı", 85.00), ("Çay", "İçecek", 25.00),
            ("Türk Kahvesi", "İçecek", 45.00), ("Ayran", "İçecek", 30.00),
            ("Su (0.5L)", "İçecek", 15.00),
        ]
        for ad, kat, fiyat in ornek_menu:
            restoran.menu.append(MenuItem(ad, kat, fiyat))

        for i in range(1, 9):
            kapasite = 2 if i <= 2 else (6 if i >= 7 else 4)
            restoran.masalar.append(Masa(i, kapasite))

        veri = {
            "menu": [m.to_dict() for m in restoran.menu],
            "masalar": [m.to_dict() for m in restoran.masalar],
            "siparisler": []
        }
        veri_kaydet(veri, VERI_DOSYASI)

    st.session_state.restoran = restoran

restoran = st.session_state.restoran

st.title("🍽️ Ana Mutfak — Restoran Yönetim Sistemi")
st.markdown("**Profesyonel Sipariş ve Masa Takip Sistemi**")

# Sidebar Navigation
secim = st.sidebar.selectbox(
    "📋 Ana Menü",
    [
        "🏠 Ana Sayfa",
        "📋 Masa Durumu",
        "🍽️ Menü",
        "➕ Yeni Sipariş Aç",
        "📝 Kalem Ekle",
        "➖ Kalem Çıkar",
        "👀 Sipariş Görüntüle",
        "💰 Hesap Kes",
        "📊 Satış Raporu",
        "⚙️ Menü Yönetimi"
    ]
)

def kaydet():
    veri = {
        "menu": [m.to_dict() for m in restoran.menu],
        "masalar": [m.to_dict() for m in restoran.masalar],
        "siparisler": [s.to_dict() for s in restoran.siparisler],
    }
    veri_kaydet(veri, VERI_DOSYASI)

# ======================= HALAMAN-HALAMAN =======================

if secim == "🏠 Ana Sayfa":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Masa", len(restoran.masalar))
    with col2:
        acik = sum(1 for s in restoran.siparisler if s.durum == "açık")
        st.metric("Açık Sipariş", acik)
    with col3:
        kapali = sum(1 for s in restoran.siparisler if s.durum == "kapalı")
        st.metric("Kapalı Sipariş", kapali)

    st.info("👈 Sidebar'dan işlem seçin")

elif secim == "📋 Masa Durumu":
    st.subheader("Masa Durumu")
    data = []
    for m in restoran.masalar:
        sip = next((s for s in restoran.siparisler if s.id == m.aktif_siparis_id), None)
        data.append({
            "Masa No": m.numara,
            "Durum": m.durum.upper(),
            "Kapasite": f"{m.kapasite} Kişi",
            "Aktif Sipariş": m.aktif_siparis_id or "-",
            "Açılış": sip.acilis_zamani if sip else "-"
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif secim == "🍽️ Menü":
    st.subheader("Menü")
    gruplar = {}
    for item in restoran.menu:
        if item.mevcut:
            gruplar.setdefault(item.kategori, []).append(item)

    for kat, items in gruplar.items():
        st.markdown(f"**{kat}**")
        menu_df = pd.DataFrame([{
            "ID": i.id,
            "Ürün": i.ad,
            "Fiyat": para_formatla(i.fiyat)
        } for i in items])
        st.dataframe(menu_df, use_container_width=True, hide_index=True)
        st.divider()

elif secim == "➕ Yeni Sipariş Aç":
    st.subheader("Yeni Sipariş Aç")
    masa_no = st.number_input("Masa Numarası", min_value=1, max_value=8, value=1)

    masa = next((m for m in restoran.masalar if m.numara == masa_no), None)
    if masa and masa.durum == "dolu":
        st.error(f"Masa {masa_no} dolu!")
    else:
        if st.button("Siparişi Aç", type="primary"):
            siparis = Siparis(masa_no)
            masa.doldur(siparis.id) if masa else None
            restoran.siparisler.append(siparis)
            kaydet()
            st.success(f"Sipariş açıldı! ID: {siparis.id}")
            st.rerun()

elif secim == "📝 Kalem Ekle":
    st.subheader("Siparişe Kalem Ekle")
    masa_no = st.number_input("Masa Numarası", min_value=1, max_value=8, value=1, key="add_masa")

    siparis = next((s for s in restoran.siparisler if s.masa_no == masa_no and s.durum == "açık"), None)

    if not siparis:
        st.warning("Bu masada aktif sipariş yok.")
    else:
        st.write(f"**Masa {masa_no} - Sipariş: {siparis.id}**")
        menu_sec = st.selectbox("Ürün Seç", options=[f"{m.id} - {m.ad} ({para_formatla(m.fiyat)})" for m in restoran.menu if m.mevcut])
        adet = st.number_input("Adet", min_value=1, max_value=20, value=1)

        if st.button("Ekle"):
            menu_id = menu_sec.split(" - ")[0]
            menu_item = next((m for m in restoran.menu if m.id == menu_id), None)
            if menu_item:
                siparis.kalem_ekle(menu_item, adet)
                kaydet()
                st.success(f"{adet}x {menu_item.ad} eklendi")
                st.rerun()

elif secim == "➖ Kalem Çıkar":
    st.subheader("Kalem Çıkar")
    dolu_masalar = [m.numara for m in restoran.masalar if m.durum == "dolu"]
        if not dolu_masalar:
            st.info("Ürün çıkarılabilecek dolu masa bulunmuyor.")
        else:
            masa_no = st.selectbox("Masa Numarası", dolu_masalar)
            siparis = restoran._aktif_siparis(masa_no)
            if not siparis:
                st.error("Seçilen masanın açık siparişi yok.")
            else:
                st.write("\nMevcut sipariş kalemleri:")
                for k in siparis.kalemler:
                    st.write(f"- {k.menu_kalemi.ad} x{k.adet}")

                kalem_ids = [k.menu_kalemi.id for k in siparis.kalemler]
                silinecek = st.selectbox("Çıkarılacak ürün", kalem_ids)
                adet_str = st.text_input("Çıkarılacak adet (boş bırakılırsa tümü silinir)")
                if st.button("Çıkar"):
                    adet = None
                    if adet_str.strip():
                        try:
                            adet = int(adet_str)
                        except ValueError:
                            st.error("Geçersiz adet değeri.")
                            st.stop()
                    restoran.kalem_kaldir(masa_no, silinecek, adet)
                    st.rerun()

elif secim == "👀 Sipariş Görüntüle":
    st.subheader("Sipariş Görüntüle")
    masa_no = st.number_input("Masa Numarası", min_value=1, max_value=8, value=1, key="view_masa")
    siparis = next((s for s in restoran.siparisler if s.masa_no == masa_no and s.durum == "açık"), None)

    if siparis:
        st.write(f"**Masa: {siparis.masa_no} | Sipariş: {siparis.id}**")
        df = pd.DataFrame([{
            "Ürün": k.menu_kalemi.ad,
            "Adet": k.adet,
            "Tutar": para_formatla(k.toplam)
        } for k in siparis.kalemler])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.metric("Genel Toplam", para_formatla(siparis.genel_toplam))
    else:
        st.warning("Aktif sipariş bulunamadı.")

elif secim == "💰 Hesap Kes":
    st.subheader("Hesap Kes")
    masa_no = st.number_input("Masa Numarası", min_value=1, max_value=8, value=1, key="kes_masa")
    siparis = next((s for s in restoran.siparisler if s.masa_no == masa_no and s.durum == "açık"), None)

    if siparis and siparis.kalemler:
        st.write("**Adisyon**")
        df = pd.DataFrame([{
            "Ürün": k.menu_kalemi.ad,
            "Adet": k.adet,
            "Tutar": para_formatla(k.toplam)
        } for k in siparis.kalemler])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.metric("Ara Toplam", para_formatla(siparis.açıklama))
        st.metric("KDV %10", para_formatla(siparis.kdv))
        st.metric("**GENEL TOPLAM**", para_formatla(siparis.genel_toplam), delta="KDV Dahil")

        if st.button("✅ Hesabı Kes ve Masayı Boşalt", type="primary"):
            siparis.kapat()
            masa = next((m for m in restoran.masalar if m.numara == masa_no), None)
            if masa:
                masa.bosalt()
            kaydet()
            st.success(f"Hesap kesildi! Masa {masa_no} boşaltıldı. Teşekkürler!")
            st.rerun()
    else:
        st.warning("Aktif sipariş bulunamadı.")

elif secim == "📊 Satış Raporu":
    st.subheader("Satış Raporu")
    kapali = [s for s in restoran.siparisler if s.durum == "kapalı"]
    ciro = sum(s.genel_toplam for s in kapali)

    col1, col2, col3 = st.columns(3)
    col1.metric("Kapalı Sipariş", len(kapali))
    col2.metric("Toplam Ciro", para_formatla(ciro))

    if kapali:
        # En çok satan
        sayim = {}
        for s in kapali:
            for k in s.kalemler:
                sayim[k.menu_kalemi.ad] = sayim.get(k.menu_kalemi.ad, 0) + k.adet

        st.markdown("**En Çok Satan Ürünler**")
        top5 = sorted(sayim.items(), key=lambda x: x[1], reverse=True)[:5]
        df_top = pd.DataFrame(top5, columns=["Ürün", "Adet"])
        st.dataframe(df_top, use_container_width=True, hide_index=True)

        st.markdown("**Son 5 Adisyon**")
        son5 = pd.DataFrame([{
            "ID": s.id,
            "Masa": s.masa_no,
            "Toplam": para_formatla(s.genel_toplam),
            "Kapanış": s.kapanis_zamani
        } for s in kapali[-5:]])
        st.dataframe(son5, use_container_width=True, hide_index=True)

elif secim == "⚙️ Menü Yönetimi":
    st.subheader("Menü Yönetimi")
    tab1, tab2 = st.tabs(["Yeni Ürün Ekle", "Ürün Düzenle"])

    with tab1:
        ad = st.text_input("Ürün Adı")
        kategori = st.text_input("Kategori")
        fiyat = st.number_input("Fiyat (₺)", min_value=1.0, value=50.0)

        if st.button("Menüye Ekle"):
            if ad and kategori:
                yeni = MenuItem(ad, kategori, fiyat)
                restoran.menu.append(yeni)
                kaydet()
                st.success(f"✅ {ad} eklendi!")
                st.rerun()

    with tab2:
        if restoran.menu:
            menu_sec = st.selectbox("Düzenlenecek Ürün", options=[f"{m.id} - {m.ad}" for m in restoran.menu])
            menu_id = menu_sec.split(" - ")[0]
            kalem = next((m for m in restoran.menu if m.id == menu_id), None)

            if kalem:
                yeni_fiyat = st.number_input("Yeni Fiyat", value=kalem.fiyat)
                if st.button("Fiyat Güncelle"):
                    kalem.fiyat = yeni_fiyat
                    kaydet()
                    st.success("Fiyat güncellendi")
                    st.rerun()

                if st.button("Görünürlüğü Değiştir"):
                    kalem.mevcut = not kalem.mevcut
                    kaydet()
                    st.success(f"Ürün şimdi {'görünür' if kalem.mevcut else 'gizli'}")
                    st.rerun()
