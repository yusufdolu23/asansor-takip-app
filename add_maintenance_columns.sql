-- Bakım işlemleri tablosuna yeni kolonlar ekle
ALTER TABLE maintenance_logs 
ADD COLUMN IF NOT EXISTS parca_adi TEXT,
ADD COLUMN IF NOT EXISTS degisim_tarihi DATE,
ADD COLUMN IF NOT EXISTS arizali_parca_teslim_tarihi DATE,
ADD COLUMN IF NOT EXISTS tahmini_teslim_tarihi DATE,
ADD COLUMN IF NOT EXISTS durum TEXT DEFAULT 'Devam Ediyor';
