-- Ödenek Talepleri Tablosu
CREATE TABLE IF NOT EXISTS odenek_talepleri (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  elevator_id UUID REFERENCES elevators(id) ON DELETE CASCADE NOT NULL,
  maintenance_id UUID REFERENCES maintenance_logs(id) ON DELETE SET NULL,
  talep_eden_user_id UUID REFERENCES users(id) NOT NULL,
  talep_tarihi TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  tutar DECIMAL(10,2) NOT NULL,
  aciklama TEXT,
  durum TEXT DEFAULT 'Beklemede' CHECK (durum IN ('Beklemede', 'Onaylandı', 'Reddedildi')),
  onaylayan_user_id UUID REFERENCES users(id),
  onay_tarihi TIMESTAMP WITH TIME ZONE,
  onay_notu TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- İndeksler (hızlı arama için)
CREATE INDEX IF NOT EXISTS idx_odenek_elevator ON odenek_talepleri(elevator_id);
CREATE INDEX IF NOT EXISTS idx_odenek_maintenance ON odenek_talepleri(maintenance_id);
CREATE INDEX IF NOT EXISTS idx_odenek_durum ON odenek_talepleri(durum);
CREATE INDEX IF NOT EXISTS idx_odenek_talep_eden ON odenek_talepleri(talep_eden_user_id);
