import json
from supabase import create_client
from datetime import datetime

# Supabase bağlantısını test et
print("🔄 Supabase'e bağlanıyor...")
with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

# Test query
result = supabase.table('companies').select("*").execute()
print(f"✅ Supabase bağlantısı BAŞARILI!")
print(f"📊 Companies tablosu hazır (şu an {len(result.data)} kayıt)")

# Firebase yedek dosyasını oku
print("\n🔄 Firebase yedeği okunuyor...")
with open('firebase_yedek_20260121_112049.json', 'r', encoding='utf-8') as f:
    firebase_data = json.load(f)

print(f"📊 Firebase'den okundu:")
print(f"   - {len(firebase_data['companies'])} Şirket")
print(f"   - {len(firebase_data['buildings'])} Bina")
print(f"   - {len(firebase_data['elevators'])} Asansör")
print(f"   - {len(firebase_data['maintenance_logs'])} Bakım Kaydı")

# 1. ŞİRKETLERİ AKTAR
print("\n🔄 1/4: Şirketler aktarılıyor...")
company_id_map = {}  # Firebase ID -> Supabase ID mapping

for company in firebase_data['companies']:
    firebase_id = company['doc_id']
    
    # Boş sirket_adi olanları atla veya varsayılan isim ver
    sirket_adi = company.get('sirket_adi', '').strip()
    if not sirket_adi:
        sirket_adi = f"Şirket-{firebase_id[:8]}"
    
    company_data = {
        'sirket_adi': sirket_adi,
        'telefon': company.get('telefon', ''),
        'yetkili': company.get('yetkili', '')
    }
    
    result = supabase.table('companies').insert(company_data).execute()
    supabase_id = result.data[0]['id']
    company_id_map[firebase_id] = supabase_id
    print(f"   ✅ {company_data['sirket_adi']} -> {supabase_id}")

print(f"✅ {len(firebase_data['companies'])} şirket aktarıldı!")

# 2. BİNALARI AKTAR
print("\n🔄 2/4: Binalar aktarılıyor...")
building_id_map = {}  # Firebase ID -> Supabase ID mapping

for building in firebase_data['buildings']:
    firebase_id = building['doc_id']
    
    # Company ID'yi map et (varsa)
    company_id = None
    if building.get('company_id') and building['company_id'] in company_id_map:
        company_id = company_id_map[building['company_id']]
    
    building_data = {
        'bina_adi': building.get('bina_adi', ''),
        'adres': building.get('adres', ''),
        'yetkili_kisi': building.get('yetkili_kisi', ''),
        'telefon': building.get('telefon', ''),
        'company_id': company_id
    }
    
    result = supabase.table('buildings').insert(building_data).execute()
    supabase_id = result.data[0]['id']
    building_id_map[firebase_id] = supabase_id
    print(f"   ✅ {building_data['bina_adi']} -> {supabase_id}")

print(f"✅ {len(firebase_data['buildings'])} bina aktarıldı!")

# 3. ASANSÖRLERI AKTAR
print("\n🔄 3/4: Asansörler aktarılıyor...")
elevator_id_map = {}  # Firebase ID -> Supabase ID mapping

for elevator in firebase_data['elevators']:
    firebase_id = elevator['doc_id']
    
    # Building ID'yi map et (zorunlu)
    if elevator.get('building_id') not in building_id_map:
        print(f"   ⚠️ ATLANDI: {elevator.get('kimlik')} (bina bulunamadı)")
        continue
    
    building_id = building_id_map[elevator['building_id']]
    
    elevator_data = {
        'building_id': building_id,
        'blok': elevator.get('blok', ''),
        'kimlik': elevator.get('kimlik', ''),
        'etiket_no': elevator.get('etiket_no', ''),
        'kapasite': elevator.get('kapasite', ''),
        'marka': elevator.get('marka', ''),
        'tip': elevator.get('tip', ''),
        'katlar': elevator.get('katlar', ''),
        'notlar': elevator.get('notlar', '')
    }
    
    result = supabase.table('elevators').insert(elevator_data).execute()
    supabase_id = result.data[0]['id']
    elevator_id_map[firebase_id] = supabase_id
    print(f"   ✅ {elevator_data['kimlik']} -> {supabase_id}")

print(f"✅ {len(elevator_id_map)} asansör aktarıldı!")

# 4. BAKIM KAYITLARINI AKTAR
print("\n🔄 4/4: Bakım kayıtları aktarılıyor...")

for log in firebase_data['maintenance_logs']:
    # Elevator ID'yi map et (zorunlu)
    if log.get('elevator_id') not in elevator_id_map:
        print(f"   ⚠️ ATLANDI: Bakım kaydı (asansör bulunamadı)")
        continue
    
    elevator_id = elevator_id_map[log['elevator_id']]
    
    log_data = {
        'elevator_id': elevator_id,
        'bakim_tarihi': log.get('bakim_tarihi', ''),
        'yapilan_islem': log.get('yapilan_islem', ''),
        'teknisyen': log.get('teknisyen', ''),
        'sonraki_bakim': log.get('sonraki_bakim', ''),
        'notlar': log.get('notlar', '')
    }
    
    result = supabase.table('maintenance_logs').insert(log_data).execute()
    print(f"   ✅ {log_data['bakim_tarihi']} - {log_data['yapilan_islem']}")

print(f"✅ {len(firebase_data['maintenance_logs'])} bakım kaydı aktarıldı!")

# ÖZET
print("\n" + "="*60)
print("🎉 VERİ AKTARIMI TAMAMLANDI!")
print("="*60)
print(f"✅ {len(firebase_data['companies'])} şirket")
print(f"✅ {len(firebase_data['buildings'])} bina")
print(f"✅ {len(elevator_id_map)} asansör")
print(f"✅ {len(firebase_data['maintenance_logs'])} bakım kaydı")
print("\n🚀 Şimdi app.py'yi Supabase için düzenleyeceğim...")
