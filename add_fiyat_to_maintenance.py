#!/usr/bin/env python3
"""Maintenance logs tablosuna fiyat kolonu ekle"""

import json
from supabase import create_client

# Supabase bağlantısı
with open('supabase_config.json', 'r') as f:
    config = json.load(f)

supabase = create_client(config['url'], config['key'])

# SQL sorgusu ile kolon ekle
sql_query = """
ALTER TABLE maintenance_logs 
ADD COLUMN IF NOT EXISTS fiyat DECIMAL(10,2);
"""

try:
    # Supabase RPC ile SQL çalıştır
    result = supabase.rpc('exec_sql', {'query': sql_query}).execute()
    print("✅ Fiyat kolonu başarıyla eklendi!")
    print(result)
except Exception as e:
    print(f"⚠️ SQL ile eklenemedi: {e}")
    print("\n📋 Şu SQL'i Supabase SQL Editor'da çalıştırın:")
    print(sql_query)
