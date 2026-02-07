-- Mesajlaşma tablosuna asansör bilgisi ekle
ALTER TABLE messages ADD COLUMN IF NOT EXISTS elevator_ids TEXT[];

-- Yorum: elevator_ids TEXT[] - Birden fazla asansör seçilebilir (PostgreSQL array)
