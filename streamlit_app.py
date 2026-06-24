import streamlit_app as st
import pandas as pd
import json
import os
from datetime import datetime
import uuid

VERI_DOSYASI = "restoran_verisi.json"

def para_formatla(tutar):
    return f"₺{tutar:,.2f}"

def veri_yukle(dosya):
    if os.path.exists(dosya):
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def veri_kaydet(veri, dosya):
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ==================== MODELS ====================
class MenuItem:
    def __init__(self, ad, kategori, fiyat):
        self.id = f"{str(uuid.uuid4())[:4].upper()}"
        self.ad = ad
        self.kategori = kategori
        self.fiyat = fiyat
        self.mevcut = True

    @classmethod
    def from_dict(cls, data):
        item = cls(data["ad"], data["kategori"], data["fiyat"])
        item.id = data.get("id", item.id)
        item.mevcut = data.get("mevcut", True)
        return item

    def to_dict(self):
        return {"id": self.id, "ad": self.ad, "kategori": self.kategori, 
                "fiyat": self.fiyat, "mevcut": self.mevcut}

class Masa:
    def __init__(self, numara, kapasite):
        self.numara = numara
        self.kapasite = kapasite
        self.durum = "boş"
        self.aktif_siparis_id = None

    @classmethod
    def from_dict(cls, data):
        masa = cls(data["numara"], data["kapasite"])
        masa.durum = data.get("durum", "boş")
        masa.aktif_siparis_id = data.get("aktif_siparis_id")
        return masa

    def to_dict(self):
        return {"numara": self.numara, "kapasite": self.kapasite, 
                "durum": self.durum, "aktif_siparis_id": self.aktif_siparis_id}

    def doldur(self, siparis_id):
        self.durum = "dolu"
        self.aktif_siparis_id = siparis_id

    def bosalt(self):
        self.durum = "boş"
        self.aktif_siparis_id = None

class SiparisKalemi:
    def __init__(self, menu_kalemi, adet):
        self.menu_kalemi = menu_kalemi
        self.adet = adet

    @property
    def toplam(self):
        return self.menu_kalemi.fiyat * self.adet

    def to_dict(self):
        return {"menu_id": self.menu_kalemi.id, "adet": self.adet}

class Siparis:
    def __init__(self, masa_no):
        self.id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        self.masa_no = masa_no
        self.kalemler = []
        self.durum = "açık"
        self.acilis_zamani = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.kapanis_zamani = None

    @classmethod
    def from_dict(cls, data, menu):
        siparis = cls(data["masa_no"])
        siparis.id = data["id"]
        siparis.durum = data.get("durum", "açık")
        siparis.acilis_zamani = data.get("acilis_zamani")
        siparis.kapanis_zamani = data.get("kapanis_zamani")

        menu_dict = {m.id: m for m in menu}
        for k in data.get("kalemler", []):
            menu_item = menu_dict.get(k.get("menu_id"))
            if menu_item:
                siparis.kalemler.append(SiparisKalemi(menu_item, k["adet"]))
        return siparis

    def to_dict(self):
        return {
            "id": self.id, "masa_no": self.masa_no, "durum": self.durum,
            "acilis_zamani": self.acilis_zamani, "kapanis_zamani": self.kapanis_zamani,
            "kalemler": [k.to_dict() for k in self.kalemler]
        }

    @property
    def ara_toplam(self):
        return sum(k.toplam for k in self.kalemler)

    @property
    def kdv(self):
        return self.ara_toplam * 0.10

    @property
    def genel_toplam(self):
        return self.ara_toplam + self.kdv

    def kalem_ekle(self, menu_kalemi, adet):
        for k in self.kalemler:
            if k.menu_kalemi.id == menu_kalemi.id:
                k.adet += adet
                return
        self.kalemler.append(SiparisKalemi(menu_kalemi, adet))

    def kalem_kaldir(self, menu_id):
        for i, k in enumerate(self.kalemler):
            if k.menu_kalemi.id == menu_id:
                del self.kalemler[i]
                return True
        return False

    def kapat(self):
        self.durum = "kapalı"
        self.kapanis_zamani = datetime.now().strftime("%d.%m.%Y %H:%M")

# ==================== STREAMLIT APP ====================
st.set_page_config(page_title="Ana Mutfak", layout="wide")

if 'restoran' not in st.session_state:
    restoran = type('obj', (object,), {})()
    restoran.menu = []
    restoran.masalar = []
    restoran.siparisler = []

    veri = veri_yukle(VERI_DOSYASI)
    if veri and veri.get("menu"):
        restoran.menu = [MenuItem.from_dict(m) for m in veri.get("menu", [])]
        restoran.masalar = [Masa.from_dict(m) for m in veri.get("masalar", [])]
        restoran.siparisler = [Siparis.from_dict(s, restoran.menu) for s in veri.get("siparisler", [])]
    else:
        # Default data
        ornek_menu = [
            ("Mercimek Çorbası", "Çorba", 65), ("Domates Çorbası", "Çorba", 55),
            ("Ezogelin Çorbası", "Çorba", 60), ("Iskender Kebap", "Ana Yemek", 280),
            ("Adana Kebap", "Ana Yemek", 260), ("Kuzu Tandır", "Ana Yemek", 320),
            ("Künefe", "Tatlı", 130), ("Çay", "İçecek", 25), ("Türk Kahvesi", "İçecek", 45)
        ]
        for ad, kat, fiyat in ornek_menu:
            restoran.menu.append(MenuItem(ad, kat, fiyat))

        for i in range(1, 9):
            kapasite = 2 if i <= 2 else 4
            restoran.masalar.append(Masa(i, kapasite))

        veri_kaydet({
            "menu": [m.to_dict() for m in restoran.menu],
            "masalar": [m.to_dict() for m in restoran.masalar],
            "siparisler": []
        }, VERI_DOSYASI)

    st.session_state.restoran = restoran

restoran = st.session_state.restoran

st.title("🍽️ Ana Mutfak Restoran Sistemi")

secim = st.sidebar.selectbox("Menu Utama", [
    "🏠 Beranda", "📋 Status Meja", "🍽️ Menu", "➕ Buka Pesanan Baru",
    "📝 Tambah Item", "💰 Tutup Bill"
])

st.success("✅ Aplikasi berhasil dimuat!")

if secim == "🏠 Beranda":
    st.info("Pilih menu di sebelah kiri (sidebar)")