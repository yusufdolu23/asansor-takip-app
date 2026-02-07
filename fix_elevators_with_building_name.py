from supabase import create_client
import json

print("🔄 Supabase elevators tablosuna bina_text alanı ekleniyor...")

with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

# 1. Tüm buildings'i çek (UUID -> Name mapping)
buildings = supabase.table('buildings').select('*').execute().data
building_map = {b['id']: b['bina_adi'] for b in buildings}

print(f"✅ {len(building_map)} bina bulundu")

# 2. Tüm elevators'ı çek
elevators = supabase.table('elevators').select('*').execute().data

print(f"🔄 {len(elevators)} asansör güncelleniyor...")

# 3. Her elevator'a bina ismini ekle
updated = 0
for elevator in elevators:
    building_id = elevator.get('building_id')
    if building_id in building_map:
        bina_adi = building_map[building_id]
        
        # Notlar alanını kullanarak bina adını sakla (geçici çözüm)
        # Veya doğrudan sorgu ile bina adını da döndürebiliriz
        # En iyisi: Her okumada JOIN yap
        
        # ŞİMDİLİK: elevator kaydına 'bina_text' custom alanı eklemiyoruz
        # Bunun yerine app.py'de her elevator için building'i ayrı çekeceğiz
        # VEYA: Supabase'de view oluştur
        
        updated += 1

print(f"✅ {updated} asansör için bina bilgisi hazır")
print("")
print("SONUÇ: Supabase'de JOIN gerekiyor!")
print("Çözüm: app.py'de elevators çekerken building bilgisini de JOIN ile çek")
print("Veya her elevator okuma sonrası building'i ayrı sor")
