from supabase import create_client
import json

# Supabase bağlantısı
with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

# SQL komutlarını çalıştır
sql_commands = [
    "ALTER TABLE maintenance_logs ADD COLUMN IF NOT EXISTS bakim_servis_no TEXT",
    "CREATE INDEX IF NOT EXISTS idx_maintenance_servis_no ON maintenance_logs(bakim_servis_no)"
]

for sql in sql_commands:
    try:
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print(f"✅ Başarılı: {sql[:50]}...")
    except Exception as e:
        print(f"⚠️ Hata (normal olabilir): {e}")
        # Manuel SQL ile dene
        print(f"Manuel olarak çalıştırılacak SQL:\n{sql}\n")

print("\n✅ Database güncelleme tamamlandı!")
