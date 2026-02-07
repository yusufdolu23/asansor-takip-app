# 🚀 FIREBASE'DEN SUPABASE'E GEÇİŞ REHBERİ

## ✅ YEDEK ALINDI
- **Kod yedeği**: `app_SON_YEDEK_SUPABASE_ONCESI_*.py`
- **Veri yedeği**: `firebase_yedek_20260121_112049.json`
  - 27 Bina
  - 88 Asansör
  - 6 Şirket
  - 5 Bakım Kaydı

---

## 📝 ADIM 1: SUPABASE HESAP AÇ (5 dakika)

### 1.1. Supabase.com'a Git
1. Tarayıcını aç
2. https://supabase.com adresine git
3. **"Start your project"** butonuna tıkla
4. GitHub veya Google ile giriş yap

### 1.2. Yeni Proje Oluştur
1. **"New project"** butonuna tıkla
2. **Organization** seç (yoksa "New organization" ile yeni oluştur)
3. Proje ayarları:
   - **Name**: `gsb-asansor-takip` (istediğin ismi koy)
   - **Database Password**: Güçlü bir şifre oluştur (KAYDET BU ŞİFREYİ!)
   - **Region**: `Frankfurt (Europe)` seç (Türkiye'ye en yakın)
   - **Pricing Plan**: **Free** seçili olsun
4. **"Create new project"** tıkla
5. ☕ 2-3 dakika bekle (proje hazırlanıyor)

### 1.3. API Bilgilerini Kaydet
Proje hazır olunca:
1. Sol menüden **"Settings"** (⚙️) tıkla
2. **"API"** sekmesine tıkla
3. Bu bilgileri **KOPYALA VE KAYDET**:
   - **Project URL**: `https://abcdefgh.supabase.co` gibi
   - **anon public** key: `eyJhbG...` gibi uzun bir kod
   - **service_role** key: `eyJhbG...` gibi başka uzun bir kod

**ÖNEMLİ**: Bu bilgileri bir yere not et (mesela bir .txt dosyasına)

---

## 📊 ADIM 2: SUPABASE'DE TABLOLARI OLUŞTUR (10 dakika)

### 2.1. SQL Editor'ü Aç
1. Sol menüden **"SQL Editor"** (📝) tıkla
2. **"New query"** tıkla

### 2.2. Tabloları Oluştur
Aşağıdaki SQL kodunu kopyala ve **"Run"** (▶️) tıkla:

```sql
-- 1. COMPANIES (Şirketler) Tablosu
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sirket_adi TEXT NOT NULL UNIQUE,
  telefon TEXT,
  yetkili TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. BUILDINGS (Binalar) Tablosu
CREATE TABLE buildings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bina_adi TEXT NOT NULL,
  adres TEXT,
  yetkili_kisi TEXT,
  telefon TEXT,
  company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. ELEVATORS (Asansörler) Tablosu
CREATE TABLE elevators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  building_id UUID REFERENCES buildings(id) ON DELETE CASCADE NOT NULL,
  blok TEXT,
  kimlik TEXT NOT NULL,
  etiket_no TEXT,
  kapasite TEXT,
  marka TEXT,
  tip TEXT,
  katlar TEXT,
  notlar TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(building_id, kimlik)
);

-- 4. MAINTENANCE_LOGS (Bakım Kayıtları) Tablosu
CREATE TABLE maintenance_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  elevator_id UUID REFERENCES elevators(id) ON DELETE CASCADE NOT NULL,
  bakim_tarihi DATE NOT NULL,
  yapilan_islem TEXT NOT NULL,
  teknisyen TEXT,
  sonraki_bakim DATE,
  notlar TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. İndeksler (Hızlandırma için)
CREATE INDEX idx_buildings_company ON buildings(company_id);
CREATE INDEX idx_elevators_building ON elevators(building_id);
CREATE INDEX idx_maintenance_elevator ON maintenance_logs(elevator_id);
CREATE INDEX idx_maintenance_date ON maintenance_logs(bakim_tarihi);
```

**✅ Başarılı olursa**: "Success. No rows returned" yazısı görürsün.

### 2.3. Kontrol Et
1. Sol menüden **"Table Editor"** (📋) tıkla
2. 4 tablo göreceksin:
   - companies
   - buildings
   - elevators
   - maintenance_logs

---

## 📥 ADIM 3: FIREBASE VERİLERİNİ SUPABASE'E AKTAR (5 dakika)

### 3.1. Python Kütüphanelerini Yükle
Terminalde şunu çalıştır:
```bash
cd "/Users/yusufdolu/Desktop/asansör takip uygulaması"
.venv/bin/pip install supabase
```

### 3.2. Supabase Bilgilerini Kaydet
Bir dosya oluşturacağım: `supabase_config.json`

**SEN ŞİMDİ BANA VER**:
1. **SUPABASE_URL**: Proje URL'in (https://...supabase.co)
2. **SUPABASE_KEY**: Service role key'in (eyJhbG... ile başlayan uzun kod)

Bu bilgileri verince ben dosyayı oluşturacağım ve veri aktarımını başlatacağım.

---

## 🔄 ADIM 4: APP.PY'Yİ SUPABASE İÇİN DÜZENLE

Supabase bilgilerini verdikten sonra ben:
1. Firebase kodlarını temizleyeceğim
2. Supabase bağlantısını kuracağım
3. Tüm CRUD işlemlerini Supabase'e çevireceğim

Değişecek şeyler:
- ❌ `firebase_admin` → ✅ `supabase`
- ❌ `db.collection()` → ✅ `supabase.table()`
- ❌ `.stream()` → ✅ `.select().execute()`
- ❌ `.add()` → ✅ `.insert().execute()`
- ❌ `.update()` → ✅ `.update().execute()`
- ❌ `.delete()` → ✅ `.delete().execute()`

---

## ✅ ADIM 5: TEST VE DOĞRULAMA

Veri aktarımı bittikten sonra:
1. Uygulamayı yeniden başlatacağım
2. Dashboard'a bakacağız (27 bina, 88 asansör görmeli)
3. Bir asansör ekleyip silmeyi test edeceğiz
4. Bakım kaydı eklemeyi test edeceğiz

---

## 🎯 ÖZET: SENIN YAPMANLAZIM GEREKENLER

1. ✅ **YEDEKLERİ KONTROL ET** (Benim yaptığım - tamam)
2. ⏳ **SUPABASE HESAP AÇ** (5 dakika - sen yapacaksın)
3. ⏳ **SQL TABLOALRI OLUŞTUR** (2 dakika - SQL kodunu kopyala yapıştır)
4. ⏳ **BANA SUPABASE BİLGİLERİNİ VER** (URL ve Key)
5. ⏳ **BEN VERİ AKTARIMINI YAPACAĞIM** (3 dakika - otomatik)
6. ⏳ **BEN APP.PY'Yİ DÜZENLEYECEĞİM** (5 dakika - otomatik)
7. ⏳ **BERABER TEST EDECEĞİZ** (5 dakika)

**TOPLAM SÜRE: 20-25 dakika**

---

## ❓ NEDEN SUPABASE?

| Özellik | Firebase (Free) | Supabase (Free) |
|---------|----------------|-----------------|
| Günlük Okuma | 50,000 | 500,000,000 |
| Günlük Yazma | 20,000 | Sınırsız |
| Depolama | 1 GB | 500 MB |
| Veritabanı | NoSQL | PostgreSQL (SQL) |
| Kota Bitti Mi? | 🛑 Uygulama çalışmaz | ✅ Yavaşlar ama çalışır |

**Sonuç**: Supabase'de günlük 50 bin okuma değil, **500 MİLYON** okuma hakkın var! Asla bitmez. 🎉

---

## 🆘 BİR ŞEY TERS GİDERSE

Yedeklerimiz var:
1. **Kod**: `app_SON_YEDEK_SUPABASE_ONCESI_*.py` dosyasını `app.py` yap
2. **Veri**: Firebase hala çalışıyor, hiçbir şey silmedik
3. **Geri dön**: `cp app_SON_YEDEK_SUPABASE_ONCESI_*.py app.py` ve Streamlit'i yeniden başlat

---

## 🚀 HADI BAŞLAYALIM!

**Şimdi sen**:
1. https://supabase.com'a git
2. Hesap aç
3. Yeni proje oluştur
4. SQL kodunu çalıştır
5. Bana URL ve KEY'i ver

Ben buradayım, her adımda yardım edeceğim! 💪
