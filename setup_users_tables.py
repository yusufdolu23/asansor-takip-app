#!/usr/bin/env python3
"""Users ve Activity Logs tablolarını oluştur"""

import json
from supabase import create_client
import bcrypt

# Supabase bağlantısı
with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

print("🔧 Users tablosu oluşturuluyor...")

# Admin şifresini hashle
admin_password = "admin123"
hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"✅ Admin şifresi hashlendi: {hashed[:50]}...")

# Tabloları oluştur
print("\n📋 Supabase'de şu SQL'leri manuel çalıştırman gerekiyor:")
print("\n" + "="*60)
print("SQL #1 - Users Tablosu:")
print("="*60)

sql1 = f"""
-- Kullanıcılar tablosu oluştur
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    building_id UUID REFERENCES buildings(id) ON DELETE CASCADE,
    rol TEXT NOT NULL CHECK (rol IN ('admin', 'bina_yetkilisi')),
    aktif BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_building ON users(building_id);
CREATE INDEX IF NOT EXISTS idx_users_rol ON users(rol);

-- Varsayılan admin kullanıcısı ekle (şifre: admin123)
INSERT INTO users (username, password_hash, building_id, rol) 
VALUES ('admin', '{hashed}', NULL, 'admin')
ON CONFLICT (username) DO NOTHING;
"""

print(sql1)

print("\n" + "="*60)
print("SQL #2 - Activity Logs Tablosu:")
print("="*60)

sql2 = """
-- Aktivite log tablosu oluştur
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    building_name TEXT,
    elevator_name TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_username ON activity_logs(username);
"""

print(sql2)

print("\n" + "="*60)
print("📝 YAPILACAKLAR:")
print("="*60)
print("1. https://dqyjainiwdeybwvecsil.supabase.co adresine git")
print("2. Sol menüden 'SQL Editor' seç")
print("3. Yukarıdaki SQL #1'i kopyala yapıştır ve 'Run' bas")
print("4. Sonra SQL #2'yi kopyala yapıştır ve 'Run' bas")
print("5. Uygulamayı yenile (F5)")
print("6. Kullanıcı: admin, Şifre: admin123 ile giriş yap")
print("="*60)

# create_users_table.sql dosyasını güncelle
with open('create_users_table.sql', 'w') as f:
    f.write(sql1)

print("\n✅ create_users_table.sql dosyası güncellendi (yeni hash ile)")

with open('create_activity_logs_table.sql', 'w') as f:
    f.write(sql2)

print("✅ create_activity_logs_table.sql dosyası güncellendi")
