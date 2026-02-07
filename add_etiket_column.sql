-- elevators tablosuna etiket kolonu ekle
ALTER TABLE elevators ADD COLUMN IF NOT EXISTS etiket TEXT DEFAULT 'Yeşil';

-- Varsayılan değeri güncelle
UPDATE elevators SET etiket = 'Yeşil' WHERE etiket IS NULL;
