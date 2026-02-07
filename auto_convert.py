import re

# app.py dosyasını oku
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.content()

# Firebase stream işlemlerini Supabase'e çevir
# Pattern 1: db.collection("table").stream()
content = re.sub(
    r'db\.collection\("buildings"\)\.stream\(\)',
    'supabase.table("buildings").select("*").execute().data',
    content
)

# Pattern 2: [d.to_dict() for d in db.collection("table").stream()]
content = re.sub(
    r'\[(.+?)\.to_dict\(\) for \1 in db\.collection\("(\w+)"\)\.stream\(\)\]',
    r'supabase.table("\2").select("*").execute().data',
    content
)

# Pattern 3: db.collection("table").add({...})
content = re.sub(
    r'db\.collection\("(\w+)"\)\.add\(',
    r'supabase.table("\1").insert(',
    content
)

# Pattern 4: db.collection("table").document(id).update({...})
content = re.sub(
    r'db\.collection\("(\w+)"\)\.document\(([^)]+)\)\.update\(',
    r'supabase.table("\1").update(',
    content
)

# Pattern 5: db.collection("table").document(id).delete()
content = re.sub(
    r'db\.collection\("(\w+)"\)\.document\(([^)]+)\)\.delete\(\)',
    r'supabase.table("\1").delete().eq("id", \2).execute()',
    content
)

# Pattern 6: db.collection("table").where("field", "==", value).stream()
content = re.sub(
    r'db\.collection\("(\w+)"\)\.where\("([^"]+)", "==", ([^)]+)\)\.stream\(\)',
    r'supabase.table("\1").select("*").eq("\2", \3).execute().data',
    content
)

# Dosyayı kaydet
with open('app_supabase_converted.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dönüşüm tamamlandı! app_supabase_converted.py dosyası oluşturuldu.")
print("Manuel düzeltme gereken yerler:")
print("1. Alan isimleri (ad -> bina_adi, firma -> company_id)")
print("2. UUID referansları (string ID yerine)")
print("3. .execute() çağrıları kontrol edilmeli")
