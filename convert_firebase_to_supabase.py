"""
Firebase kodlarını Supabase'e çevirmek için helper script
"""

# Firebase -> Supabase dönüşüm rehberi:

# 1. BAĞLANTI
# Firebase:
#   db = firestore.client()
# Supabase:
#   supabase = create_client(url, key)

# 2. OKUMA (SELECT)
# Firebase:
#   docs = db.collection("buildings").stream()
#   data_list = [d.to_dict() for d in docs]
# Supabase:
#   result = supabase.table("buildings").select("*").execute()
#   data_list = result.data

# 3. FİLTRELEME
# Firebase:
#   docs = db.collection("elevators").where("bina", "==", "Horasan").stream()
# Supabase:
#   result = supabase.table("elevators").select("*").eq("bina_adi", "Horasan").execute()

# 4. EKLEME (INSERT)
# Firebase:
#   db.collection("buildings").add({"ad": "Bina 1"})
# Supabase:
#   supabase.table("buildings").insert({"bina_adi": "Bina 1"}).execute()

# 5. GÜNCELLEME (UPDATE)
# Firebase:
#   db.collection("buildings").document(doc_id).update({"ad": "Yeni Ad"})
# Supabase:
#   supabase.table("buildings").update({"bina_adi": "Yeni Ad"}).eq("id", uuid).execute()

# 6. SİLME (DELETE)
# Firebase:
#   db.collection("buildings").document(doc_id).delete()
# Supabase:
#   supabase.table("buildings").delete().eq("id", uuid).execute()

# 7. ALAN İSİMLERİ DEĞİŞTİ!
# Firebase -> Supabase:
#   ad -> bina_adi
#   firma -> company_id (UUID referans)
#   bina -> building_id (UUID referans)
#   asansor_kimlik -> elevator_id (UUID referans)
#   tarih -> bakim_tarihi
#   son_bakim -> sadece elevators tablosunda yok artık
#   timestamp -> created_at

print("Bu dosya sadece referans amaçlıdır. Kod dönüşümünü otomatik olarak yapıyorum...")
