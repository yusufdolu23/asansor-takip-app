-- Maintenance logs tablosuna fiyat kolonu ekle
ALTER TABLE maintenance_logs 
ADD COLUMN IF NOT EXISTS fiyat DECIMAL(10,2);

-- Kolon açıklaması ekle
COMMENT ON COLUMN maintenance_logs.fiyat IS 'Parça değişimi veya işlem maliyeti (TL cinsinden)';
