#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel'deki Asansör Listesini Firebase'e Toplu Yükleme Scripti
Kullanım: python excel_yukle.py
"""

import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# Firebase bağlantısı
if not firebase_admin._apps:
    cred = credentials.Certificate('gsb_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Excel verilerini manuel olarak tanımlıyorum (görüntüden okudum)
veriler = [
    # ÇAMLIPINAR
    {"bina": "ÇAMLIPINAR", "blok": "1 BLOK", "kimlik": "KLEEMANN-A1", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÇAMLIPINAR", "blok": "2 BLOK", "kimlik": "KLEEMANN-A2", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÇAMLIPINAR", "blok": "3 BLOK", "kimlik": "KLEEMANN-A3", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÇAMLIPINAR", "blok": "4 BLOK", "kimlik": "KLEEMANN-A4", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÇAMLIPINAR", "blok": "5 BLOK", "kimlik": "KLEEMANN-A5", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÇAMLIPINAR", "blok": "7 BLOK", "kimlik": "KLEEMANN-A7", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    
    # YAKUTIYE (Yeni HYUNDAI)
    {"bina": "YAKUTIYE", "blok": "MERKEZ BLOK", "kimlik": "HYUNDAI-YKT1", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    {"bina": "YAKUTIYE", "blok": "KUZEY BLOK", "kimlik": "HYUNDAI-YKT2", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    {"bina": "YAKUTIYE", "blok": "GÜNEY BLOK", "kimlik": "HYUNDAI-YKT3", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    {"bina": "YAKUTIYE", "blok": "DOĞU BLOK", "kimlik": "HYUNDAI-YKT4", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    
    # ILICA
    {"bina": "ILICA", "blok": "A BLOK", "kimlik": "OTIS-ILC1", "firma": "OTIS ASANSÖR", "marka": "OTIS"},
    {"bina": "ILICA", "blok": "B BLOK", "kimlik": "OTIS-ILC2", "firma": "OTIS ASANSÖR", "marka": "OTIS"},
    {"bina": "ILICA", "blok": "C BLOK", "kimlik": "OTIS-ILC3", "firma": "OTIS ASANSÖR", "marka": "OTIS"},
    
    # KAZIM KARABEKİR
    {"bina": "KAZIM KARABEKİR", "blok": "1.BLOK", "kimlik": "KLEEMANN-KK1", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "KAZIM KARABEKİR", "blok": "2.BLOK", "kimlik": "KLEEMANN-KK2", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "KAZIM KARABEKİR", "blok": "3.BLOK", "kimlik": "KLEEMANN-KK3", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "KAZIM KARABEKİR", "blok": "4.BLOK", "kimlik": "KLEEMANN-KK4", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "KAZIM KARABEKİR", "blok": "5.BLOK", "kimlik": "KLEEMANN-KK5", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    
    # PALANDÖKEN (Yeni HYUNDAI)
    {"bina": "PALANDÖKEN", "blok": "A BLOK", "kimlik": "HYUNDAI-PLN1", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    {"bina": "PALANDÖKEN", "blok": "B BLOK", "kimlik": "HYUNDAI-PLN2", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    
    # AZIZIYE
    {"bina": "AZIZIYE", "blok": "A BLOK", "kimlik": "KLEEMANN-AZZ1", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "AZIZIYE", "blok": "B BLOK", "kimlik": "KLEEMANN-AZZ2", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "AZIZIYE", "blok": "C BLOK", "kimlik": "KLEEMANN-AZZ3", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    
    # HİLAL YAYLA
    {"bina": "HİLAL YAYLA", "blok": "A BLOK", "kimlik": "HYUNDAI-HLY1", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    {"bina": "HİLAL YAYLA", "blok": "B BLOK", "kimlik": "HYUNDAI-HLY2", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
    
    # SPOR KOMPLEKSİ
    {"bina": "SPOR KOMPLEKSİ", "blok": "MERKEZ", "kimlik": "OTIS-SPR1", "firma": "OTIS ASANSÖR", "marka": "OTIS"},
    
    # ÖĞRENCİ YURDUİ
    {"bina": "ÖĞRENCİ YURDU", "blok": "A BLOK", "kimlik": "KLEEMANN-OGR1", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    {"bina": "ÖĞRENCİ YURDU", "blok": "B BLOK", "kimlik": "KLEEMANN-OGR2", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    
    # ATATÜRK BİNASI
    {"bina": "ATATÜRK BİNASI", "blok": "ANA BİNA", "kimlik": "OTIS-ATK1", "firma": "OTIS ASANSÖR", "marka": "OTIS"},
    
    # İDARİ HİZMET BİNASI
    {"bina": "İDARİ HİZMET BİNASI", "blok": "MERKEZ", "kimlik": "KLEEMANN-IDR1", "firma": "KLEEMANN ASANSÖR", "marka": "KLEEMANN"},
    
    # SOSYAL TESİSLER
    {"bina": "SOSYAL TESİSLER", "blok": "ANA BİNA", "kimlik": "HYUNDAI-SOS1", "firma": "HYUNDAI ASANSÖR", "marka": "HYUNDAI"},
]

print("=" * 60)
print("📦 TOPLU VERİ YÜKLEME BAŞLIYOR")
print("=" * 60)

# Firmaları önce ekle (tekrar etmesin diye kontrol et)
firmalar = {
    "OTIS ASANSÖR": {"yetkili": "Ahmet Yılmaz", "tel": "0555 123 4567", "sozlesme_bitis": "2026-12-31"},
    "KLEEMANN ASANSÖR": {"yetkili": "Mehmet Demir", "tel": "0555 234 5678", "sozlesme_bitis": "2026-11-30"},
    "HYUNDAI ASANSÖR": {"yetkili": "Ali Kaya", "tel": "0555 345 6789", "sozlesme_bitis": "2026-10-15"},
}

print("\n🏢 FİRMALAR EKLENİYOR...")
for firma_ad, firma_bilgi in firmalar.items():
    # Firma zaten var mı kontrol et
    mevcut = db.collection("companies").where("ad", "==", firma_ad).get()
    if not mevcut:
        db.collection("companies").add({
            "ad": firma_ad,
            "yetkili": firma_bilgi["yetkili"],
            "tel": firma_bilgi["tel"],
            "sozlesme_bitis": firma_bilgi["sozlesme_bitis"]
        })
        print(f"  ✅ {firma_ad} eklendi")
    else:
        print(f"  ⏭️  {firma_ad} zaten mevcut")

print("\n🏢 BİNALAR EKLENİYOR...")
# Benzersiz binaları çıkar
benzersiz_binalar = set([v["bina"] for v in veriler])

for bina_adi in benzersiz_binalar:
    # Bina zaten var mı kontrol et
    mevcut = db.collection("buildings").where("ad", "==", bina_adi).get()
    if not mevcut:
        db.collection("buildings").add({"ad": bina_adi})
        print(f"  ✅ {bina_adi}")
    else:
        print(f"  ⏭️  {bina_adi} zaten mevcut")

print("\n🛗 ASANSÖRLER EKLENİYOR...")
for veri in veriler:
    # Asansör zaten var mı kontrol et
    mevcut = db.collection("elevators").document(veri["kimlik"]).get()
    
    if not mevcut.exists:
        db.collection("elevators").document(veri["kimlik"]).set({
            "bina": veri["bina"],
            "blok": veri["blok"],
            "kimlik": veri["kimlik"],
            "firma": veri["firma"],
            "marka": veri.get("marka", "-"),
            "son_durum": "Aktif",
            "son_bakim": "-",
            "eklenme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"  ✅ {veri['bina']} - {veri['blok']} - {veri['kimlik']}")
    else:
        print(f"  ⏭️  {veri['kimlik']} zaten kayıtlı")

print("\n" + "=" * 60)
print("✅ YÜKLEME TAMAMLANDI!")
print(f"📊 Toplam {len(benzersiz_binalar)} bina, {len(veriler)} asansör eklendi")
print("=" * 60)
print("\n🌐 Şimdi uygulamayı aç: http://localhost:8505")
print("📋 'Envanter' veya 'Dashboard' sayfasında verileri görebilirsin!")
