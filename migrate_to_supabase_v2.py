import json
from supabase import create_client
from datetime import datetime

# Supabase bağlantısı
print("🔄 Supabase'e bağlanıyor...")
with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])
print(f"✅ Supabase bağlantısı BAŞARILI!")

# Firebase yedeği
print("\n🔄 Firebase yedeği okunuyor...")
with open('firebase_yedek_20260121_112049.json', 'r', encoding='utf-8') as f:
    firebase_data = json.load(f)

print(f"📊 Firebase'den okundu:")
print(f"   - {len(firebase_data['companies'])} Şirket")
print(f"   - {len(firebase_data['buildings'])} Bina")
print(f"   - {len(firebase_data['elevators'])} Asansör")
print(f"   - {len(firebase_data['maintenance_logs'])} Bakım Kaydı")

# 1. ŞİRKETLERİ AKTAR (ad bazlı)
print("\n🔄 1/4: Şirketler aktarılıyor...")
company_name_to_id = {}  # Şirket adı -> Supabase ID

# Önce Firebase'deki firma isimlerini topla
firebase_company_names = set()
for building in firebase_data['buildings']:
    firma = building.get('firma', '').strip()
    if firma:
        firebase_company_names.add(firma)
for elevator in firebase_data['elevators']:
    firma = elevator.get('firma', '').strip()
    if firma:
        firebase_company_names.add(firma)

# Şirketleri ekle
for firma_adi in sorted(firebase_company_names):
    try:
        result = supabase.table('companies').insert({
            'sirket_adi': firma_adi,
            'telefon': '',
            'yetkili': ''
        }).execute()
        company_name_to_id[firma_adi] = result.data[0]['id']
        print(f"   ✅ {firma_adi}")
    except Exception as e:
        # Zaten varsa select ile al
        result = supabase.table('companies').select('*').eq('sirket_adi', firma_adi).execute()
        if result.data:
            company_name_to_id[firma_adi] = result.data[0]['id']
            print(f"   ♻️ {firma_adi} (zaten var)")

print(f"✅ {len(company_name_to_id)} şirket hazır!")

# 2. BİNALARI AKTAR
print("\n🔄 2/4: Binalar aktarılıyor...")
building_name_to_id = {}  # Bina adı -> Supabase ID

for building in firebase_data['buildings']:
    bina_adi = building.get('ad', '').strip()
    if not bina_adi:
        continue
    
    # Company ID'yi bul
    company_id = None
    firma = building.get('firma', '').strip()
    if firma and firma in company_name_to_id:
        company_id = company_name_to_id[firma]
    
    building_data = {
        'bina_adi': bina_adi,
        'adres': building.get('adres', ''),
        'yetkili_kisi': '',
        'telefon': '',
        'company_id': company_id
    }
    
    try:
        result = supabase.table('buildings').insert(building_data).execute()
        building_name_to_id[bina_adi] = result.data[0]['id']
        print(f"   ✅ {bina_adi}")
    except Exception as e:
        print(f"   ⚠️ {bina_adi}: {str(e)[:50]}")

print(f"✅ {len(building_name_to_id)} bina aktarıldı!")

# 3. ASANSÖRLERI AKTAR
print("\n🔄 3/4: Asansörler aktarılıyor...")
elevator_kimlik_to_id = {}  # Kimlik -> Supabase ID

for elevator in firebase_data['elevators']:
    # Bina adından Supabase ID'yi bul
    bina_adi = elevator.get('bina', '').strip()
    if not bina_adi or bina_adi not in building_name_to_id:
        print(f"   ⚠️ ATLANDI: {elevator.get('kimlik')} (bina: {bina_adi} bulunamadı)")
        continue
    
    building_id = building_name_to_id[bina_adi]
    kimlik = elevator.get('kimlik', '') or elevator.get('etiket_no', '')
    
    if not kimlik:
        continue
    
    elevator_data = {
        'building_id': building_id,
        'blok': elevator.get('blok', ''),
        'kimlik': kimlik,
        'etiket_no': elevator.get('etiket_no', ''),
        'kapasite': '',
        'marka': '',
        'tip': elevator.get('tip', ''),
        'katlar': '',
        'notlar': f"Etiket: {elevator.get('etiket', '')}"
    }
    
    try:
        result = supabase.table('elevators').insert(elevator_data).execute()
        elevator_kimlik_to_id[kimlik] = result.data[0]['id']
        print(f"   ✅ {bina_adi} - {kimlik}")
    except Exception as e:
        print(f"   ⚠️ {kimlik}: {str(e)[:80]}")

print(f"✅ {len(elevator_kimlik_to_id)} asansör aktarıldı!")

# 4. BAKIM KAYITLARINI AKTAR
print("\n🔄 4/4: Bakım kayıtları aktarılıyor...")
bakim_sayisi = 0

for log in firebase_data['maintenance_logs']:
    # Asansör kimliğinden Supabase ID'yi bul
    elevator_firebase_id = log.get('elevator_id', '')
    
    # Önce Firebase'den elevator'ı bul
    elevator_obj = None
    for elev in firebase_data['elevators']:
        if elev['doc_id'] == elevator_firebase_id:
            elevator_obj = elev
            break
    
    if not elevator_obj:
        continue
    
    kimlik = elevator_obj.get('kimlik', '') or elevator_obj.get('etiket_no', '')
    if not kimlik or kimlik not in elevator_kimlik_to_id:
        continue
    
    elevator_id = elevator_kimlik_to_id[kimlik]
    
    log_data = {
        'elevator_id': elevator_id,
        'bakim_tarihi': log.get('bakim_tarihi', '2026-01-01'),
        'yapilan_islem': log.get('yapilan_islem', 'Bakım yapıldı'),
        'teknisyen': log.get('teknisyen', ''),
        'sonraki_bakim': log.get('sonraki_bakim', None),
        'notlar': log.get('notlar', '')
    }
    
    try:
        supabase.table('maintenance_logs').insert(log_data).execute()
        bakim_sayisi += 1
        print(f"   ✅ {log_data['bakim_tarihi']} - {log_data['yapilan_islem'][:30]}")
    except Exception as e:
        print(f"   ⚠️ {str(e)[:50]}")

print(f"✅ {bakim_sayisi} bakım kaydı aktarıldı!")

# ÖZET
print("\n" + "="*60)
print("🎉 VERİ AKTARIMI TAMAMLANDI!")
print("="*60)
print(f"✅ {len(company_name_to_id)} şirket")
print(f"✅ {len(building_name_to_id)} bina")
print(f"✅ {len(elevator_kimlik_to_id)} asansör")
print(f"✅ {bakim_sayisi} bakım kaydı")
print("\n🚀 Şimdi app.py'yi Supabase için düzenleyebilirim!")
