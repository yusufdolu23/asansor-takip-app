import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate('gsb_key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Tüm koleksiyonları export et
yedek_data = {
    'export_tarihi': datetime.now().isoformat(),
    'buildings': [],
    'elevators': [],
    'companies': [],
    'maintenance_logs': []
}

print('🔄 Buildings export ediliyor...')
for doc in db.collection('buildings').stream():
    data = doc.to_dict()
    data['doc_id'] = doc.id
    yedek_data['buildings'].append(data)

print('🔄 Elevators export ediliyor...')
for doc in db.collection('elevators').stream():
    data = doc.to_dict()
    data['doc_id'] = doc.id
    yedek_data['elevators'].append(data)

print('🔄 Companies export ediliyor...')
for doc in db.collection('companies').stream():
    data = doc.to_dict()
    data['doc_id'] = doc.id
    yedek_data['companies'].append(data)

print('🔄 Maintenance logs export ediliyor...')
for doc in db.collection('maintenance_logs').stream():
    data = doc.to_dict()
    data['doc_id'] = doc.id
    yedek_data['maintenance_logs'].append(data)

# JSON dosyasına kaydet
filename = f'firebase_yedek_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(yedek_data, f, ensure_ascii=False, indent=2, default=str)

print(f'\n✅ YEDEK TAMAMLANDI!')
print(f'📊 Buildings: {len(yedek_data["buildings"])}')
print(f'📊 Elevators: {len(yedek_data["elevators"])}')
print(f'📊 Companies: {len(yedek_data["companies"])}')
print(f'📊 Maintenance Logs: {len(yedek_data["maintenance_logs"])}')
print(f'💾 Dosya: {filename}')
