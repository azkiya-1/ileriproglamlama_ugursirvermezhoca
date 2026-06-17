"""
utils.py — Yardımcı Fonksiyonlar
Dosya I/O, güvenli girdi okuma ve ekran formatlama araçları.
"""

import json
import os

VERI_DOSYASI = "restoran_verisi.json"
AYIRICI_INCE = "─" * 60
AYIRICI_KALIN = "═" * 60


# ─── Ekran Formatlama ─────────────────────────────────────────────────────────


def ekrani_temizle() -> None:
    """Terminal ekranını temizler (Windows/Linux/macOS uyumlu)."""
    os.system("cls" if os.name == "nt" else "clear")


def baslik_yazdir(metin: str) -> None:
    """Kalın çizgilerle çevrelenmiş başlık yazar."""
    print(f"\n{AYIRICI_KALIN}")
    print(f"  {metin}")
    print(AYIRICI_KALIN)


def bolum_yazdir(metin: str) -> None:
    """Alt bölüm başlığı yazar."""
    print(f"\n  ── {metin} {'─' * (44 - len(metin))}")


def para_formatla(tutar: float) -> str:
    """
    Sayıyı Türk Lirası formatında döndürür.
    Örnek: 1234.5 → '1.234,50 ₺'
    """
    return f"{tutar:,.2f} ₺".replace(",", "X").replace(".", ",").replace("X", ".")


def tablo_satiri(sutunlar: list, genislikler: list) -> str:
    """Hizalanmış tablo satırı oluşturur."""
    parcalar = []
    for deger, genislik in zip(sutunlar, genislikler):
        parcalar.append(str(deger)[:genislik].ljust(genislik))
    return "  " + "  ".join(parcalar)


# ─── Güvenli Girdi Okuma ──────────────────────────────────────────────────────


def giris_al(mesaj: str, tip=str, min_val=None, max_val=None):
    """
    Belirtilen türde kullanıcı girdisi okur.
    Hatalı girişlerde çökmez; tekrar sorar.

    Args:
        mesaj   : Kullanıcıya gösterilecek soru
        tip     : Beklenen Python tipi (str, int, float vb.)
        min_val : Minimum değer (opsiyonel)
        max_val : Maksimum değer (opsiyonel)

    Returns:
        Geçerli değer
    """
    while True:
        try:
            ham = input(f"  {mesaj}: ").strip()
            if not ham:
                print("  ! Boş bırakılamaz.")
                continue
            deger = tip(ham)
            if min_val is not None and deger < min_val:
                print(f"  ! Değer en az {min_val} olmalıdır.")
                continue
            if max_val is not None and deger > max_val:
                print(f"  ! Değer en fazla {max_val} olmalıdır.")
                continue
            return deger
        except ValueError:
            print(f"  ! Geçersiz giriş ({tip.__name__} bekleniyordu). "
                  "Lütfen tekrar deneyin.")
        except KeyboardInterrupt:
            print("\n\n  Çıkış yapılıyor...")
            raise


def onayla(mesaj: str) -> bool:
    """
    Evet/Hayır sorusu sorar.

    Returns:
        True → kullanıcı 'E' veya 'e' girdi
        False → diğer tüm girişler
    """
    cevap = input(f"  {mesaj} (E/H): ").strip().upper()
    return cevap == "E"


# ─── JSON Veri Kalıcılığı ──────────────────────────────────────────────────────


def veri_yukle(dosya: str = VERI_DOSYASI) -> dict:
    """
    JSON dosyasından veri yükler.

    - Dosya yoksa: boş dict döner (ilk çalıştırma senaryosu).
    - Dosya bozuksa: kullanıcıyı uyarır, boş dict döner.
    - Okuma hatası: kullanıcıyı uyarır, boş dict döner.

    Args:
        dosya: JSON dosyasının yolu

    Returns:
        Yüklenen veri sözlüğü veya {}
    """
    if not os.path.exists(dosya):
        return {}
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"  ! UYARI: '{dosya}' dosyası bozuk veya geçersiz JSON. "
              "Boş veri ile başlanıyor.")
        return {}
    except OSError as e:
        print(f"  ! HATA: Dosya okunamadı → {e}")
        return {}


def veri_kaydet(veri: dict, dosya: str = VERI_DOSYASI) -> bool:
    """
    Veriyi JSON dosyasına kaydeder.

    Args:
        veri  : Kaydedilecek sözlük
        dosya : Hedef dosya yolu

    Returns:
        True → başarılı, False → yazma hatası
    """
    try:
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"  ! HATA: Veri kaydedilemedi → {e}")
        return False
