#!/usr/bin/env python3
"""Admin kullanıcısını güncelle"""

import bcrypt

# Yeni şifreyi hashle
new_password = "yusuf23keban"
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print("🔑 Yeni admin bilgileri:")
print(f"Kullanıcı adı: yusuf")
print(f"Şifre: yusuf23keban")
print(f"Hash: {hashed}")
print("\n" + "="*60)
print("SUPABASE SQL EDITOR'DA ÇALIŞTIR:")
print("="*60)
print(f"""
-- Admin kullanıcısını güncelle
UPDATE users 
SET username = 'yusuf', 
    password_hash = '{hashed}'
WHERE rol = 'admin';

-- Kontrol et
SELECT username, rol, aktif FROM users WHERE rol = 'admin';
""")
print("="*60)
