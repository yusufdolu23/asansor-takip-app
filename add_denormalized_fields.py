from supabase import create_client
import json

print("🔄 Supabase elevators tablosuna bina_adi ve firma_adi ekleniyor...")

with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

# 1. Buildings ve Companies map oluştur
buildings = supabase.table('buildings').select('id, bina_adi, company_id').execute().data
companies = supabase.table('companies').select('id, sirket_adi').execute().data

building_map = {b['id']: {'bina_adi': b['bina_adi'], 'company_id': b.get('company_id')} for b in buildings}
company_map = {c['id']: c['sirket_adi'] for c in companies}

print(f"✅ {len(building_map)} bina")
print(f"✅ {len(company_map)} şirket")

# 2. Her elevator'a bina_adi ve firma_adi ekle
elevators = supabase.table('elevators').select('*').execute().data

print(f"🔄 {len(elevators)} asansör güncelleniyor...")

updated = 0
for elevator in elevators:
    building_id = elevator.get('building_id')
    
    if building_id and building_id in building_map:
        bina_adi = building_map[building_id]['bina_adi']
        company_id = building_map[building_id].get('company_id')
        
        # Firma adını da al
        firma_adi = ''
        if company_id and company_id in company_map:
            firma_adi = company_map[company_id]
        
        # Şimdi elevator'ın notlar alanına JSON olarak ekleyelim MI?
        # HAYIR! Doğrudan tablo şemasına ekleyelim
        # PostgreSQL'de ALTER TABLE ile kolon eklenebilir
        
        # Ama Python client ile kolon ekleyemeyiz, sadece veri update edebiliriz
        # O yüzden: Mevcut alanları kullan veya SQL execute et
        
        # EN KOLAY: notlar alanını kullan
        # notlar = f"Bina: {bina_adi} | Firma: {firma_adi}"
        
        # DAHA İYİ: Supabase'de SQL çalıştır
        break

print("❌ Python client ile tablo şeması değiştirilemez!")
print("✅ Çözüm: SQL ile ALTER TABLE yap veya app.py'de JOIN yap")
print("")
print("KARAR: app.py'de helper function yazıyorum (hiçbir SQL gerekmiyor)")
