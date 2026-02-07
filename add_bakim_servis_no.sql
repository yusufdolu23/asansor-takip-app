-- Bakım kayıtlarına servis no kolonu ekle
ALTER TABLE maintenance_logs 
ADD COLUMN bakim_servis_no TEXT;

-- İndeks ekle (hızlı arama için)
CREATE INDEX idx_maintenance_servis_no ON maintenance_logs(bakim_servis_no);
