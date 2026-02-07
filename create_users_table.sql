
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
VALUES ('admin', '$2b$12$J5x7G9Gvspy23bBlegWJGeRNFObZsPjog1hEv31VoZIiArngN5ag6', NULL, 'admin')
ON CONFLICT (username) DO NOTHING;
