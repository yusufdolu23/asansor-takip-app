import streamlit as st
from supabase import create_client
import json
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from io import BytesIO
import bcrypt
import os
import pickle

# TARİH FORMATLAMA FONKSİYONU
def format_tarih(tarih_str):
    """Tarih string'ini gün/ay/yıl formatına çevirir"""
    try:
        if 'T' in str(tarih_str):
            # ISO format: 2026-01-23T00:00:00+00:00
            tarih_obj = datetime.fromisoformat(str(tarih_str).replace('Z', '+00:00'))
        else:
            # Basit format: 2026-01-23
            tarih_obj = datetime.strptime(str(tarih_str)[:10], '%Y-%m-%d')
        return tarih_obj.strftime('%d/%m/%Y')
    except:
        return str(tarih_str)[:10]

# ETİKET RENGİNİ RENKLE GÖSTERME FONKSİYONU
def etiket_rengi_goster(renk):
    """Etiket rengini HTML ile renkli badge olarak gösterir"""
    renk_kodlari = {
        'Yeşil': '#28a745',
        'Mavi': '#17a2b8',
        'Sarı': '#ffc107',
        'Kırmızı': '#dc3545'
    }
    bg_color = renk_kodlari.get(renk, '#6c757d')
    return f'<span style="background-color: {bg_color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; display: inline-block;">{renk}</span>'

# --- 1. AYARLAR VE TASARIM (TAM ÇÖZÜM) ---
st.set_page_config(
    page_title="GSB Asansör Takip",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MODERN & SAKİN TASARIM - MAVİ TONLARI
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* GENEL ARKAPLAN - BEYAZ */
        [data-testid="stAppViewContainer"] {
            background: #F8F9FA !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        /* SIDEBAR - Modern Cam Efekti */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px) !important;
            border-right: 1px solid #E2E8F0 !important;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05) !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #2D3748 !important;
        }
        
        /* YAZI TİPLERİ - HEPSİ SİYAH */
        h1, h2, h3, h4, h5, h6 {
            color: #1A202C !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        p, span, div, label, li, td, th {
            color: #2D3748 !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* FORM ELEMANLARI - MİLİMETRİK HİZALAMA */
        
        /* 1. Selectbox (Açılır Menü) - YAZININ AŞAĞIYA KAYMASINI ENGELLİYOR */
        .stSelectbox div[data-baseweb="select"] > div {
            min-height: 50px !important;
            height: auto !important;
            display: flex !important;
            align-items: center !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            background: #FFFFFF !important;
            color: #1A202C !important;
            font-weight: 500 !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            font-size: 15px !important;
        }
        
        /* 2. Text Input (Yazı Girişi) - TAM ORTALANMIŞ */
        .stTextInput > div > div > input {
            height: 50px !important;
            min-height: 50px !important;
            background: #FFFFFF !important;
            color: #1A202C !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 0px 16px !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            line-height: 50px !important;
            transition: all 0.3s ease !important;
        }
        
        /* 3. TextArea (Çok Satırlı) */
        .stTextArea > div > div > textarea {
            background: #FFFFFF !important;
            color: #1A202C !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        /* 4. Number Input */
        .stNumberInput > div > div > input {
            height: 50px !important;
            background: #FFFFFF !important;
            color: #1A202C !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 0px 16px !important;
            font-size: 15px !important;
            line-height: 50px !important;
        }
        
        /* 5. Date Input - TAM HİZALI */
        .stDateInput > div > div > input {
            height: 50px !important;
            min-height: 50px !important;
            background: #FFFFFF !important;
            color: #1A202C !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 0px 16px !important;
            font-size: 15px !important;
            line-height: 50px !important;
        }
        
        /* Placeholder rengi */
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #A0AEC0 !important;
            opacity: 1 !important;
        }
        
        /* Focus (Tıklandığında) */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox div[data-baseweb="select"]:focus-within > div,
        .stDateInput > div > div > input:focus {
            border-color: #E30A17 !important;
            box-shadow: 0 0 0 3px rgba(227, 10, 23, 0.1) !important;
        }
        
        /* LABEL - Koyu & Okunabilir */
        .stTextInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stNumberInput > label,
        .stDateInput > label {
            color: #2D3748 !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            margin-bottom: 10px !important;
            display: block !important;
        }
        
        /* TABS - Temiz Stil */
        .stTabs [data-baseweb="tab-list"] {
            background: #FFFFFF !important;
            border-radius: 8px !important;
            padding: 4px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            background: transparent !important;
            color: #718096 !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: #E30A17 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(227, 10, 23, 0.3) !important;
        }
        
        /* EKSTRA GÜÇLENDİRME - SEÇİLİ TAB YAZISINI BEYAZ YAP */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] * {
            color: #FFFFFF !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
            color: #FFFFFF !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] div {
            color: #FFFFFF !important;
        }
        
        /* KARTLAR - BEYAZ KUTUCUK TASARIMI */
        .metric-card {
            background: #FFFFFF !important;
            padding: 20px !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08) !important;
            text-align: center !important;
            border: 1px solid #E0E0E0 !important;
            border-left: 6px solid #E30A17 !important;
            margin-bottom: 20px !important;
            transition: all 0.3s ease !important;
            overflow: hidden !important;
        }
        
        .metric-card:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1) !important;
        }
        
        .metric-card h3 {
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #666666 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 8px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        
        .metric-card h2 {
            font-size: 34px !important;
            font-weight: 800 !important;
            color: #2C3E50 !important;
            margin: 0 !important;
            line-height: 1.2 !important;
        }
        
        /* BUTONLAR - GSB Kırmızısı */
        .stButton > button {
            background: #E30A17 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            height: 52px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            padding: 0 32px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 16px rgba(227, 10, 23, 0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        .stButton > button:hover {
            background: #C00000 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(227, 10, 23, 0.5) !important;
        }
        
        /* DASHBOARD KARTLARI */
        div[data-testid="column"] .stButton > button[kind="secondary"] {
            background: #FFFFFF !important;
            color: #1A202C !important;
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            height: 120px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            padding: 16px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            white-space: normal !important;
            line-height: 1.4 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        
        div[data-testid="column"] .stButton > button[kind="secondary"]:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 20px rgba(227, 10, 23, 0.2) !important;
            border-color: #E30A17 !important;
        }
        
        /* ALERTLER & BILDIRIMLER */
        .stAlert {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            color: #1A202C !important;
        }
        
        .stAlert p, .stAlert span, .stAlert div {
            color: #1A202C !important;
        }
        
        /* TABLOLAR */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.5) !important;
            border-radius: 10px !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(102, 126, 234, 0.8) !important;
        }
        
        /* ANİMASYONLAR */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        [data-testid="stMarkdownContainer"] {
            animation: fadeIn 0.6s ease-out !important;
        }
        
        [role="option"]:hover {
            background-color: #F0F0F0 !important;
        }
        
        /* === KRİTİK DÜZELTME: EXPANDER İKONU VE "keyboard_arrow_right" YAZISINI GİZLE === */
        /* Streamlit expander içindeki SVG ikonu komple gizle */
        [data-testid="stExpander"] details > summary > svg {
            display: none !important;
        }
        
        /* Summary elementinin list style'ını kaldır */
        [data-testid="stExpander"] details > summary {
            list-style: none !important;
            font-weight: 600 !important;
            color: #2D3748 !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            margin-bottom: 8px !important;
            background-color: #FFFFFF !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stExpander"] details > summary:hover {
            background-color: #F8F9FA !important;
            border-color: #E30A17 !important;
        }
        
        /* Webkit tarayıcılar (Chrome, Safari) için ekstra önlem */
        [data-testid="stExpander"] details > summary::-webkit-details-marker {
            display: none !important;
        }
        
        /* Açık olan expander için */
        [data-testid="stExpander"] details[open] > summary {
            border-color: #E30A17 !important;
            background-color: #FFF5F5 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. VERİTABANI BAĞLANTISI (SUPABASE) ---
@st.cache_resource
def get_supabase_client():
    try:
        # Önce Streamlit Secrets'a bak (Canlı Ortam)
        if hasattr(st, "secrets") and "supabase" in st.secrets:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            return create_client(url, key)
        
        # Yoksa yerel dosyaya bak (Geliştirme Ortamı)
        elif os.path.exists("supabase_config.json"):
            with open("supabase_config.json", "r") as f:
                config = json.load(f)
                return create_client(config["url"], config["key"])
        
        else:
            st.error("Supabase konfigürasyonu bulunamadı! (secrets.toml veya supabase_config.json)")
            return None
    except Exception as e:
        st.error(f"Supabase bağlantı hatası: {str(e)}")
        return None

supabase = get_supabase_client()

# --- 3. LOGİN VE KULLANICI YÖNETİMİ FONKSİYONLARI ---
def hash_password(password):
    """Şifreyi bcrypt ile hashle"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Şifreyi doğrula"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    """Kullanıcı girişi yap"""
    try:
        result = supabase.table('users').select('*').eq('username', username).eq('aktif', True).execute()
        if result.data and len(result.data) > 0:
            user = result.data[0]
            if verify_password(password, user['password_hash']):
                return user
        return None
    except Exception as e:
        st.error(f"Giriş hatası: {e}")
        return None

def log_activity(user_id, username, action, building_name=None, elevator_name=None, details=None):
    """Kullanıcı aktivitesini logla"""
    try:
        supabase.table('activity_logs').insert({
            'user_id': user_id,
            'username': username,
            'action': action,
            'building_name': building_name,
            'elevator_name': elevator_name,
            'details': details
        }).execute()
    except Exception as e:
        print(f"Log hatası: {e}")

def init_session_state():
    """Session state başlat"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_rol' not in st.session_state:
        st.session_state.user_rol = None
    if 'user_building_id' not in st.session_state:
        st.session_state.user_building_id = None

def logout():
    """Çıkış yap"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_rol = None
    st.session_state.user_building_id = None
    st.session_state.auto_login_attempted = False
    st.rerun()

# --- CACHE TEMİZLEME FONKSİYONU ---
def clear_all_caches():
    """Tüm cache'leri temizle"""
    get_buildings_map.clear()
    get_companies_map.clear()
    get_all_elevators.clear()
    get_all_maintenance_logs.clear()

# --- HELPER FUNCTIONS (Supabase için) ---
@st.cache_data(ttl=60)
def get_buildings_map():
    """Buildings UUID -> Name mapping"""
    result = supabase.table('buildings').select('id, bina_adi, company_id').execute()
    return {b['id']: b for b in result.data}

@st.cache_data(ttl=60)
def get_companies_map():
    """Companies UUID -> Name mapping"""
    result = supabase.table('companies').select('id, sirket_adi').execute()
    return {c['id']: c['sirket_adi'] for c in result.data}

@st.cache_data(ttl=60)
def get_all_elevators():
    """Tüm asansörleri cache'den getir"""
    result = supabase.table('elevators').select('*').execute()
    return enrich_elevators(result.data)

@st.cache_data(ttl=60)
def get_all_maintenance_logs():
    """Tüm bakım kayıtlarını cache'den getir"""
    result = supabase.table('maintenance_logs').select('*').execute()
    logs = []
    for log in result.data:
        log_copy = log.copy()
        if log.get('elevator_id'):
            elev_result = supabase.table('elevators').select('*').eq('id', log['elevator_id']).execute()
            if elev_result.data:
                enriched = enrich_elevators(elev_result.data)
                if enriched:
                    log_copy['bina'] = enriched[0].get('bina', '-')
                    log_copy['blok'] = enriched[0].get('blok', '-')
                    log_copy['asansor_kimlik'] = enriched[0].get('kimlik', '-')
                    log_copy['firma'] = enriched[0].get('firma', '-')
        logs.append(log_copy)
    return logs

def enrich_elevators(elevators_data):
    """Elevator verilerine bina ve firma adlarını ekle"""
    buildings_map = get_buildings_map()
    companies_map = get_companies_map()
    
    enriched = []
    for e in elevators_data:
        e_copy = e.copy()
        building_id = e.get('building_id')
        
        if building_id and building_id in buildings_map:
            building = buildings_map[building_id]
            e_copy['bina'] = building['bina_adi']
            
            company_id = building.get('company_id')
            if company_id and company_id in companies_map:
                e_copy['firma'] = companies_map[company_id]
            else:
                e_copy['firma'] = ''
        else:
            e_copy['bina'] = '-'
            e_copy['firma'] = ''
        
        # Etiket bilgisini notlardan parse et veya varsayılan Yeşil
        if 'etiket' not in e_copy or not e_copy.get('etiket'):
            notlar = e_copy.get('notlar', '')
            if 'Etiket:' in notlar:
                # "Etiket: Mavi" gibi notlardan parse et
                try:
                    parts = notlar.split('Etiket:')
                    if len(parts) > 1:
                        etiket = parts[1].strip().split()[0] if parts[1].strip() else 'Yeşil'
                        e_copy['etiket'] = etiket
                    else:
                        e_copy['etiket'] = 'Yeşil'
                except:
                    e_copy['etiket'] = 'Yeşil'
            else:
                e_copy['etiket'] = 'Yeşil'
        
        enriched.append(e_copy)
    
    return enriched

# --- SESSION STATE VE LOGİN KONTROL ---
init_session_state()

# LOGİN SAYFASI - MODERN & BASIT
if not st.session_state.logged_in:
    # Modern gradient arka plan
    st.markdown("""
        <style>
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
            50% { box-shadow: 0 8px 30px rgba(102, 126, 234, 0.8); }
        }
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            animation: gradientShift 8s ease infinite;
        }
        
        .stTextInput > div > div > input {
            border-radius: 10px;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            font-size: 15px;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: scale(1.02);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-size: 200% 200%;
            animation: gradientShift 3s ease infinite;
            color: white;
            border-radius: 10px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Ana container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Boşluk
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        
        # Login kartı
        # Login kartı
        st.markdown("""
            <div style='background: white; padding: 20px 28px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);'>
                <div style='text-align: center; margin-bottom: 20px;'>
                    <div style='font-size: 80px; margin-bottom: 10px; line-height: 1;'>🏢</div>
                    <h1 style='color: #2D3748; margin: 0 0 6px 0; font-size: 24px; font-weight: 700;'>Asansör Takip Sistemi</h1>
                    <p style='color: #718096; font-size: 13px; margin: 0;'>TC Gençlik ve Spor Bakanlığı</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Form
        st.markdown("<div style='margin-top: -10px;'>", unsafe_allow_html=True)
        
        
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı girin", key="login_username")
            password = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin", key="login_password")
            submit = st.form_submit_button("🔓 Giriş Yap", use_container_width=True)
            
            if submit:
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.user_rol = user['rol']
                        st.session_state.user_building_id = user.get('building_id')
                        
                        st.success(f"✅ Hoş geldiniz, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Kullanıcı adı veya şifre hatalı!")
                else:
                    st.warning("⚠️ Lütfen tüm alanları doldurun")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
            <div style='text-align: center; margin-top: 12px; padding: 10px; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);'>
                <p style='margin: 0 0 2px 0; font-size: 12px; color: #666; font-weight: 500;'>
                    Tasarlayan: <strong style='color: #667eea; font-size: 14px; font-weight: 700;'>Yusuf DOLU</strong>
                </p>
                <p style='margin: 0; font-size: 10px; color: #999;'>© 2026 Tüm hakları saklıdır</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# KULLANICI GİRİŞ YAPMIŞ - ANA UYGULAMA

# --- 3. MENÜ ---
with st.sidebar:
    st.markdown("""
    st.markdown("""
        <div style='text-align: center; padding: 20px 0 10px 0;'>
            <div style="font-size: 40px; margin-bottom: 5px; line-height: 1;">🏢</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #2D3748 !important; font-weight: 700; font-size: 20px; margin-top: 0;'>ASANSÖR TAKİP</h3>", unsafe_allow_html=True)
    
    # Kullanıcı bilgisi
    if st.session_state.user and isinstance(st.session_state.user, dict):
        st.markdown(f"""
            <div style='background: #f0f2f6; padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;'>
                <p style='margin: 0; font-size: 14px; color: #555;'>👤 <strong>{st.session_state.user.get('username', 'Kullanıcı')}</strong></p>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #888;'>
                    {'🔑 Yönetici' if st.session_state.user_rol == 'admin' else '🏢 Bina Yetkilisi'}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Rol bazlı menü
    if st.session_state.user_rol == 'admin':
        menu_options = ["Dashboard", "Envanter", "Firma Yönetimi", "Bakım İşlemleri", "💬 Mesajlar", "💰 Ödenek Talebi", "💰 Ödenek Yönetimi", "Raporlar", "Veri Yükleme", "👥 Kullanıcı Yönetimi", "📊 Aktivite Logu"]
        menu_icons = ["speedometer2", "building", "briefcase", "tools", "chat-dots", "cash-coin", "wallet2", "bar-chart", "cloud-upload", "people", "activity"]
    else:
        menu_options = ["Bakım Ekle", "Bakım Geçmişi", "💬 Mesajlar", "💰 Ödenek Talebi"]
        menu_icons = ["plus-circle", "clock-history", "chat-dots", "cash-coin"]
    
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#E30A17", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin":"8px 0", 
                "padding": "12px 16px",
                "--hover-color": "#FFEAEA",
                "color": "#2D3748",
                "font-weight": "500",
                "border-radius": "12px"
            },
            "nav-link-selected": {
                "background": "#E30A17", 
                "color": "#FFFFFF !important",
                "font-weight": "600",
                "box-shadow": "0 4px 12px rgba(227, 10, 23, 0.3)"
            },
        }
    )
    
    st.markdown("---")
    
    # Çıkış Butonu
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        logout()
    
    st.markdown("<p style='text-align: center; color: #A0AEC0 !important; font-size: 12px;'>v2.0 Modern Edition</p>", unsafe_allow_html=True)

# --- 4. SAYFALAR ---

# === BİNA YETKİLİSİ SAYFALARİ ===
if st.session_state.user_rol == 'bina_yetkilisi':
    # Bina yetkilisi sadece kendi binasını görebilir
    user_building_id = st.session_state.user_building_id
    
    if not user_building_id:
        st.error("⚠️ Hesabınıza bina atanmamış. Lütfen yöneticiyle iletişime geçin.")
        st.stop()
    
    # Bina bilgisini al
    building_result = supabase.table('buildings').select('*').eq('id', user_building_id).execute()
    if not building_result.data:
        st.error("⚠️ Bina bulunamadı.")
        st.stop()
    
    user_building = building_result.data[0]
    
    if selected == "Bakım Ekle":
        st.title(f"🔧 Bakım Ekle - {user_building['bina_adi']}")
        st.markdown("---")
        
        # Asansörleri getir (sadece bu binanın)
        elevators_result = supabase.table('elevators').select('*').eq('building_id', user_building_id).execute()
        elevators = enrich_elevators(elevators_result.data)
        
        if not elevators:
            st.warning(f"⚠️ {user_building['bina_adi']} binasında asansör bulunmuyor.")
            st.stop()
        
        # Bakım formu
        elevator_options = []
        for e in elevators:
            blok = e.get('blok', '-')
            kimlik = e.get('kimlik', '-')
            etiket = e.get('etiket_no', '')
            if etiket:
                elevator_options.append(f"{blok} - {kimlik} - Etiket: {etiket}")
            else:
                elevator_options.append(f"{blok} - {kimlik}")
        selected_elevator_str = st.selectbox("🏗️ Asansör Seçin", elevator_options)
        selected_elevator_idx = elevator_options.index(selected_elevator_str)
        selected_elevator_id = elevators[selected_elevator_idx]['id']
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            islem_turu = st.selectbox("İşlem Türü", ["Periyodik Bakım", "Arıza Giderme", "Parça Değişimi", "Revizyon"])
            tarih = st.date_input("İşlem Tarihi")
            bakim_servis_no = st.text_input("🔢 Bakım Servis No", placeholder="Örn: BS-2026-001")
        with col2:
            teknisyen = st.text_input("Bina Yetkilisi", value=st.session_state.user['username'])
            durum = st.selectbox("Durum", ["Tamamlandı", "Devam Ediyor", "Beklemede"])
        
        # Fiyat alanı (Parça Değişimi için)
        degisen_parcalar = ""
        degismesi_gereken_parcalar = ""
        fiyat = None
        if islem_turu == "Parça Değişimi":
            degisen_parcalar = st.text_area(
                "Değişim Yapılan Parçalar (virgülle ayırın, opsiyonel)",
                placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
            )
            st.markdown("---")
            fiyat = st.number_input("💰 Parça Fiyatı (TL)", min_value=0.0, step=10.0, format="%.2f")
        elif islem_turu == "Periyodik Bakım":
            show_degismesi_gereken = st.checkbox("Değişmesi Gereken Parçalar Var", value=False)
            if show_degismesi_gereken:
                degismesi_gereken_parcalar = st.text_area(
                    "Değişmesi Gereken Parçalar (virgülle ayırın, opsiyonel)",
                    placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
                )
            show_degisen = st.checkbox("Değişim Yapılan Parçalar Var", value=False)
            if show_degisen:
                degisen_parcalar = st.text_area(
                    "Değişim Yapılan Parçalar (virgülle ayırın, opsiyonel)",
                    placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
                )
            fiyat = None
        else:
            fiyat = None

        aciklama = st.text_area(
            "Yapılan İşlem Detayı / Açıklama",
            height=200,
            placeholder="Detaylı açıklama yazın..."
        )
        
        # Etiket değiştirme
        st.markdown("---")
        etiket_degistir = st.checkbox("🏷️ Asansörün etiket durumunu değiştirmek istiyorum")
        yeni_etiket = None
        if etiket_degistir:
            st.warning("⚠️ Etiket durumunu değiştirmek üzeresiniz!")
            yeni_etiket = st.selectbox("Yeni Etiket Durumu", ["Yeşil", "Mavi", "Sarı", "Kırmızı"])
        
        if st.button("💾 İşlemi Kaydet ve Tamamla", type="primary", use_container_width=True):
            try:
                # Fiyat ve parça bilgilerini notlara ekle
                notlar_son = aciklama if aciklama else ""
                if degismesi_gereken_parcalar:
                    notlar_son += f"\n\n🟡 Değişmesi Gereken Parçalar: {degismesi_gereken_parcalar}"
                if degisen_parcalar:
                    notlar_son += f"\n\n🔧 Değişim Yapılan Parçalar: {degisen_parcalar}"
                if fiyat and fiyat > 0:
                    notlar_son += f"\n\n💰 Maliyet: {fiyat:.2f} TL"
                # Bakım kaydını ekle
                maintenance_data = {
                    "elevator_id": selected_elevator_id,
                    "bakim_tarihi": str(tarih),
                    "yapilan_islem": islem_turu,
                    "teknisyen": teknisyen,
                    "sonraki_bakim": None,
                    "notlar": notlar_son,
                    "durum": durum,
                    "bakim_servis_no": bakim_servis_no if bakim_servis_no else None
                }
                supabase.table("maintenance_logs").insert(maintenance_data).execute()
                # Aktivite logu
                log_activity(
                    st.session_state.user['id'],
                    st.session_state.user['username'],
                    'bakım_eklendi',
                    user_building['bina_adi'],
                    selected_elevator_str,
                    f"{islem_turu} - {durum}"
                )
                # Cache temizle
                clear_all_caches()
                # Etiket güncelle
                if etiket_degistir and yeni_etiket:
                    supabase.table("elevators").update({
                        "etiket": yeni_etiket
                    }).eq("id", selected_elevator_id).execute()
                    st.success(f"✅ Bakım kaydedildi ve etiket '{yeni_etiket}' olarak güncellendi!")
                else:
                    st.success("✅ Bakım kaydı başarıyla işlendi!")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Hata: {e}")
            # açıklama zorunlu değil, uyarı kaldırıldı
    
    elif selected == "Bakım Geçmişi":
        st.title(f"📋 Bakım Geçmişi - {user_building['bina_adi']}")
        
        # Sadece bu binaya ait bakım kayıtları
        elevators_result = supabase.table('elevators').select('id').eq('building_id', user_building_id).execute()
        elevator_ids = [e['id'] for e in elevators_result.data]
        
        if not elevator_ids:
            st.warning("⚠️ Henüz bakım kaydı yok.")
            st.stop()
        
        # Bakım kayıtlarını getir
        all_bakim = get_all_maintenance_logs()
        bakim_filtered = [b for b in all_bakim if b.get('elevator_id') in elevator_ids]
        
        if bakim_filtered:
            import streamlit as st
            import pandas as pd
            df = pd.DataFrame(bakim_filtered)
            st.markdown(f"### 📊 Toplam {len(bakim_filtered)} Bakım Kaydı")
            st.markdown("---")
            # Arama
            arama = st.text_input("🔎 Ara (Asansör, Teknisyen, Not...)")
            if arama:
                mask = df.astype(str).apply(lambda row: row.str.contains(arama, case=False).any(), axis=1)
                df = df[mask]
            # Sıralama seçenekleri
            st.markdown("#### Sıralama ve Filtreleme")
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_col = st.selectbox("Sırala", ["En Yeni (Tarih)", "En Eski (Tarih)", "Servis No", "Teknisyen", "Durum"])
            with col2:
                durum_filter = st.multiselect("Durum Filtrele", options=sorted(df["durum"].dropna().unique()) if "durum" in df.columns else [], default=[])
            with col3:
                teknisyen_filter = st.multiselect("Teknisyen Filtrele", options=sorted(df["teknisyen"].dropna().unique()) if "teknisyen" in df.columns else [], default=[])
            # Filtre uygula
            if durum_filter:
                df = df[df["durum"].isin(durum_filter)]
            if teknisyen_filter:
                df = df[df["teknisyen"].isin(teknisyen_filter)]
            # Sıralama uygula
            if sort_col == "En Yeni (Tarih)" and "bakim_tarihi" in df.columns:
                df = df.sort_values("bakim_tarihi", ascending=False)
            elif sort_col == "En Eski (Tarih)" and "bakim_tarihi" in df.columns:
                df = df.sort_values("bakim_tarihi", ascending=True)
            elif sort_col == "Servis No" and "bakim_servis_no" in df.columns:
                df = df.sort_values("bakim_servis_no", ascending=True)
            elif sort_col == "Teknisyen" and "teknisyen" in df.columns:
                df = df.sort_values("teknisyen", ascending=True)
            elif sort_col == "Durum" and "durum" in df.columns:
                df = df.sort_values("durum", ascending=True)
            # Gruplama ve gösterim
            if len(df) > 0:
                df['asansor_kimlik'] = df['asansor_kimlik'].fillna('-')
                df['blok'] = df['blok'].fillna('-')
                asansor_groups = df.groupby(['blok', 'asansor_kimlik'])
                for (blok, asansor_kimlik), grup in asansor_groups:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; 
                                padding: 15px 20px; 
                                border-radius: 10px; 
                                margin: 20px 0 10px 0;
                                color: #2D3748;
                                font-weight: 600;
                                font-size: 16px;
                                border: 2px solid #E2E8F0;">
                        🏘️ {blok} • 🆔 {asansor_kimlik} <span style="background: #F0F0F0; padding: 4px 12px; border-radius: 15px; margin-left: 10px;">{len(grup)} kayıt</span>
                    </div>
                    """, unsafe_allow_html=True)
                    display_cols = ['bakim_servis_no', 'bakim_tarihi', 'yapilan_islem', 'teknisyen', 'durum', 'notlar']
                    available_cols = [col for col in display_cols if col in grup.columns]
                    df_display = grup[available_cols].copy()
                    col_mapping = {
                        'bakim_servis_no': '🔢 Servis No',
                        'bakim_tarihi': '📅 Tarih',
                        'yapilan_islem': '⚙️ İşlem',
                        'teknisyen': '👷 Teknisyen',
                        'durum': '📊 Durum',
                        'notlar': '📝 Notlar'
                    }
                    df_display.columns = [col_mapping.get(col, col) for col in available_cols]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Arama sonucu bulunamadı.")
        else:
            st.warning("⚠️ Henüz bakım kaydı yok.")
    
    elif selected == "💬 Mesajlar":
        st.title("💬 Mesajlar")
        
        tab1, tab2, tab3 = st.tabs(["📥 Gelen Kutusu", "📤 Giden Kutusu", "✉️ Yeni Mesaj"])
        
        with tab1:
            st.markdown("### 📥 Gelen Mesajlar")
            
            try:
                # Gelen mesajları getir
                messages_result = supabase.table('messages').select('*').eq('receiver_id', st.session_state.user['id']).order('created_at', desc=True).execute()
                
                if messages_result.data:
                    for msg in messages_result.data:
                        # Gönderen bilgisini al
                        sender_result = supabase.table('users').select('username').eq('id', msg['sender_id']).execute()
                        sender_name = sender_result.data[0]['username'] if sender_result.data else 'Bilinmeyen'
                        
                        # Asansör bilgilerini hazırla
                        elevator_info_html = ""
                        if msg.get('elevator_ids'):
                            elevator_names = []
                            for elev_id in msg['elevator_ids']:
                                elev_result = supabase.table('elevators').select('kimlik, blok').eq('id', elev_id).execute()
                                if elev_result.data:
                                    elev = elev_result.data[0]
                                    elevator_names.append(f"{elev.get('blok', '-')} - {elev.get('kimlik', '-')}")
                            
                            if elevator_names:
                                elevator_info_html = f'<div style="color: #4A5568; margin-bottom: 12px;"><strong>🛗 İlgili Asansörler:</strong> {", ".join(elevator_names)}</div>'
                        
                        # Mesaj içeriğini hazırla
                        message_content = msg['message'].replace('\n', '<br>')
                        
                        # Tüm kartı tek HTML string olarak oluştur (giden kutusu gibi)
                        # Okunmamış mesajlar için farklı stil
                        border_color = "#E30A17" if not msg['is_read'] else "#48BB78"
                        status_badge = "🔴 Yeni" if not msg['is_read'] else "✅ Okundu"
                        status_bg = '#FED7D7' if not msg['is_read'] else '#C6F6D5'
                        status_color = '#C53030' if not msg['is_read'] else '#22543D'

                        card_html = f"""
<div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {border_color}; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h4 style="margin: 0; color: #1A202C;">📧 {msg.get('subject', 'Konu yok')}</h4>
<span style="color: #718096; font-size: 14px;">{format_tarih(msg['created_at'])}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div style="color: #4A5568;"><strong>Gönderen:</strong> {sender_name}</div>
<span style="background: {status_bg}; color: {status_color}; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;">{status_badge}</span>
</div>
{elevator_info_html}
<div style="background: #F7FAFC; padding: 12px; border-radius: 8px; color: #2D3748; line-height: 1.6; margin-bottom: 12px;">
{message_content}
</div>
</div>
"""
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Butonlar: Okundu işaretle ve Sil
                        col1, col2 = st.columns(2)
                        with col1:
                            if not msg['is_read']:
                                if st.button("✅ Okundu Olarak İşaretle", key=f"mark_read_bina_{msg['id']}", use_container_width=True):
                                    supabase.table('messages').update({'is_read': True}).eq('id', msg['id']).execute()
                                    st.success("Mesaj okundu olarak işaretlendi!")
                                    time.sleep(0.5)
                                    st.rerun()
                        with col2:
                            if st.button("🗑️ Sil", key=f"delete_inbox_bina_{msg['id']}", use_container_width=True, type="secondary"):
                                if st.session_state.get(f"confirm_delete_inbox_bina_{msg['id']}", False):
                                    supabase.table('messages').delete().eq('id', msg['id']).execute()
                                    st.success("Mesaj silindi!")
                                    if f"confirm_delete_inbox_bina_{msg['id']}" in st.session_state:
                                        del st.session_state[f"confirm_delete_inbox_bina_{msg['id']}"]
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.session_state[f"confirm_delete_inbox_bina_{msg['id']}"] = True
                                    st.warning("⚠️ Tekrar 'Sil' butonuna tıklayarak onaylayın!")
                                    st.rerun()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.info("📭 Gelen mesaj bulunmuyor.")
            except Exception as e:
                st.error("Mesajlar yüklenirken bir bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
                print(f"Gelen mesajlar hatası: {e}")
        
        with tab2:
            st.markdown("### 📤 Gönderilen Mesajlar")
            
            try:
                # Gönderilen mesajları getir
                sent_messages = supabase.table('messages').select('*').eq('sender_id', st.session_state.user['id']).order('created_at', desc=True).execute()
                
                if sent_messages.data:
                    for msg in sent_messages.data:
                        # Asansör bilgilerini hazırla
                        elevator_info_html = ""
                        if msg.get('elevator_ids'):
                            elevator_names = []
                            for elev_id in msg['elevator_ids']:
                                elev_result = supabase.table('elevators').select('kimlik, blok').eq('id', elev_id).execute()
                                if elev_result.data:
                                    elev = elev_result.data[0]
                                    elevator_names.append(f"{elev.get('blok', '-')} - {elev.get('kimlik', '-')}")
                            
                            if elevator_names:
                                elevator_info_html = f'<div style="color: #4A5568; margin-bottom: 12px;"><strong>🛗 İlgili Asansörler:</strong> {", ".join(elevator_names)}</div>'
                        
                        # Mesaj içeriğini hazırla
                        message_content = msg['message'].replace('\n', '<br>')
                        
                        # Tüm kartı tek HTML string olarak oluştur
                        card_html = f"""
<div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #E30A17; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h4 style="margin: 0; color: #1A202C;">📧 {msg.get('subject', 'Konu yok')}</h4>
<span style="color: #718096; font-size: 14px;">{format_tarih(msg['created_at'])}</span>
</div>
<div style="color: #4A5568; margin-bottom: 12px;">
<strong>Alıcı:</strong> Yönetici
</div>
{elevator_info_html}
<div style="background: #F7FAFC; padding: 12px; border-radius: 8px; color: #2D3748; line-height: 1.6; margin-bottom: 12px;">
{message_content}
</div>
</div>
"""
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Silme butonu
                        if st.button("🗑️ Sil", key=f"delete_outbox_bina_{msg['id']}", use_container_width=True, type="secondary"):
                            if st.session_state.get(f"confirm_delete_outbox_bina_{msg['id']}", False):
                                supabase.table('messages').delete().eq('id', msg['id']).execute()
                                st.success("Mesaj silindi!")
                                if f"confirm_delete_outbox_bina_{msg['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_outbox_bina_{msg['id']}"]
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_outbox_bina_{msg['id']}"] = True
                                st.warning("⚠️ Tekrar 'Sil' butonuna tıklayarak onaylayın!")
                                st.rerun()
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.info("📭 Gönderilen mesaj bulunmuyor.")
            except Exception as e:
                st.error("Gönderilen mesajlar yüklenirken bir bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
                print(f"Giden mesajlar hatası: {e}")
        
        with tab3:
            st.markdown("### ✉️ Yeni Mesaj Gönder")
            
            with st.form("new_message_form_bina"):
                try:
                    # Bina yetkilisi sadece admin'e gönderir
                    admin_result = supabase.table('users').select('id').eq('rol', 'admin').eq('aktif', True).execute()
                    if admin_result.data:
                        receiver_id = admin_result.data[0]['id']
                        st.info("📧 Mesaj yöneticiye gönderilecek")
                    else:
                        st.error("⚠️ Admin kullanıcı bulunamadı")
                        receiver_id = None
                    
                    subject = st.text_input("📌 Konu", key="msg_subject_bina")
                    message = st.text_area("✍️ Mesaj", height=200, key="msg_content_bina")
                    
                    submit = st.form_submit_button("📨 Gönder", use_container_width=True)
                except Exception as e:
                    st.error("Yönetici bilgisi yüklenirken bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
                    print(f"Bina yetkilisi yeni mesaj formu hatası: {e}")
                    receiver_id = None
                    subject = None
                    message = None
                    submit = False
                
                if submit and receiver_id:
                    if subject and message:
                        try:
                            supabase.table('messages').insert({
                                'sender_id': st.session_state.user['id'],
                                'receiver_id': receiver_id,
                                'subject': subject,
                                'message': message,
                                'is_read': False
                            }).execute()
                            
                            st.success("✅ Mesaj başarıyla gönderildi!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Hata: {e}")
                    else:
                        st.warning("⚠️ Lütfen konu ve mesaj alanlarını doldurun")
    
    elif selected == "💰 Ödenek Talebi":
        # Admin veya bina yetkilisi kontrolü
        if st.session_state.user_rol == 'admin':
            st.title("💰 Ödenek Talebi Oluştur (Admin)")
        else:
            st.title(f"💰 Ödenek Talebi - {user_building['bina_adi']}")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📝 Yeni Talep Oluştur", "📋 Taleplerim"])
        
        with tab1:
            st.subheader("Yeni Ödenek Talebi")
            
            # Admin için: Kim adına talep oluşturuyor?
            selected_user_id = st.session_state.user['id']
            selected_building_id = user_building_id if st.session_state.user_rol != 'admin' else None
            
            if st.session_state.user_rol == 'admin':
                st.info("👤 Admin olarak tüm binalar için talep oluşturabilirsiniz")
                
                talep_sahipligi = st.radio(
                    "Kim adına talep oluşturuyorsunuz?",
                    ["👔 Kendim Adına (Admin)", "👤 Bina Yetkilisi Adına"],
                    horizontal=True
                )
                
                # Bina seçimi
                buildings_result = supabase.table('buildings').select('*').order('bina_adi').execute()
                if buildings_result.data:
                    building_names = [b['bina_adi'] for b in buildings_result.data]
                    selected_building_name = st.selectbox("🏢 Bina Seçin", building_names)
                    selected_building_idx = building_names.index(selected_building_name)
                    selected_building_id = buildings_result.data[selected_building_idx]['id']
                    selected_building = buildings_result.data[selected_building_idx]
                else:
                    st.error("Bina bulunamadı!")
                    st.stop()
                
                # Bina yetkilisi adına ise, o binanın yetkilisini seç
                if talep_sahipligi == "👤 Bina Yetkilisi Adına":
                    users_result = supabase.table('users').select('*').eq('building_id', selected_building_id).eq('rol', 'bina_yetkilisi').execute()
                    if users_result.data:
                        user_names = [f"{u['username']} ({u['email']})" for u in users_result.data]
                        if user_names:
                            selected_user_str = st.selectbox("👤 Bina Yetkilisi Seçin", user_names)
                            selected_user_idx = user_names.index(selected_user_str)
                            selected_user_id = users_result.data[selected_user_idx]['id']
                            st.success(f"✅ Talep **{users_result.data[selected_user_idx]['username']}** adına oluşturulacak")
                        else:
                            st.warning(f"⚠️ {selected_building_name} binası için bina yetkilisi bulunamadı. Kendiniz adına oluşturabilirsiniz.")
                    else:
                        st.warning(f"⚠️ {selected_building_name} binası için bina yetkilisi bulunamadı.")
            else:
                selected_building = user_building
            
            st.markdown("---")
            
            # Hedef seçimi (sadece admin seçebilir - hem kendi hem bina yetkilisi adına)
            if st.session_state.user_rol == 'admin':
                st.markdown("### 🎯 Talep Hedefi")
                talep_hedefi_secim = st.radio(
                    "Ödenek nereden talep edilecek?",
                    ["🏛️ İl Müdürlüğü", "📍 Doğrudan Ankara"],
                    horizontal=True,
                    help="İl Müdürlüğü: Normal süreç | Ankara: Hızlı süreç (acil durumlar)"
                )
                talep_hedefi = 'ankara' if talep_hedefi_secim == "📍 Doğrudan Ankara" else 'il_mudurluk'
                
                if talep_hedefi == 'ankara':
                    st.warning("⚡ Bu talep doğrudan Ankara'ya iletilecektir (acil durum süreci)")
                else:
                    st.info("ℹ️ Bu talep önce İl Müdürlüğü'nden onay alacak, sonra gerekirse Ankara'ya iletilecek")
            else:
                # Bina yetkilisi her zaman İl Müdürlüğü'ne talep eder
                talep_hedefi = 'il_mudurluk'
                st.info("ℹ️ Bu talep İl Müdürlüğü'ne gönderilecektir.")
            
            st.markdown("---")
            
            # Talep türü seçimi
            talep_turu = st.radio(
                "Ödenek talebi ne için?",
                ["🏗️ Belirli Bir Asansör İçin", "🏢 Tüm Bina İçin (Genel)"],
                horizontal=True
            )
            
            selected_elevator_id = None
            selected_elevator_str = None
            
            if talep_turu == "🏗️ Belirli Bir Asansör İçin":
                # Asansör seçimi
                elevators_result = supabase.table('elevators').select('*').eq('building_id', selected_building_id).execute()
                elevators = enrich_elevators(elevators_result.data)
                
                if not elevators:
                    st.warning("⚠️ Asansör bulunamadı.")
                    st.stop()
                
                elevator_options = []
                for e in elevators:
                    blok = e.get('blok', '-')
                    kimlik = e.get('kimlik', '-')
                    etiket = e.get('etiket_no', '')
                    if etiket:
                        elevator_options.append(f"{blok} - {kimlik} - Etiket: {etiket}")
                    else:
                        elevator_options.append(f"{blok} - {kimlik}")
                
                selected_elevator_str = st.selectbox("🏗️ Asansör Seçin", elevator_options)
                selected_elevator_idx = elevator_options.index(selected_elevator_str)
                selected_elevator_id = elevators[selected_elevator_idx]['id']
                
                # Bakım kaydı ile ilişkilendirme (opsiyonel)
                st.markdown("---")
                bakim_ile_iliski = st.checkbox("Bu talep bir bakım/arıza kaydı ile ilişkili")
                selected_maintenance_id = None
                
                if bakim_ile_iliski:
                    # Bu asansörün bakım kayıtlarını getir
                    all_bakim = get_all_maintenance_logs()
                    elevator_bakim = [b for b in all_bakim if b.get('elevator_id') == selected_elevator_id]
                    
                    if elevator_bakim:
                        bakim_options = []
                        for b in elevator_bakim:
                            servis_no = b.get('bakim_servis_no', 'Yok')
                            tarih = b.get('bakim_tarihi', '-')
                            islem = b.get('yapilan_islem', '-')
                            bakim_options.append(f"{servis_no} | {tarih} | {islem}")
                        
                        selected_bakim_str = st.selectbox("İlişkili Bakım Kaydı", bakim_options)
                        selected_bakim_idx = bakim_options.index(selected_bakim_str)
                        selected_maintenance_id = elevator_bakim[selected_bakim_idx]['id']
                    else:
                        st.warning("Bu asansör için bakım kaydı bulunamadı.")
            else:
                st.info(f"📢 Bu talep **{selected_building['bina_adi']}** binasının tamamı için oluşturulacak.")
                selected_maintenance_id = None
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                tutar = st.number_input("💵 Talep Edilen Tutar (TL)", min_value=0.0, step=100.0, format="%.2f")
            with col2:
                talep_tarihi = st.date_input("📅 Talep Tarihi", value=datetime.now())
            
            aciklama = st.text_area(
                "📝 Talep Açıklaması",
                height=150,
                placeholder="Ödenek talebinizin detaylarını yazın..."
            )
            
            if st.button("💾 Talebi Gönder", type="primary", use_container_width=True):
                if aciklama and tutar > 0:
                    try:
                        odenek_data = {
                            "building_id": selected_building_id,
                            "elevator_id": selected_elevator_id,
                            "maintenance_id": selected_maintenance_id,
                            "talep_eden_user_id": selected_user_id,
                            "talep_tarihi": str(talep_tarihi),
                            "talep_hedefi": talep_hedefi,
                            "tutar": float(tutar),
                            "aciklama": aciklama,
                            "durum": "Beklemede"
                        }
                        supabase.table("odenek_talepleri").insert(odenek_data).execute()
                        
                        # Aktivite logu
                        talep_detay = selected_elevator_str if selected_elevator_str else f"Tüm {selected_building['bina_adi']} binası"
                        log_activity(
                            st.session_state.user['id'],
                            st.session_state.user['username'],
                            'odenek_talep',
                            selected_building['bina_adi'],
                            talep_detay,
                            f"{tutar:.2f} TL ödenek talebi oluşturuldu" + (" (Admin)" if st.session_state.user_rol == 'admin' else "")
                        )
                        
                        st.success("✅ Ödenek talebi başarıyla gönderildi!")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
                else:
                    st.warning("⚠️ Lütfen tüm alanları doldurun ve geçerli bir tutar girin!")
        
        with tab2:
            st.subheader("Taleplerim")
            
            try:
                # Kullanıcının taleplerini getir
                talepler_result = supabase.table('odenek_talepleri')\
                    .select('*')\
                    .eq('talep_eden_user_id', st.session_state.user['id'])\
                    .order('talep_tarihi', desc=True)\
                    .execute()
                
                if talepler_result.data:
                    for talep in talepler_result.data:
                        # Bina bilgisini getir
                        building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                        bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                        
                        # Asansör bilgisini getir (varsa)
                        if talep.get('elevator_id'):
                            elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                            if elevator_info.data:
                                elev = enrich_elevators(elevator_info.data)[0]
                                hedef_str = f"🏢 {bina_adi} - 🏗️ {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                            else:
                                hedef_str = f"🏢 {bina_adi} (Asansör bulunamadı)"
                        else:
                            hedef_str = f"🏢 {bina_adi} (Tüm Bina)"
                        
                        # Durum rengini belirle
                        durum = talep['durum']
                        if durum == 'Onaylandı':
                            durum_renk = '#28a745'
                            durum_icon = '✅'
                        elif durum == 'Reddedildi':
                            durum_renk = '#dc3545'
                            durum_icon = '❌'
                        else:
                            durum_renk = '#ffc107'
                            durum_icon = '⏳'
                        
                        # Hedef bilgisi
                        talep_hedefi = talep.get('talep_hedefi', 'il_mudurluk')
                        hedef_badge = "🏛️ İl Müdürlüğü" if talep_hedefi == 'il_mudurluk' else "📍 Ankara"
                        hedef_renk = "#3b82f6" if talep_hedefi == 'il_mudurluk' else "#8b5cf6"
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid {durum_renk};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <h4 style="margin: 0; color: #2D3748;">{hedef_str}</h4>
                                <div style="display: flex; gap: 8px;">
                                    <span style="background: {hedef_renk}; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 13px;">
                                        {hedef_badge}
                                    </span>
                                    <span style="background: {durum_renk}; color: white; padding: 6px 15px; border-radius: 20px; font-weight: 600;">
                                        {durum_icon} {durum}
                                    </span>
                                </div>
                            </div>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Durum mesajları
                        if durum == 'Onaylandı':
                            # İl Müdürlük onayladı
                            ankara_durum = talep.get('ankara_durum', 'Beklemede')
                            
                            if ankara_durum == 'Onaylandı':
                                st.success(f"🎉 İl Müdürlük onayladı! Ankara da onayladı! Ödenek alınabilir.")
                                if talep.get('ankara_onay_tarihi'):
                                    st.info(f"📅 Ankara Onay: {format_tarih(talep['ankara_onay_tarihi'])}")
                            elif talep.get('ankara_talep_tarihi'):
                                st.info(f"✅ İl Müdürlük onayladı! Ankara'ya bildirildi ({format_tarih(talep['ankara_talep_tarihi'])}). Ankara onayı bekleniyor...")
                            else:
                                st.warning("✅ İl Müdürlük onayladı! Ankara'ya bildirilecek.")
                        elif durum == 'Reddedildi':
                            st.error("❌ İl Müdürlük tarafından reddedildi.")
                        
                        if talep.get('onay_notu'):
                            st.info(f"💬 İl Müdürlük Notu: {talep['onay_notu']}")
                        
                        if talep.get('ankara_onay_notu'):
                            st.info(f"💬 Ankara Notu: {talep['ankara_onay_notu']}")
                        
                        # Beklemedeyse düzenleme/silme izni ver
                        if durum == 'Beklemede':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✏️ Düzenle", key=f"edit_{talep['id']}", use_container_width=True):
                                    st.session_state[f"editing_{talep['id']}"] = True
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Sil", key=f"delete_{talep['id']}", use_container_width=True):
                                    if st.session_state.get(f"confirm_delete_{talep['id']}"):
                                        try:
                                            supabase.table('odenek_talepleri').delete().eq('id', talep['id']).execute()
                                            st.success("✅ Talep silindi!")
                                            time.sleep(1)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Hata: {e}")
                                    else:
                                        st.session_state[f"confirm_delete_{talep['id']}"] = True
                                        st.warning("⚠️ Tekrar bas silmek için!")
                        
                        # Düzenleme formu
                        if st.session_state.get(f"editing_{talep['id']}"):
                            with st.expander("✏️ Düzenle", expanded=True):
                                new_tutar = st.number_input("💵 Tutar", value=float(talep['tutar']), key=f"tutar_{talep['id']}")
                                new_aciklama = st.text_area("📝 Açıklama", value=talep['aciklama'], key=f"aciklama_{talep['id']}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("💾 Kaydet", key=f"save_{talep['id']}", type="primary"):
                                        try:
                                            supabase.table('odenek_talepleri').update({
                                                'tutar': new_tutar,
                                                'aciklama': new_aciklama
                                            }).eq('id', talep['id']).execute()
                                            del st.session_state[f"editing_{talep['id']}"]
                                            st.success("✅ Güncellendi!")
                                            time.sleep(1)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Hata: {e}")
                                with col2:
                                    if st.button("❌ İptal", key=f"cancel_{talep['id']}"):
                                        del st.session_state[f"editing_{talep['id']}"]
                                        st.rerun()
                        
                        st.markdown("---")
                else:
                    st.info("📭 Henüz ödenek talebiniz bulunmuyor.")
            except Exception as e:
                st.error(f"❌ Talepler getirilemedi: {e}")
    
    st.stop()

# === ADMIN SAYFALARİ ===

# === ADMIN ÖDENEK TALEBİ ===
if selected == "💰 Ödenek Talebi" and st.session_state.user_rol == 'admin':
    st.title("💰 Ödenek Talebi Oluştur (Admin)")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Yeni Talep Oluştur", "📋 Tüm Talepler"])
    
    with tab1:
        st.subheader("Yeni Ödenek Talebi")
        
        # Bina seçimi
        buildings_result = supabase.table('buildings').select('*').execute()
        building_options = [b['bina_adi'] for b in buildings_result.data]
        selected_building_name = st.selectbox("🏢 Bina Seçin", building_options)
        selected_building = next(b for b in buildings_result.data if b['bina_adi'] == selected_building_name)
        selected_building_id = selected_building['id']
        
        # Talep türü seçimi
        talep_turu = st.radio(
            "Ödenek talebi ne için?",
            ["🏗️ Belirli Bir Asansör İçin", "🏢 Tüm Bina İçin (Genel)"],
            horizontal=True
        )
        
        selected_elevator_id = None
        selected_elevator_str = None
        selected_maintenance_id = None
        
        if talep_turu == "🏗️ Belirli Bir Asansör İçin":
            # Asansör seçimi
            elevators_result = supabase.table('elevators').select('*').eq('building_id', selected_building_id).execute()
            elevators = enrich_elevators(elevators_result.data)
            
            if not elevators:
                st.warning("⚠️ Bu binada asansör bulunamadı.")
            else:
                elevator_options = []
                for e in elevators:
                    blok = e.get('blok', '-')
                    kimlik = e.get('kimlik', '-')
                    etiket = e.get('etiket_no', '')
                    if etiket:
                        elevator_options.append(f"{blok} - {kimlik} - Etiket: {etiket}")
                    else:
                        elevator_options.append(f"{blok} - {kimlik}")
                
                selected_elevator_str = st.selectbox("🏗️ Asansör Seçin", elevator_options)
                selected_elevator_idx = elevator_options.index(selected_elevator_str)
                selected_elevator_id = elevators[selected_elevator_idx]['id']
                
                # Bakım kaydı ile ilişkilendirme
                st.markdown("---")
                bakim_ile_iliski = st.checkbox("Bu talep bir bakım/arıza kaydı ile ilişkili")
                
                if bakim_ile_iliski:
                    all_bakim = get_all_maintenance_logs()
                    elevator_bakim = [b for b in all_bakim if b.get('elevator_id') == selected_elevator_id]
                    
                    if elevator_bakim:
                        bakim_options = []
                        for b in elevator_bakim:
                            servis_no = b.get('bakim_servis_no', 'Yok')
                            tarih = b.get('bakim_tarihi', '-')
                            islem = b.get('yapilan_islem', '-')
                            bakim_options.append(f"{servis_no} | {tarih} | {islem}")
                        
                        selected_bakim_str = st.selectbox("İlişkili Bakım Kaydı", bakim_options)
                        selected_bakim_idx = bakim_options.index(selected_bakim_str)
                        selected_maintenance_id = elevator_bakim[selected_bakim_idx]['id']
                    else:
                        st.warning("Bu asansör için bakım kaydı bulunamadı.")
        else:
            st.info(f"📢 Bu talep **{selected_building_name}** binasının tamamı için oluşturulacak.")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            tutar = st.number_input("💵 Talep Edilen Tutar (TL)", min_value=0.0, step=100.0, format="%.2f")
        with col2:
            talep_tarihi = st.date_input("📅 Talep Tarihi", value=datetime.now())
        
        aciklama = st.text_area(
            "📝 Talep Açıklaması",
            height=150,
            placeholder="Ödenek talebinin detaylarını yazın..."
        )
        
        if st.button("💾 Talebi Oluştur", type="primary", use_container_width=True):
            if aciklama and tutar > 0:
                try:
                    odenek_data = {
                        "building_id": selected_building_id,
                        "elevator_id": selected_elevator_id,
                        "maintenance_id": selected_maintenance_id,
                        "talep_eden_user_id": st.session_state.user['id'],
                        "talep_tarihi": str(talep_tarihi),
                        "talep_hedefi": 'il_mudurluk',
                        "tutar": float(tutar),
                        "aciklama": aciklama,
                        "durum": "Beklemede"
                    }
                    supabase.table("odenek_talepleri").insert(odenek_data).execute()
                    
                    # Aktivite logu
                    talep_detay = selected_elevator_str if selected_elevator_str else f"Tüm {selected_building_name} binası"
                    log_activity(
                        st.session_state.user['id'],
                        st.session_state.user['username'],
                        'odenek_talep',
                        selected_building_name,
                        talep_detay,
                        f"{tutar:.2f} TL ödenek talebi oluşturuldu (Admin)"
                    )
                    
                    st.success("✅ Ödenek talebi başarıyla oluşturuldu!")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata: {e}")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun ve geçerli bir tutar girin!")
    
    with tab2:
        st.subheader("Tüm Ödenek Talepleri")
        
        try:
            # Tüm talepleri getir
            talepler_result = supabase.table('odenek_talepleri')\
                .select('*')\
                .order('talep_tarihi', desc=True)\
                .execute()
            
            if talepler_result.data:
                # Durum filtreleme
                durum_filter = st.selectbox("Durum Filtrele", ["Tümü", "Beklemede", "Onaylandı", "Reddedildi"])
                
                filtered_talepler = talepler_result.data if durum_filter == "Tümü" else [t for t in talepler_result.data if t['durum'] == durum_filter]
                
                st.markdown(f"### 📊 {len(filtered_talepler)} Talep Bulundu")
                st.markdown("---")
                
                for talep in filtered_talepler:
                    # Bina bilgisi
                    building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                    bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                    
                    # Asansör bilgisi (varsa)
                    if talep.get('elevator_id'):
                        elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                        if elevator_info.data:
                            elev = enrich_elevators(elevator_info.data)[0]
                            hedef_str = f"🏢 {bina_adi} - 🏗️ {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                        else:
                            hedef_str = f"🏢 {bina_adi} (Asansör bulunamadı)"
                    else:
                        hedef_str = f"🏢 {bina_adi} (Tüm Bina)"
                    
                    # Talep eden kullanıcı
                    user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                    talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                    
                    # Durum rengi
                    durum = talep['durum']
                    if durum == 'Onaylandı':
                        durum_renk = '#28a745'
                        durum_icon = '✅'
                    elif durum == 'Reddedildi':
                        durum_renk = '#dc3545'
                        durum_icon = '❌'
                    else:
                        durum_renk = '#ffc107'
                        durum_icon = '⏳'
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid {durum_renk};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: #2D3748;">{hedef_str}</h4>
                            <span style="background: {durum_renk}; color: white; padding: 6px 15px; border-radius: 20px; font-weight: 600;">
                                {durum_icon} {durum}
                            </span>
                        </div>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if talep.get('onay_notu'):
                        st.info(f"💬 Yönetici Notu: {talep['onay_notu']}")
                    
                    # Admin düzenleme/silme butonları
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Düzenle", key=f"admin_edit_{talep['id']}", use_container_width=True):
                            st.session_state[f"admin_editing_{talep['id']}"] = True
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Sil", key=f"admin_delete_{talep['id']}", use_container_width=True):
                            if st.session_state.get(f"admin_confirm_delete_{talep['id']}"):
                                try:
                                    supabase.table('odenek_talepleri').delete().eq('id', talep['id']).execute()
                                    st.success("✅ Talep silindi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                            else:
                                st.session_state[f"admin_confirm_delete_{talep['id']}"] = True
                                st.warning("⚠️ Tekrar bas silmek için!")
                    
                    # Düzenleme formu
                    if st.session_state.get(f"admin_editing_{talep['id']}"):
                        with st.expander("✏️ Düzenle", expanded=True):
                            new_tutar = st.number_input("💵 Tutar", value=float(talep['tutar']), key=f"admin_tutar_{talep['id']}")
                            new_aciklama = st.text_area("📝 Açıklama", value=talep['aciklama'], key=f"admin_aciklama_{talep['id']}")
                            new_durum = st.selectbox("📊 Durum", ["Beklemede", "Onaylandı", "Reddedildi"], 
                                                     index=["Beklemede", "Onaylandı", "Reddedildi"].index(talep['durum']),
                                                     key=f"admin_durum_{talep['id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("💾 Kaydet", key=f"admin_save_{talep['id']}", type="primary"):
                                    try:
                                        update_data = {
                                            'tutar': new_tutar,
                                            'aciklama': new_aciklama,
                                            'durum': new_durum
                                        }
                                        if new_durum in ['Onaylandı', 'Reddedildi'] and talep['durum'] == 'Beklemede':
                                            update_data['onaylayan_user_id'] = st.session_state.user['id']
                                            update_data['onay_tarihi'] = datetime.now().isoformat()
                                        
                                        supabase.table('odenek_talepleri').update(update_data).eq('id', talep['id']).execute()
                                        del st.session_state[f"admin_editing_{talep['id']}"]
                                        st.success("✅ Güncellendi!")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Hata: {e}")
                            with col2:
                                if st.button("❌ İptal", key=f"admin_cancel_{talep['id']}"):
                                    del st.session_state[f"admin_editing_{talep['id']}"]
                                    st.rerun()
                    
                    st.markdown("---")
            else:
                st.info("📭 Henüz ödenek talebi bulunmuyor.")
        except Exception as e:
            st.error(f"❌ Talepler getirilemedi: {e}")

# === DASHBOARD (İNTERAKTİF VERSİYON) ===
if selected == "Dashboard":
    # DASHBOARD BAŞLIĞI - ÖZEL TASARIM
    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 80px; margin-bottom: 10px; line-height: 1; animation: float 6s ease-in-out infinite;">📊</div>
            <h1 style="color: #2D3748; font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -1px;">İnteraktif Durum Paneli</h1>
            <p style="color: #718096; font-size: 16px; margin-top: 5px;">Sistem Genel Bakış ve İstatistikler</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Session State Başlatma
    if 'dashboard_view' not in st.session_state:
        st.session_state.dashboard_view = 'ana_panel'
    
    # Supabase'den gerçek verileri çek (CACHE'Lİ)
    try:
        buildings_result = supabase.table("buildings").select("*").execute()
        total_bina = len(buildings_result.data)
        
        # Cache'den hızlı getir
        elevators_list = get_all_elevators()
        bakim_list = get_all_maintenance_logs()
    except Exception as e:
        st.error(f"⚠️ Veritabanı hatası: {str(e)[:100]}")
        total_bina = 0
        elevators_list = []
        bakim_list = []
    
    total_asansor = len(elevators_list)
    bu_ay_bakim = len(bakim_list)
    
    # Etiket Durumlarını Say
    yeşil_sayisi = sum(1 for e in elevators_list if e.get('etiket') == 'Yeşil')
    mavi_sayisi = sum(1 for e in elevators_list if e.get('etiket') == 'Mavi')
    sari_sayisi = sum(1 for e in elevators_list if e.get('etiket') == 'Sarı')
    kirmizi_sayisi = sum(1 for e in elevators_list if e.get('etiket') == 'Kırmızı')

    # 2. TIKLANABİLİR BÜYÜK KART BUTONLARI
    if st.session_state.dashboard_view == 'ana_panel':
        
        # Beyaz kutucuk stili - Düzenli Hizalama
        st.markdown("""
        <style>
        /* Tüm kolonları eşit genişlikte yap */
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 0 !important;
        }
        
        /* Buton stilleri */
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
            background-color: white !important;
            border: 2px solid #E5E7EB !important;
            color: #1A202C !important;
            font-weight: 600 !important;
            padding: 2rem 1rem !important;
            height: 140px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            gap: 0.5rem !important;
            transition: all 0.2s !important;
            white-space: pre-line !important;
            line-height: 1.4 !important;
        }
        
        div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
            border-color: #E30A17 !important;
            box-shadow: 0 4px 12px rgba(227, 10, 23, 0.15) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Buton içindeki p elementleri */
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 0.95rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            if st.button(f"🏢\n\nToplam Bina\n\n{total_bina}", key="card_bina", use_container_width=True, type="secondary"):
                st.session_state.dashboard_view = 'binalar'
                st.rerun()
        
        with col2:
            if st.button(f"🛗\n\nToplam Asansör\n\n{total_asansor}", key="card_asansor", use_container_width=True, type="secondary"):
                st.session_state.dashboard_view = 'tum_asansorler'
                st.rerun()
        
        with col3:
            if st.button(f"🔧\n\nTüm Bakım Geçmişi\n\n{bu_ay_bakim}", key="card_bakim", use_container_width=True, type="secondary"):
                st.session_state.dashboard_view = 'bakim_gecmisi'
                st.rerun()
        
        with col4:
            emoji = "🚨" if kirmizi_sayisi > 0 else "✅"
            if st.button(f"{emoji}\n\nKırmızı Etiket\n\n{kirmizi_sayisi}", key="card_kirmizi", use_container_width=True, type="secondary"):
                st.session_state.dashboard_view = 'kirmizi_etiket'
                st.rerun()
    
    else:
        # GERİ DÖN BUTONU (Detay görünümlerinde)
        if st.button("⬅️ Ana Panele Dön", type="primary"):
            st.session_state.dashboard_view = 'ana_panel'
            st.rerun()
    
    # Uyarı Mesajı
    if kirmizi_sayisi > 0 and st.session_state.dashboard_view == 'ana_panel':
        st.error(f"⚠️ DİKKAT: {kirmizi_sayisi} adet Kırmızı Etiketli asansör var!")
    
    st.markdown("---")
    
    # 3. DİNAMİK İÇERİK (Session State'e Göre)
    if st.session_state.dashboard_view == 'ana_panel':
        # GRAFİK VE İSTATİSTİKLER
        left_col, right_col = st.columns([1.5, 1])
        
        with left_col:
            st.subheader("📊 Etiket Durum Analizi")
            if total_asansor > 0:
                etiket_data = pd.DataFrame({
                    'Etiket': ['Yeşil', 'Mavi', 'Sarı', 'Kırmızı'],
                    'Sayı': [yeşil_sayisi, mavi_sayisi, sari_sayisi, kirmizi_sayisi]
                })
                etiket_data = etiket_data[etiket_data['Sayı'] > 0]
                
                if len(etiket_data) > 0:
                    fig = px.pie(
                        etiket_data, 
                        values='Sayı', 
                        names='Etiket',
                        color='Etiket',
                        color_discrete_map={
                            'Yeşil': '#28a745',
                            'Mavi': '#17a2b8',
                            'Sarı': '#ffc107',
                            'Kırmızı': '#dc3545'
                        },
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Henüz asansör eklenmemiş.")
        
        with right_col:
            st.subheader("📈 Hızlı İstatistikler")
            st.metric("✅ Yeşil", yeşil_sayisi, delta="Güvenli")
            st.metric("🔵 Mavi", mavi_sayisi)
            st.metric("⚠️ Sarı", sari_sayisi)
            st.metric("🚨 Kırmızı", kirmizi_sayisi, delta="Acil!" if kirmizi_sayisi > 0 else None, delta_color="inverse")
        
        st.markdown("---")
        st.subheader("� Son 10 Bakım Hareketi")
        if len(bakim_list) > 0:
            son_10_bakim = bakim_list[-10:] if len(bakim_list) > 10 else bakim_list
            df_bakim = pd.DataFrame(son_10_bakim)
            
            display_cols = []
            col_mapping = {}
            
            if 'bakim_tarihi' in df_bakim.columns:
                display_cols.append('bakim_tarihi')
                col_mapping['bakim_tarihi'] = '📅 Tarih'
            if 'bina' in df_bakim.columns:
                display_cols.append('bina')
                col_mapping['bina'] = '🏢 Bina'
            if 'blok' in df_bakim.columns:
                display_cols.append('blok')
                col_mapping['blok'] = '🏛️ Blok'
            if 'asansor_kimlik' in df_bakim.columns:
                display_cols.append('asansor_kimlik')
                col_mapping['asansor_kimlik'] = '🛗 Asansör'
            if 'yapilan_islem' in df_bakim.columns:
                display_cols.append('yapilan_islem')
                col_mapping['yapilan_islem'] = '⚙️ İşlem'
            if 'teknisyen' in df_bakim.columns:
                display_cols.append('teknisyen')
                col_mapping['teknisyen'] = '👷 Teknisyen'
            if 'durum' in df_bakim.columns:
                display_cols.append('durum')
                col_mapping['durum'] = '📊 Durum'
            
            if display_cols:
                df_display = df_bakim[display_cols].copy()
                df_display = df_display.rename(columns=col_mapping)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_bakim, use_container_width=True, hide_index=True
)
        else:
            st.info("📝 Henüz bakım kaydı girilmemiş.")
    
    elif st.session_state.dashboard_view == 'binalar':
        st.title("🏢 Tüm Binalar")
        try:
            buildings = supabase.table("buildings").select("*").execute().data
            if len(buildings) > 0:
                # Firma adlarını ekle
                companies_map = get_companies_map()
                for b in buildings:
                    if b.get('company_id') and b['company_id'] in companies_map:
                        b['firma'] = companies_map[b['company_id']]
                    else:
                        b['firma'] = '-'
                
                df_bina = pd.DataFrame(buildings)
                
                # Sadece kullanıcıya anlamlı kolonları göster
                display_cols = []
                col_mapping = {
                    'bina_adi': '🏢 Bina Adı',
                    'ilce': '📍 İlçe',
                    'adres': '🗺️ Adres',
                    'firma': '🔧 Bakım Firması'
                }
                
                for col_key, col_display in col_mapping.items():
                    if col_key in df_bina.columns:
                        display_cols.append(col_key)
                
                if display_cols:
                    df_display = df_bina[display_cols].copy()
                    df_display.columns = [col_mapping[col] for col in display_cols]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_bina, use_container_width=True, hide_index=True)
                
                st.success(f"✅ Toplam {len(buildings)} bina kayıtlı")
            else:
                st.warning("⚠️ Henüz bina kaydı yok.")
        except Exception as e:
            st.error(f"Hata: {e}")
    
    elif st.session_state.dashboard_view == 'tum_asansorler':
        st.title("🛗 Tüm Asansörler")
        if len(elevators_list) > 0:
            df = pd.DataFrame(elevators_list)
            
            # FİLTRELEME VE ARAMA ÖZELLİKLERİ
            st.markdown("### 🔍 Filtreleme ve Arama")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Bina filtresi
                tum_binalar = ['Tümü'] + sorted(df['bina'].unique().tolist()) if 'bina' in df.columns else ['Tümü']
                secili_bina = st.selectbox("🏢 Bina Filtrele", tum_binalar)
            
            with col2:
                # Etiket filtresi
                tum_etiketler = ['Tümü', 'Yeşil', 'Mavi', 'Sarı', 'Kırmızı']
                secili_etiket = st.selectbox("🎨 Etiket Filtrele", tum_etiketler)
            
            with col3:
                # Firma filtresi
                tum_firmalar = ['Tümü'] + sorted(df['firma'].unique().tolist()) if 'firma' in df.columns else ['Tümü']
                secili_firma = st.selectbox("🔧 Firma Filtrele", tum_firmalar)
            
            # Arama kutusu
            arama_text = st.text_input("🔎 Asansör Ara (Kimlik No, Blok, vb.)", "")
            
            # Sıralama
            siralama_secenekleri = {
                'Bina (A-Z)': ('bina', True),
                'Bina (Z-A)': ('bina', False),
                'Kimlik No': ('kimlik', True),
                'Etiket': ('etiket', True)
            }
            siralama = st.selectbox("📊 Sıralama", list(siralama_secenekleri.keys()))
            
            # Filtreleme uygula
            df_filtered = df.copy()
            
            if secili_bina != 'Tümü' and 'bina' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['bina'] == secili_bina]
            
            if secili_etiket != 'Tümü' and 'etiket' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['etiket'] == secili_etiket]
            
            if secili_firma != 'Tümü' and 'firma' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['firma'] == secili_firma]
            
            # Arama uygula
            if arama_text:
                mask = df_filtered.astype(str).apply(lambda row: row.str.contains(arama_text, case=False, na=False).any(), axis=1)
                df_filtered = df_filtered[mask]
            
            # Sıralama uygula
            sort_col, sort_asc = siralama_secenekleri[siralama]
            if sort_col in df_filtered.columns:
                df_filtered = df_filtered.sort_values(by=sort_col, ascending=sort_asc)
            
            st.markdown("---")
            
            # Sadece kullanıcıya anlamlı kolonları seç
            display_columns = []
            col_mapping = {
                'bina': '🏢 Bina',
                'blok': '🏛️ Blok',
                'firma': '🔧 Bakım Firması',
                'kimlik': '🆔 Kimlik No',
                'etiket_no': '🏷️ Etiket No',
                'tip': '⚙️ Tip',
                'etiket': '🎨 Etiket'
            }
            
            # Mevcut kolonları kontrol et ve ekle
            for col_key, col_display in col_mapping.items():
                if col_key in df_filtered.columns:
                    display_columns.append(col_key)
            
            if display_columns and len(df_filtered) > 0:
                df_display = df_filtered[display_columns].copy()
                
                # Kolon isimlerini Türkçeleştir
                df_display.columns = [col_mapping[col] for col in display_columns]
                
                # Etiket rengini renklendir
                if '🎨 Etiket' in df_display.columns:
                    df_display['🎨 Etiket'] = df_display['🎨 Etiket'].apply(etiket_rengi_goster)
                    st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.success(f"✅ {len(df_filtered)} asansör gösteriliyor (Toplam: {len(elevators_list)})")
            else:
                st.warning("⚠️ Filtrelere uygun asansör bulunamadı.")
        else:
            st.warning("⚠️ Henüz asansör kaydı yok.")
    
    elif st.session_state.dashboard_view == 'kirmizi_etiket':
        st.title("🔴 Kırmızı Etiketli (Riskli) Asansörler")
        kirmizi_asansorler = [e for e in elevators_list if e.get('etiket') == 'Kırmızı']
        if len(kirmizi_asansorler) > 0:
            df_kirmizi = pd.DataFrame(kirmizi_asansorler)
            
            # Etiket rengini HTML ile renklendir
            if 'etiket' in df_kirmizi.columns:
                df_kirmizi['etiket_renkli'] = df_kirmizi['etiket'].apply(etiket_rengi_goster)
                try:
                    # FİRMA SÜTUNU EKLE
                    display_cols = ["bina", "blok", "firma", "kimlik", "tip", "etiket_renkli", "son_bakim"]
                    df_display = df_kirmizi[[col for col in display_cols if col in df_kirmizi.columns]]
                    
                    # Sütun isimlerini Türkçeleştir
                    df_display.columns = ["Bina", "Blok", "Bakım Firması", "Kimlik", "Tip", "Etiket", "Son Bakım"]
                    
                    st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
                except:
                    st.dataframe(df_kirmizi, use_container_width=True, hide_index=True)
            else:
                try:
                    st.dataframe(df_kirmizi[["bina", "blok", "firma", "kimlik", "tip", "son_bakim"]], 
                               use_container_width=True, hide_index=True)
                except:
                    st.dataframe(df_kirmizi, use_container_width=True, hide_index=True)
            st.error(f"⚠️ UYARI: {len(kirmizi_asansorler)} adet kırmızı etiketli asansör tespit edildi!")
        else:
            st.success("✅ Kırmızı etiketli asansör yok!")
    
    elif st.session_state.dashboard_view == 'bakim_gecmisi':
        st.title("🔧 Tüm Bakım Geçmişi")
        if len(bakim_list) > 0:
            import pandas as pd
            df_bakim_full = pd.DataFrame(bakim_list)
            # EXCEL İNDİRME BUTONLARI (aynı bırak)
            col_excel1, col_excel2, col_excel3 = st.columns([1, 1, 2])
            with col_excel1:
                def bakim_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        export_cols = ['bina', 'blok', 'asansor_kimlik', 'bakim_tarihi', 'yapilan_islem', 'teknisyen', 'durum', 'notlar', 'firma']
                        df_export = df[[col for col in export_cols if col in df.columns]].copy()
                        df_export.columns = ['Bina', 'Blok', 'Asansör', 'Tarih', 'İşlem', 'Teknisyen', 'Durum', 'Notlar', 'Firma']
                        df_export.to_excel(writer, sheet_name='Bakım Geçmişi', index=False)
                        worksheet = writer.sheets['Bakım Geçmişi']
                        worksheet.set_column('A:A', 20)
                        worksheet.set_column('B:B', 12)
                        worksheet.set_column('C:C', 25)
                        worksheet.set_column('D:D', 12)
                        worksheet.set_column('E:E', 18)
                        worksheet.set_column('F:F', 18)
                        worksheet.set_column('G:G', 12)
                        worksheet.set_column('H:H', 50)
                        worksheet.set_column('I:I', 18)
                    output.seek(0)
                    return output
                excel_bakim = bakim_to_excel(df_bakim_full)
                st.download_button(
                    label="📥 Bakım Geçmişi Excel",
                    data=excel_bakim,
                    file_name=f"bakim_gecmisi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_excel2:
                def asansorler_to_excel(elevators):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_elev = pd.DataFrame(elevators)
                        export_cols = ['bina', 'blok', 'kimlik', 'etiket', 'tip', 'firma']
                        df_export = df_elev[[col for col in export_cols if col in df_elev.columns]].copy()
                        df_export.columns = ['Bina', 'Blok', 'Asansör Kimlik', 'Etiket', 'Tip', 'Firma']
                        df_export.to_excel(writer, sheet_name='Asansörler', index=False)
                        worksheet = writer.sheets['Asansörler']
                        worksheet.set_column('A:A', 20)
                        worksheet.set_column('B:B', 12)
                        worksheet.set_column('C:C', 30)
                        worksheet.set_column('D:D', 12)
                        worksheet.set_column('E:E', 12)
                        worksheet.set_column('F:F', 18)
                    output.seek(0)
                    return output
                excel_asansor = asansorler_to_excel(elevators_list)
                st.download_button(
                    label="📥 Asansör Listesi Excel",
                    data=excel_asansor,
                    file_name=f"asansor_listesi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            st.markdown("---")
            # ARAMA FİLTRESİ
            arama_text = st.text_input("🔎 Ara (Bina, Asansör, Teknisyen, Not...)", key="arama_bakim")
            df_filtered = df_bakim_full.copy()
            if arama_text:
                mask = df_filtered.astype(str).apply(lambda row: row.str.contains(arama_text, case=False).any(), axis=1)
                df_filtered = df_filtered[mask]
            st.markdown("---")
            # ASANSÖRE GÖRE GRUPLU TABLO
            if len(df_filtered) > 0:
                df_filtered['bina'] = df_filtered['bina'].fillna('-')
                df_filtered['blok'] = df_filtered['blok'].fillna('-')
                df_filtered['asansor_kimlik'] = df_filtered['asansor_kimlik'].fillna('-')
                asansor_gruplari = df_filtered.groupby(['bina', 'blok', 'asansor_kimlik'])
                st.markdown(f"### 📋 {len(asansor_gruplari)} Asansör - {len(df_filtered)} Bakım Kaydı")
                st.markdown("---")
                for (bina, blok, asansor_kimlik), grup in asansor_gruplari:
                    kayit_sayisi = len(grup)
                    st.markdown(f"""
                    <div style=\"background: #FFFFFF; 
                                padding: 15px 20px; 
                                border-radius: 10px; 
                                margin: 20px 0 10px 0;
                                color: #2D3748;
                                font-weight: 600;
                                font-size: 16px;
                                border: 2px solid #E2E8F0;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);\">
                        🏢 {bina} • 🏘️ {blok} • 🆔 {asansor_kimlik} <span style=\"background: #F0F0F0; color: #2D3748; padding: 4px 12px; border-radius: 15px; margin-left: 10px;\">{kayit_sayisi} kayıt</span>
                    </div>
                    """, unsafe_allow_html=True)
                    display_cols = ['bakim_servis_no', 'bakim_tarihi', 'yapilan_islem', 'teknisyen', 'durum', 'notlar']
                    col_mapping = {
                        'bakim_servis_no': '🔢 Servis No',
                        'bakim_tarihi': '📅 Tarih',
                        'yapilan_islem': '⚙️ İşlem',
                        'teknisyen': '👷 Teknisyen',
                        'durum': '📊 Durum',
                        'notlar': '📝 Notlar'
                    }
                    available_cols = [col for col in display_cols if col in grup.columns]
                    if available_cols:
                        df_display = grup[available_cols].copy()
                        df_display = df_display.rename(columns=col_mapping)
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Arama sonucu bulunamadı.")
        else:
            st.warning("⚠️ Henüz bakım kaydı girilmemiş.")
    
    # === YAKLAŞAN BAKIMLAR TAKVİMİ (YENİ ÖZELLİK) ===
    elif st.session_state.dashboard_view == 'ana':
        st.markdown("---")
        st.markdown("### 📅 Yaklaşan Bakım Takvimi")
        
        try:
            # Tüm asansörleri çek
            asansorler_result = supabase.table("elevators").select("*").execute()
            asansorler = enrich_elevators(asansorler_result.data)
            
            if asansorler:
                bugun = datetime.now().date()
                bakim_takvim = []
                
                for asansor in asansorler:
                    son_bakim_str = asansor.get('son_bakim', '-')
                    if son_bakim_str and son_bakim_str != "-":
                        try:
                            son_bakim_date = datetime.strptime(son_bakim_str, "%Y-%m-%d").date()
                            gelecek_bakim = son_bakim_date + timedelta(days=30)
                            kalan_gun = (gelecek_bakim - bugun).days
                            
                            # Durum ikonu
                            if kalan_gun < 0:
                                durum = "🔴 GECİKMİŞ"
                            elif kalan_gun <= 5:
                                durum = "🟡 YAKIN"
                            else:
                                durum = "🟢 NORMAL"
                            
                            bakim_takvim.append({
                                "Bina": asansor.get('bina', '-'),
                                "Blok": asansor.get('blok', '-'),
                                "Asansör": asansor.get('kimlik', '-'),
                                "Firma": asansor.get('firma', 'Belirtilmemiş'),
                                "Son Bakım": son_bakim_str,
                                "Hedef Tarih": str(gelecek_bakim),
                                "Kalan Gün": kalan_gun,
                                "Durum": durum
                            })
                        except:
                            pass
                
                if bakim_takvim:
                    df_takvim = pd.DataFrame(bakim_takvim).sort_values(by="Kalan Gün")
                    
                    # Sadece yaklaşanları göster (15 gün içinde veya gecikmiş)
                    df_yaklasan = df_takvim[df_takvim['Kalan Gün'] <= 15]
                    
                    if not df_yaklasan.empty:
                        st.dataframe(df_yaklasan, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ 15 gün içinde yapılması gereken bakım yok!")
                else:
                    st.info("ℹ️ Bakım tarihi hesaplanabilmesi için asansörlere bakım kaydı girilmelidir.")
            else:
                st.info("ℹ️ Henüz asansör kaydı bulunmuyor.")
                
        except Exception as e:
            st.error(f"Takvim yüklenirken hata: {e}")
    

# === ENVANTER (BİNA & ASANSÖR EKLEME & SECERE) ===
elif selected == "Envanter":
    st.markdown("## 🏢 Envanter Yönetimi")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Bina Ekle", "🛗 Asansör Tanımla", "📜 Asansör Seceresi", "⚙️ Düzenle / Sil"])

    # -- Sekme 1: Bina Ekleme --
    with tab1:
        st.markdown("<h3 style='color: #1E1E1E !important; margin-bottom: 20px;'>Yeni Bina Kaydı</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            bina_adi = st.text_input("🏢 Bina / Yurt Adı", placeholder="Örn: Yakutiye Yurdu")
        with col2:
            ilce = st.text_input("📍 İlçe", placeholder="Örn: Palandöken")
        
        # FİRMA SEÇİMİ - Firmalardan dropdown
        try:
            firmalar_result = supabase.table("companies").select("sirket_adi").execute()
            firma_listesi = [f['sirket_adi'] for f in firmalar_result.data if f.get('sirket_adi')]
        except:
            firma_listesi = []
        
        if firma_listesi:
            bina_firmasi = st.selectbox("🔧 Bu Binanın Bakım Firması", ["Firma Seçiniz"] + firma_listesi, key="bina_firma_select")
        else:
            st.warning("⚠️ Henüz firma kaydı yok. 'Firma Yönetimi' menüsünden firma ekleyebilirsiniz.")
            bina_firmasi = st.text_input("🔧 Bakım Firması (Manuel)", placeholder="Firma adı giriniz")
        
        adres = st.text_area("📝 Açık Adres", placeholder="Detaylı adres bilgisi giriniz...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✅ Binayı Kaydet", key="save_building"):
            if bina_adi:
                # Firma kontrolü ve UUID bulma
                company_id = None
                final_firma = bina_firmasi if bina_firmasi != "Firma Seçiniz" else ""
                
                if final_firma:
                    # Firma adından UUID bul
                    firma_result = supabase.table("companies").select("id").eq("sirket_adi", final_firma).execute()
                    if firma_result.data:
                        company_id = firma_result.data[0]['id']
                
                try:
                    supabase.table("buildings").insert({
                        "bina_adi": bina_adi,
                        "adres": adres,
                        "yetkili_kisi": "",
                        "telefon": "",
                        "company_id": company_id
                    }).execute()
                    st.success(f"✅ **{bina_adi}** başarıyla sisteme kaydedildi! (Firma: {final_firma if final_firma else 'Belirtilmedi'})")
                    clear_all_caches()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata oluştu: {e}")
            else:
                st.warning("⚠️ Lütfen en azından bina adını giriniz!")

    # -- Sekme 2: Asansör Ekleme --
    with tab2:
        st.markdown("<h3 style='color: #1E1E1E !important; margin-bottom: 20px;'>Asansör Envanter Kaydı</h3>", unsafe_allow_html=True)
        
        # Binaları Çek
        try:
            buildings_result = supabase.table("buildings").select("*").execute()
            bina_dict = {b['bina_adi']: b for b in buildings_result.data}
            bina_listesi = list(bina_dict.keys())
        except:
            bina_listesi = []
            bina_dict = {}
            
        if not bina_listesi:
            st.error("⚠️ **Önce sisteme bina eklemelisiniz!** Yukarıdaki 'Bina Ekle' sekmesinden bina kaydı yapabilirsiniz.")
        else:
            secilen_bina = st.selectbox("🏢 Bina Seçin", bina_listesi)
            
            # BİNADAN FİRMA BİLGİSİNİ OTOMATİK ÇEK
            selected_building = bina_dict.get(secilen_bina, {})
            company_id = selected_building.get('company_id')
            bina_firmasi = ''
            if company_id:
                company_result = supabase.table("companies").select("sirket_adi").eq("id", company_id).execute()
                if company_result.data:
                    bina_firmasi = company_result.data[0]['sirket_adi']
            
            if bina_firmasi:
                st.info(f"🔧 **Bakım Firması:** {bina_firmasi} _(Binadan otomatik atandı)_")
            else:
                st.warning("⚠️ Bu binaya firma atanmamış. Binayı düzenleyerek firma ekleyebilirsiniz.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                kimlik_32 = st.text_input("🔢 Asansör Kimlik No (32 Haneli) - Opsiyonel", placeholder="Örn: TR123456789012345678901234567890")
                etiket_no = st.text_input("🏷️ Asansör Etiket No *", placeholder="Örn: TR-25-001")
                blok = st.text_input("🏛️ Blok Adı", placeholder="Örn: A Blok, B Blok")
            with c2:
                tip = st.selectbox("⚙️ Asansör Tipi", ["İnsan", "Yük", "Sedye", "Monşarj"])
                etiket = st.selectbox("🏷️ Mevcut Etiket Rengi", ["Yeşil", "Mavi", "Sarı", "Kırmızı"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✅ Asansörü Kaydet", key="save_elevator"):
                # Etiket no veya 32 haneli kimlikten biri olmalı
                if (kimlik_32 or etiket_no) and secilen_bina:
                    # Building UUID'sini al
                    building_uuid = selected_building['id']
                    kimlik_final = kimlik_32 if kimlik_32 else etiket_no
                    
                    try:
                        supabase.table("elevators").insert({
                            "building_id": building_uuid,
                            "blok": blok,
                            "kimlik": kimlik_final,
                            "etiket_no": etiket_no if etiket_no else "",
                            "kapasite": "",

                            "tip": tip,
                            "katlar": "",
                            "notlar": f"Etiket: {etiket}"
                        }).execute()
                        st.success(f"✅ **{kimlik_final}** ({blok}) numaralı asansör **{secilen_bina}** binasına başarıyla eklendi!")
                        clear_all_caches()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
                else:
                    st.warning("⚠️ En az bir kimlik numarası (32 haneli veya etiket no) ve bina seçimi zorunludur!")
    
    # -- Sekme 3: ASANSÖR SECERESİ (BAKIM KARNESI) --
    with tab3:
        st.markdown("<h3 style='color: #1E1E1E !important; margin-bottom: 20px;'>📜 Asansör Bakım Karnesi</h3>", unsafe_allow_html=True)
        st.info("Bir asansör seçin, tüm bakım geçmişini görün!")
        
        # Tüm asansörleri listele
        try:
            elevators_result = supabase.table("elevators").select("*").execute()
            all_elevators = enrich_elevators(elevators_result.data)
            
            # Okunabilir format için dictionary oluştur
            elevator_options = {}
            for e in all_elevators:
                bina = e.get('bina', 'Bilinmiyor')
                blok = e.get('blok', '-')
                kimlik = e.get('etiket_no') or e.get('kimlik', '')
                display_text = f"{bina} - {blok} - {kimlik}"
                elevator_options[display_text] = e['id']  # UUID
        except:
            elevator_options = {}
        
        if not elevator_options:
            st.warning("⚠️ Sistemde asansör bulunmuyor.")
        else:
            secilen_display = st.selectbox("🛗 Asansör Seçin", list(elevator_options.keys()), key="asansor_secere_select")
            secilen_asansor_secere = elevator_options[secilen_display]  # Gerçek ID'yi al
            
            if secilen_asansor_secere:
                st.markdown("---")
                
                # Asansör Bilgileri
                try:
                    # Elevator detaylarını çek
                    elevator_result = supabase.table("elevators").select("*").eq("id", secilen_asansor_secere).execute()
                    if not elevator_result.data:
                        st.error("Asansör bulunamadı!")
                    else:
                        asansor_data = enrich_elevators(elevator_result.data)[0]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🏢 Bina", asansor_data.get('bina', '-'))
                        with col2:
                            st.metric("⚙️ Tip", asansor_data.get('tip', '-'))
                        with col3:
                            st.metric("🏷️ Tip", asansor_data.get('tip', '-'))
                        
                        st.markdown("---")
                        st.subheader("📋 Bakım Geçmişi")
                        
                        # Bu asansöre ait tüm bakım kayıtlarını çek
                        bakim_result = supabase.table("maintenance_logs").select("*").eq("elevator_id", secilen_asansor_secere).execute()
                        bakim_gecmis = bakim_result.data
                        
                        if len(bakim_gecmis) > 0:
                            df_gecmis = pd.DataFrame(bakim_gecmis)
                            # Tarihe göre sırala
                            if 'bakim_tarihi' in df_gecmis.columns:
                                df_gecmis = df_gecmis.sort_values('bakim_tarihi', ascending=False)
                            
                            st.dataframe(
                                df_gecmis[["bakim_tarihi", "yapilan_islem", "teknisyen", "notlar"]],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("📝 Bu asansöre henüz bakım kaydı girilmemiş.")
                        
                except Exception as e:
                    st.error(f"Veri çekilirken hata: {e}")
    
    # -- Sekme 4: DÜZENLEME VE SİLME İŞLEMLERİ --
    with tab4:
        st.markdown("<h3 style='color: #1E1E1E !important; margin-bottom: 20px;'>⚙️ Düzenleme ve Silme İşlemleri</h3>", unsafe_allow_html=True)
        
        islem_turu = st.radio("İşlem Türünü Seçin:", ["Bina Düzenle", "Asansör Düzenle", "Bina Sil", "Asansör Sil"], horizontal=True)
        
        st.markdown("---")
        
        if islem_turu == "Bina Düzenle":
            st.info("💡 Mevcut binaların firma bilgisini güncelleyebilirsiniz.")
            
            try:
                buildings_result = supabase.table("buildings").select("*").execute()
                binalar = buildings_result.data
                
                if binalar:
                    bina_isimleri = [b['bina_adi'] for b in binalar]
                    duzenlenecek_bina = st.selectbox("🏢 Düzenlenecek Binayı Seçin", bina_isimleri, key="duzenle_bina_sec")
                    
                    # Seçilen binanın mevcut bilgileri
                    bina_info = next(b for b in binalar if b['bina_adi'] == duzenlenecek_bina)
                    
                    # Firma adını getir
                    mevcut_firma = "Belirtilmemiş"
                    if bina_info.get('company_id'):
                        firma_result = supabase.table("companies").select("sirket_adi").eq("id", bina_info['company_id']).execute()
                        if firma_result.data:
                            mevcut_firma = firma_result.data[0]['sirket_adi']
                    
                    st.markdown("### Mevcut Bilgiler")
                    st.write(f"**İlçe:** {bina_info.get('ilce', '-')}")
                    st.write(f"**Adres:** {bina_info.get('adres', '-')}")
                    st.write(f"**Mevcut Firma:** {mevcut_firma}")
                    
                    st.markdown("---")
                    st.markdown("### Yeni Firma Seç")
                    
                    # Firma listesi
                    try:
                        companies_result = supabase.table("companies").select("*").execute()
                        firma_listesi = [f['sirket_adi'] for f in companies_result.data]
                    except:
                        firma_listesi = []
                    
                    if firma_listesi:
                        yeni_firma = st.selectbox("🔧 Yeni Bakım Firması", ["Değiştirme"] + firma_listesi)
                        
                        if st.button("✅ Firmayı Güncelle", type="primary", use_container_width=True):
                            if yeni_firma != "Değiştirme":
                                # Firma ID'sini bul
                                firma_id_result = supabase.table("companies").select("id").eq("sirket_adi", yeni_firma).execute()
                                new_company_id = firma_id_result.data[0]['id'] if firma_id_result.data else None
                                
                                # Binayı güncelle
                                supabase.table("buildings").update({
                                    "company_id": new_company_id
                                }).eq("id", bina_info['id']).execute()
                                
                                st.success(f"✅ **{duzenlenecek_bina}** binasının firması **{yeni_firma}** olarak güncellendi!")
                                clear_all_caches()
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.warning("⚠️ Lütfen yeni bir firma seçin.")
                    else:
                        st.warning("⚠️ Sistemde firma bulunmuyor. 'Firma Yönetimi' menüsünden firma ekleyebilirsiniz.")
                else:
                    st.info("📋 Sistemde bina bulunmuyor.")
            except Exception as e:
                st.error(f"Hata: {e}")
        
        elif islem_turu == "Asansör Düzenle":
            st.info("💡 Asansör bilgilerini güncelleyebilirsiniz.")
            
            try:
                elevators_result = supabase.table("elevators").select("*").execute()
                asansorler = enrich_elevators(elevators_result.data)
                
                if asansorler:
                    # Asansörleri dropdown'da göster
                    asansor_display = [f"{a.get('bina', '-')} - {a.get('blok', '-')} - {a.get('etiket_no') or a.get('kimlik', '-')}" for a in asansorler]
                    secilen = st.selectbox("🛗 Düzenlenecek Asansörü Seçin", asansor_display, key="duzenle_asansor_sec")
                    
                    # Seçilen asansörün bilgilerini bul
                    secilen_index = asansor_display.index(secilen)
                    asansor_info = asansorler[secilen_index]
                    
                    st.markdown("---")
                    st.markdown("### Asansör Bilgilerini Güncelle")
                    
                    # Binaları çek
                    try:
                        buildings_result = supabase.table("buildings").select("*").execute()
                        bina_listesi = [b['bina_adi'] for b in buildings_result.data]
                        bina_map = {b['bina_adi']: b['id'] for b in buildings_result.data}
                    except:
                        bina_listesi = []
                        bina_map = {}
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        yeni_bina = st.selectbox("🏢 Bina", bina_listesi, index=bina_listesi.index(asansor_info.get('bina')) if asansor_info.get('bina') in bina_listesi else 0)
                        yeni_kimlik_32 = st.text_input("🔢 Asansör Kimlik No (32 Haneli)", value=asansor_info.get('kimlik', ''))
                        yeni_etiket_no = st.text_input("🏷️ Asansör Etiket No", value=asansor_info.get('etiket_no', ''))
                        yeni_blok = st.text_input("🏛️ Blok Adı", value=asansor_info.get('blok', ''))
                    
                    with c2:
                        tip_listesi = ["İnsan", "Yük", "Sedye", "Monşarj"]
                        mevcut_tip = asansor_info.get('tip', 'İnsan')
                        yeni_tip = st.selectbox("⚙️ Asansör Tipi", tip_listesi, index=tip_listesi.index(mevcut_tip) if mevcut_tip in tip_listesi else 0)
                        
                        etiket_listesi = ["Yeşil", "Mavi", "Sarı", "Kırmızı"]
                        mevcut_etiket = asansor_info.get('etiket', 'Yeşil')
                        yeni_etiket = st.selectbox("🏷️ Mevcut Etiket Rengi", etiket_listesi, index=etiket_listesi.index(mevcut_etiket) if mevcut_etiket in etiket_listesi else 0)
                    
                    if st.button("✅ Değişiklikleri Kaydet", type="primary", use_container_width=True):
                        if yeni_etiket_no or yeni_kimlik_32:
                            # Yeni bina ID'sini bul
                            new_building_id = bina_map.get(yeni_bina)
                            
                            # Güncellenmiş verileri kaydet
                            supabase.table("elevators").update({
                                "building_id": new_building_id,
                                "blok": yeni_blok,
                                "kimlik": yeni_kimlik_32,
                                "etiket_no": yeni_etiket_no,
                                "tip": yeni_tip,
                                "etiket": yeni_etiket
                            }).eq("id", asansor_info['id']).execute()
                            
                            st.success(f"✅ Asansör başarıyla güncellendi!")
                            clear_all_caches()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.warning("⚠️ En az bir kimlik numarası (32 haneli veya etiket no) gereklidir!")
                else:
                    st.info("📋 Sistemde asansör bulunmuyor.")
            except Exception as e:
                st.error(f"Hata: {e}")
        
        elif islem_turu == "Bina Sil":
            st.warning("⚠️ **DİKKAT:** Bir binayı sildiğinizde, o binaya ait TÜM asansörler de silinir!")
            
            try:
                buildings_result = supabase.table("buildings").select("*").execute()
                binalar = buildings_result.data
                
                if binalar:
                    bina_isimleri = [b['bina_adi'] for b in binalar]
                    silinecek_bina = st.selectbox("🏢 Silinecek Binayı Seçin", bina_isimleri, key="sil_bina_sec")
                    
                    # ONAY CHECKBOX'I
                    onay = st.checkbox(f"⚠️ **{silinecek_bina}** binasını ve tüm asansörlerini kalıcı olarak silmek istediğimi onaylıyorum", key="bina_sil_onay")
                    
                    if st.button("🗑️ BİNAYI SİL", type="primary", use_container_width=True, disabled=not onay):
                        if onay:
                            # Binayı bul
                            bina_id = next(b['id'] for b in binalar if b['bina_adi'] == silinecek_bina)
                            
                            # Asansör sayısını kontrol et
                            elevator_count_result = supabase.table("elevators").select("id", count="exact").eq("building_id", bina_id).execute()
                            silinen_asansor = elevator_count_result.count if hasattr(elevator_count_result, 'count') else 0
                            
                            # Binayı sil (CASCADE ile asansörler otomatik silinir)
                            supabase.table("buildings").delete().eq("id", bina_id).execute()
                            
                            st.success(f"✅ **{silinecek_bina}** binası ve {silinen_asansor} asansör silindi!")
                            clear_all_caches()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("❌ Silme işlemi için onay gereklidir!")
                else:
                    st.info("📋 Sistemde bina bulunmuyor.")
            except Exception as e:
                st.error(f"Hata: {e}")
        
        else:  # Asansör Silme
            st.info("ℹ️ Asansör seçip silebilirsiniz. Bakım kayıtları korunur.")
            
            try:
                elevators_result = supabase.table("elevators").select("*").execute()
                asansorler = enrich_elevators(elevators_result.data)
                
                if asansorler:
                    # Asansörleri dropdown'da göster
                    asansor_display = [f"{a.get('bina', '-')} - {a.get('blok', '-')} - {a.get('kimlik', '-')}" for a in asansorler]
                    secilen = st.selectbox("🛗 Silinecek Asansörü Seçin", asansor_display, key="sil_asansor_sec")
                    
                    # Seçilen asansörün ID'sini bul
                    secilen_index = asansor_display.index(secilen)
                    asansor_id = asansorler[secilen_index]['id']
                    
                    # ONAY CHECKBOX'I
                    onay = st.checkbox(f"⚠️ **{secilen}** asansörünü kalıcı olarak silmek istediğimi onaylıyorum", key="asansor_sil_onay")
                    
                    if st.button("🗑️ ASANSÖRÜ SİL", type="primary", use_container_width=True, disabled=not onay):
                        if onay:
                            supabase.table("elevators").delete().eq("id", asansor_id).execute()
                            st.success(f"✅ **{secilen}** asansörü silindi!")
                            clear_all_caches()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("❌ Silme işlemi için onay gereklidir!")
                else:
                    st.info("📋 Sistemde asansör bulunmuyor.")
            except Exception as e:
                st.error(f"Hata: {e}")

# === FİRMA YÖNETİMİ (YENİ) ===
elif selected == "Firma Yönetimi":
    st.title("🤝 Bakım Firması Yönetimi")
    
    tab1, tab2, tab3 = st.tabs(["➕ Firma Ekle", "✏️ Firma Düzenle", "📋 Firma Listesi & Sil"])
    
    with tab1:
        st.markdown("### Yeni Firma Kaydet")
        with st.form("firma_ekle_form"):
            col1, col2 = st.columns(2)
            f_ad = col1.text_input("🏢 Firma Adı", placeholder="Örn: Otis Asansör")
            f_yetkili = col2.text_input("👤 Yetkili Adı Soyadı")
            f_belge = col1.text_input("📜 Yetki Belge Numarası", placeholder="Örn: YB-2024-12345")
            f_tel = col2.text_input("📞 İletişim Telefonu", placeholder="+90 555 123 4567")
            f_sozlesme = col1.date_input("📅 Sözleşme Bitiş Tarihi")
            
            if st.form_submit_button("✅ Firmayı Kaydet", use_container_width=True):
                if f_ad:
                    try:
                        supabase.table("companies").insert({
                            "sirket_adi": f_ad,
                            "telefon": f_tel,
                            "yetkili": f_yetkili
                        }).execute()
                        st.success(f"✅ **{f_ad}** başarıyla eklendi!")
                        clear_all_caches()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
                else:
                    st.error("❌ Firma adı boş olamaz!")
    
    with tab2:
        st.markdown("### Firma Düzenle")
        try:
            companies_result = supabase.table("companies").select("*").execute()
            firmalar = companies_result.data
            
            if firmalar:
                firma_isimleri = [f['sirket_adi'] for f in firmalar]
                secilen_firma_ad = st.selectbox("✏️ Düzenlenecek Firmayı Seçin", firma_isimleri, key="duzenle_firma_sec")
                
                # Seçilen firmayı bul
                secilen_firma = next(f for f in firmalar if f['ad'] == secilen_firma_ad)
                
                st.markdown("---")
                st.markdown("### Firma Bilgilerini Güncelle")
                
                with st.form("firma_duzenle_form"):
                    col1, col2 = st.columns(2)
                    
                    yeni_ad = col1.text_input("🏢 Firma Adı", value=secilen_firma.get('ad', ''))
                    yeni_yetkili = col2.text_input("👤 Yetkili Adı Soyadı", value=secilen_firma.get('yetkili', ''))
                    yeni_belge = col1.text_input("📜 Yetki Belge Numarası", value=secilen_firma.get('belge_no', ''))
                    yeni_tel = col2.text_input("📞 İletişim Telefonu", value=secilen_firma.get('tel', ''))
                    
                    # Sözleşme tarihi parse et
                    try:
                        from datetime import datetime
                        mevcut_tarih_str = secilen_firma.get('sozlesme_bitis', '')
                        if mevcut_tarih_str:
                            mevcut_tarih = datetime.strptime(mevcut_tarih_str, '%Y-%m-%d').date()
                        else:
                            mevcut_tarih = datetime.today().date()
                    except:
                        mevcut_tarih = datetime.today().date()
                    
                    yeni_sozlesme = col1.date_input("📅 Sözleşme Bitiş Tarihi", value=mevcut_tarih)
                    
                    if st.form_submit_button("✅ Değişiklikleri Kaydet", use_container_width=True):
                        if yeni_ad:
                            # Firmayı güncelle
                            supabase.table("companies").update({
                                "sirket_adi": yeni_ad,
                                "yetkili_kisi": yeni_yetkili,
                                "belge_no": yeni_belge,
                                "telefon": yeni_tel,
                                "sozlesme_bitis_tarihi": str(yeni_sozlesme)
                            }).eq("id", secilen_firma['id']).execute()
                            
                            st.success(f"✅ **{yeni_ad}** başarıyla güncellendi!")
                            clear_all_caches()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("❌ Firma adı boş olamaz!")
            else:
                st.info("📋 Henüz firma eklenmemiş. 'Firma Ekle' sekmesinden yeni firma ekleyebilirsiniz.")
        except Exception as e:
            st.error(f"Hata: {e}")
    
    with tab3:
        st.markdown("### Kayıtlı Firmalar")
        try:
            firmalar_result = supabase.table("companies").select("*").execute()
            firmalar = firmalar_result.data
            if firmalar:
                df_firma = pd.DataFrame(firmalar)
                
                # Kullanıcıya anlamlı sütunları göster (UUID'siz)
                col_mapping = {
                    'sirket_adi': '🏢 Firma Adı',
                    'yetkili_kisi': '👤 Yetkili Kişi',
                    'belge_no': '📜 Belge No',
                    'telefon': '📞 Telefon',
                    'sozlesme_bitis_tarihi': '📅 Sözleşme Bitiş'
                }
                
                display_cols = [col for col in col_mapping.keys() if col in df_firma.columns]
                
                if display_cols:
                    df_display = df_firma[display_cols].copy()
                    df_display.columns = [col_mapping[col] for col in display_cols]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_firma, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### 🗑️ Firma Sil")
                silinecek = st.selectbox("Silinecek Firmayı Seçin", [f['sirket_adi'] for f in firmalar], key="sil_firma_sec")
                if st.button("🗑️ Firmayı Sil", type="primary", use_container_width=True):
                    for f in firmalar:
                        if f['sirket_adi'] == silinecek:
                            try:
                                supabase.table("companies").delete().eq("id", f['id']).execute()
                                st.success(f"✅ **{silinecek}** silindi.")
                                clear_all_caches()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Hata: {e}")
            else:
                st.info("📋 Henüz firma eklenmemiş.")
        except Exception as e:
            st.error(f"Hata: {e}")

# === BAKIM İŞLEMLERİ (GÜNCELLENDİ) ===
elif selected == "Bakım İşlemleri":
    st.title("🛠️ Bakım ve Arıza Yönetimi")
    
    # İKİ SEKME: EKLEME VE SİLME
    tab_ekle, tab_sil = st.tabs(["➕ Yeni Bakım Gir", "🗑️ Geçmiş Bakımları Sil"])
    
    # Binaları çek
    try:
        buildings_result = supabase.table("buildings").select("bina_adi").execute()
        bina_listesi = [b['bina_adi'] for b in buildings_result.data]
    except:
        bina_listesi = []

    if not bina_listesi:
        st.warning("⚠️ Önce sisteme bina eklemelisiniz.")
    else:
        # --- SEKME 1: YENİ BAKIM EKLE ---
        with tab_ekle:
            secilen_bina_bakim = st.selectbox("İşlem Yapılacak Bina", bina_listesi, key="bina_ekle")
            
            # 2. O Binadaki Asansörleri Getir - BLOK BİLGİSİYLE BİRLİKTE
            # Önce building UUID'sini bul
            building_result = supabase.table("buildings").select("id").eq("bina_adi", secilen_bina_bakim).execute()
            if not building_result.data:
                st.error("Bina bulunamadı!")
                asansor_map = {}
            else:
                building_id = building_result.data[0]['id']
                asansorler_result = supabase.table("elevators").select("*").eq("building_id", building_id).execute()
                asansor_list_raw = asansorler_result.data  # Ham listeyi sakla
                
                # Asansörleri Blok ve Kimlik ile birlikte göster
                asansor_map = {}
                for a in asansorler_result.data:
                    kimlik = a.get('kimlik')
                    blok = a.get('blok', '-')
                    etiket_no = a.get('etiket_no', '')
                    if etiket_no:
                        etiket_text = f"{blok} / {kimlik} / Etiket: {etiket_no}"
                    else:
                        etiket_text = f"{blok} / {kimlik}"
                    asansor_map[etiket_text] = a['id']  # UUID kullan
            
            if not asansor_map:
                st.info(f"{secilen_bina_bakim} için kayıtlı asansör bulunamadı.")
            else:
                secilen_asansor_label = st.selectbox("Asansör Seçiniz (Blok / Etiket No)", list(asansor_map.keys()))
                secilen_asansor = asansor_map[secilen_asansor_label]
                
                st.markdown("---")
                
                # 3. Form Alanları - BASİT
                col1, col2 = st.columns(2)
                with col1:
                    islem_turu = st.selectbox("İşlem Türü", ["Periyodik Bakım", "Arıza Giderme", "Parça Değişimi"])
                    tarih = st.date_input("İşlem Tarihi")
                    bakim_servis_no = st.text_input("🔢 Bakım Servis No", placeholder="Örn: BS-2026-001")
                with col2:
                    teknisyen = st.text_input("👤 Bina Asansör Sorumlusu", placeholder="Bina asansör sorumlusu adı")
                    durum = st.selectbox("Durum", ["Tamamlandı", "Devam Ediyor", "Beklemede"])

                degisen_parcalar = ""
                degismesi_gereken_parcalar = ""
                # Parça Değişimi ise sadece değişen parça alanı
                if islem_turu == "Parça Değişimi":
                    degisen_parcalar = st.text_area(
                        "Değişim Yapılan Parçalar (virgülle ayırın, opsiyonel)",
                        placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
                    )
                    st.markdown("---")
                    fiyat = st.number_input("💰 Parça Fiyatı (TL)", min_value=0.0, step=10.0, format="%.2f", help="İsteğe bağlı - Parça maliyetini girebilirsiniz")
                elif islem_turu == "Periyodik Bakım":
                    # Kutucuk ile açılır alanlar
                    show_degismesi_gereken = st.checkbox("Değişmesi Gereken Parçalar Var", value=False)
                    if show_degismesi_gereken:
                        degismesi_gereken_parcalar = st.text_area(
                            "Değişmesi Gereken Parçalar (virgülle ayırın, opsiyonel)",
                            placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
                        )
                    show_degisen = st.checkbox("Değişim Yapılan Parçalar Var", value=False)
                    if show_degisen:
                        degisen_parcalar = st.text_area(
                            "Değişim Yapılan Parçalar (virgülle ayırın, opsiyonel)",
                            placeholder="Ör: Halat, Kapı Kontağı, Buton Paneli"
                        )
                    fiyat = None
                else:
                    fiyat = None

                aciklama = st.text_area(
                    "Yapılan İşlem Detayı / Açıklama", 
                    height=200,
                    placeholder="Örnek:\n06.12.2025 - Kuyu aydınlatması yanmıyor, yağdanlıklar işlevini kaybetmiş, anakart role arızalı\n08.12.2025 - Regülatör bobinine enerji vermiyordu, kart söküldü tamire gidilecek"
                )
                
                # ETİKET DEĞİŞTİRME - OPSİYONEL
                st.markdown("---")
                etiket_degistir = st.checkbox("🏷️ Asansörün etiket durumunu değiştirmek istiyorum")
                
                yeni_etiket = None
                if etiket_degistir:
                    st.warning("⚠️ Etiket durumunu değiştirmek üzeresiniz!")
                    yeni_etiket = st.selectbox("Yeni Etiket Durumu", ["Yeşil", "Mavi", "Sarı", "Kırmızı"])

                # 4. Kaydet Butonu
                if st.button("💾 İşlemi Kaydet ve Tamamla", type="primary", use_container_width=True):
                    if aciklama:
                        try:
                            # Fiyat bilgisini notlara ekle
                            notlar_son = aciklama
                            if degismesi_gereken_parcalar:
                                notlar_son += f"\n\n🟡 Değişmesi Gereken Parçalar: {degismesi_gereken_parcalar}"
                            if degisen_parcalar:
                                notlar_son += f"\n\n🔧 Değişim Yapılan Parçalar: {degisen_parcalar}"
                            if fiyat and fiyat > 0:
                                notlar_son += f"\n\n💰 Maliyet: {fiyat:.2f} TL"
                            
                            # A) Geçmişe (Loglara) Kaydet
                            maintenance_data = {
                                "elevator_id": secilen_asansor,
                                "bakim_tarihi": str(tarih),
                                "yapilan_islem": islem_turu,
                                "teknisyen": teknisyen,
                                "sonraki_bakim": None,
                                "notlar": notlar_son,
                                "durum": durum,
                                "bakim_servis_no": bakim_servis_no if bakim_servis_no else None
                            }
                            
                            supabase.table("maintenance_logs").insert(maintenance_data).execute()
                            
                            # Aktivite logu ekle
                            elevator_info = next((e for e in enrich_elevators(asansor_list_raw) if e['id'] == secilen_asansor), None)
                            if elevator_info:
                                log_activity(
                                    st.session_state.user['id'],
                                    st.session_state.user['username'],
                                    'bakım_eklendi',
                                    elevator_info.get('bina', '-'),
                                    f"{elevator_info.get('blok', '-')} - {elevator_info.get('kimlik', '-')}",
                                    f"{islem_turu} - {durum}"
                                )
                            
                            # Cache'i temizle - yeni veriyi göster
                            clear_all_caches()
                            
                            # B) Etiket güncelle - SADECE İSTENİRSE
                            if etiket_degistir and yeni_etiket:
                                supabase.table("elevators").update({
                                    "notlar": f"Etiket: {yeni_etiket}"
                                }).eq("id", secilen_asansor).execute()
                                st.success(f"✅ Bakım kaydedildi ve etiket '{yeni_etiket}' olarak güncellendi!")
                            else:
                                st.success("✅ Bakım kaydı başarıyla işlendi!")
                            
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Hata oluştu: {e}")
                    else:
                        st.warning("Lütfen yapılan işlemi açıklayınız.")

        # --- SEKME 2: BAKIM SİL ---
        with tab_sil:
            st.info("🗑️ Burada hatalı girilen bakım kayıtlarını silebilirsiniz.")
            
            sil_bina = st.selectbox("Bina Seçiniz", bina_listesi, key="bina_sil")
            
            # O binadaki tüm logları çekelim - SADECE LİSTELE, SIRALAMA YOK
            try:
                # Bina adından building_id bul
                building_result = supabase.table("buildings").select("id").eq("bina_adi", sil_bina).execute()
                if not building_result.data:
                    st.warning("Bu binaya ait bakım kaydı bulunamadı.")
                else:
                    building_id = building_result.data[0]['id']
                    
                    # Bu binaya ait tüm asansörleri bul
                    elevators_result = supabase.table("elevators").select("id, kimlik").eq("building_id", building_id).execute()
                    elevator_ids = [e['id'] for e in elevators_result.data]
                    
                    if not elevator_ids:
                        st.warning("Bu binada asansör bulunamadı.")
                    else:
                        # Tüm elevator_ids için maintenance_logs çek
                        log_list = []
                        log_ids = []
                        
                        for elev_id in elevator_ids:
                            logs_result = supabase.table("maintenance_logs").select("*").eq("elevator_id", elev_id).execute()
                            
                            for d in logs_result.data:
                                tarih = d.get('bakim_tarihi', 'Tarihsiz')
                                
                                # Asansör kimliğini bul
                                asansor_kimlik = next((e['kimlik'] for e in elevators_result.data if e['id'] == d['elevator_id']), 'Bilinmiyor')
                                
                                islem = d.get('yapilan_islem', 'İşlem')
                                notlar = d.get('notlar', '')[:50]  # İlk 50 karakter
                                
                                ozet = f"{tarih} | {asansor_kimlik} | {islem} | {notlar}"
                                log_list.append(ozet)
                                log_ids.append(d['id'])
                        
                        if log_list:
                            secilen_log_str = st.selectbox("Silinecek Kaydı Seçiniz", log_list, key="sil_bakim_kaydi_sec")
                            
                            # Seçilenin ID'sini bul
                            index = log_list.index(secilen_log_str)
                            silinecek_id = log_ids[index]
                            
                            st.warning(f"⚠️ Seçili Kayıt: **{secilen_log_str}**")
                            
                            if st.button("🗑️ BU KAYDI SİL", type="primary"):
                                supabase.table("maintenance_logs").delete().eq("id", silinecek_id).execute()
                                clear_all_caches()
                                st.success("✅ Kayıt veritabanından silindi.")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Bu binaya ait geçmiş bakım kaydı bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")

# === MESAJLAŞMA ===
elif selected == "💬 Mesajlar":
    st.title("💬 Mesajlar")
    
    tab1, tab2, tab3 = st.tabs(["📥 Gelen Kutusu", "📤 Giden Kutusu", "✉️ Yeni Mesaj"])
    
    with tab1:
        st.markdown("### 📥 Gelen Mesajlar")
        
        try:
            # Gelen mesajları getir
            messages_result = supabase.table('messages').select('*').eq('receiver_id', st.session_state.user['id']).order('created_at', desc=True).execute()
            
            if messages_result.data:
                for msg in messages_result.data:
                    # Gönderen bilgisini al
                    sender_result = supabase.table('users').select('username').eq('id', msg['sender_id']).execute()
                    sender_name = sender_result.data[0]['username'] if sender_result.data else 'Bilinmeyen'
                    
                    # Asansör bilgilerini hazırla
                    elevator_info_html = ""
                    if msg.get('elevator_ids'):
                        elevator_names = []
                        for elev_id in msg['elevator_ids']:
                            elev_result = supabase.table('elevators').select('kimlik, blok').eq('id', elev_id).execute()
                            if elev_result.data:
                                elev = elev_result.data[0]
                                elevator_names.append(f"{elev.get('blok', '-')} - {elev.get('kimlik', '-')}")
                        
                        if elevator_names:
                            elevator_info_html = f'<div style="color: #4A5568; margin-bottom: 12px;"><strong>🛗 İlgili Asansörler:</strong> {", ".join(elevator_names)}</div>'
                    
                    # Mesaj içeriğini hazırla
                    message_content = msg['message'].replace('\n', '<br>')
                    
                    # Tüm kartı tek HTML string olarak oluştur (giden kutusu gibi)
                    # Okunmamış mesajlar için farklı stil
                    border_color = "#E30A17" if not msg['is_read'] else "#48BB78"
                    status_badge = "🔴 Yeni" if not msg['is_read'] else "✅ Okundu"
                    status_bg = '#FED7D7' if not msg['is_read'] else '#C6F6D5'
                    status_color = '#C53030' if not msg['is_read'] else '#22543D'

                    card_html = f"""
<div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {border_color}; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h4 style="margin: 0; color: #1A202C;">📧 {msg.get('subject', 'Konu yok')}</h4>
<span style="color: #718096; font-size: 14px;">{format_tarih(msg['created_at'])}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div style="color: #4A5568;"><strong>Gönderen:</strong> {sender_name}</div>
<span style="background: {status_bg}; color: {status_color}; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;">{status_badge}</span>
</div>
{elevator_info_html}
<div style="background: #F7FAFC; padding: 12px; border-radius: 8px; color: #2D3748; line-height: 1.6; margin-bottom: 12px;">
{message_content}
</div>
</div>
"""
                    
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Butonlar: Okundu işaretle ve Sil
                    col1, col2 = st.columns(2)
                    with col1:
                        if not msg['is_read']:
                            if st.button("✅ Okundu Olarak İşaretle", key=f"mark_read_{msg['id']}", use_container_width=True):
                                supabase.table('messages').update({'is_read': True}).eq('id', msg['id']).execute()
                                st.success("Mesaj okundu olarak işaretlendi!")
                                time.sleep(0.5)
                                st.rerun()
                    with col2:
                        if st.button("🗑️ Sil", key=f"delete_inbox_admin_{msg['id']}", use_container_width=True, type="secondary"):
                            if st.session_state.get(f"confirm_delete_inbox_admin_{msg['id']}", False):
                                supabase.table('messages').delete().eq('id', msg['id']).execute()
                                st.success("Mesaj silindi!")
                                if f"confirm_delete_inbox_admin_{msg['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_inbox_admin_{msg['id']}"]
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_inbox_admin_{msg['id']}"] = True
                                st.warning("⚠️ Tekrar 'Sil' butonuna tıklayarak onaylayın!")
                                st.rerun()
            else:
                st.info("📭 Gelen mesaj bulunmuyor.")
        except Exception as e:
            st.error("Mesajlar yüklenirken bir bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
            print(f"Admin gelen mesajlar hatası: {e}")
    
    with tab2:
        st.markdown("### 📤 Gönderilen Mesajlar")
        
        try:
            # Gönderilen mesajları getir
            sent_messages = supabase.table('messages').select('*').eq('sender_id', st.session_state.user['id']).order('created_at', desc=True).execute()
            
            if sent_messages.data:
                for msg in sent_messages.data:
                    # Alıcı bilgisini al
                    receiver_result = supabase.table('users').select('username').eq('id', msg['receiver_id']).execute()
                    receiver_name = receiver_result.data[0]['username'] if receiver_result.data else 'Bilinmeyen'
                    
                    # Mesaj içeriğini hazırla
                    message_content = msg['message'].replace('\n', '<br>')
                    
                    # Tüm kartı tek HTML string olarak oluştur
                    card_html = f"""
<div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #E30A17; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<h4 style="margin: 0; color: #1A202C;">📧 {msg.get('subject', 'Konu yok')}</h4>
<span style="color: #718096; font-size: 14px;">{format_tarih(msg['created_at'])}</span>
</div>
<div style="color: #4A5568; margin-bottom: 12px;">
<strong>Alıcı:</strong> {receiver_name}
</div>
<div style="background: #F7FAFC; padding: 12px; border-radius: 8px; color: #2D3748; line-height: 1.6; margin-bottom: 12px;">
{message_content}
</div>
</div>
"""
                    
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Silme butonu
                    if st.button("🗑️ Sil", key=f"delete_outbox_admin_{msg['id']}", use_container_width=True, type="secondary"):
                        if st.session_state.get(f"confirm_delete_outbox_admin_{msg['id']}", False):
                            supabase.table('messages').delete().eq('id', msg['id']).execute()
                            st.success("Mesaj silindi!")
                            if f"confirm_delete_outbox_admin_{msg['id']}" in st.session_state:
                                del st.session_state[f"confirm_delete_outbox_admin_{msg['id']}"]
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_outbox_admin_{msg['id']}"] = True
                            st.warning("⚠️ Tekrar 'Sil' butonuna tıklayarak onaylayın!")
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("📭 Gönderilen mesaj bulunmuyor.")
        except Exception as e:
            st.error("Gönderilen mesajlar yüklenirken bir bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
            print(f"Admin giden mesajlar hatası: {e}")
    
    with tab3:
        st.markdown("### ✉️ Yeni Mesaj Gönder")
        
        with st.form("new_message_form"):
            try:
                # Admin ise bina yetkilisi seçebilir, bina yetkilisi ise sadece admin'e gönderir
                if st.session_state.user_rol == 'admin':
                    # Tüm bina yetkililerini getir
                    users_result = supabase.table('users').select('id, username').eq('rol', 'bina_yetkilisi').eq('aktif', True).execute()
                    
                    if users_result.data:
                        user_options = {u['username']: u['id'] for u in users_result.data}
                        selected_user_name = st.selectbox("👤 Alıcı", list(user_options.keys()), key="msg_receiver")
                        receiver_id = user_options[selected_user_name]
                    else:
                        st.warning("⚠️ Aktif bina yetkilisi bulunamadı")
                        receiver_id = None
                else:
                    # Bina yetkilisi admin'e gönderir
                    admin_result = supabase.table('users').select('id').eq('rol', 'admin').eq('aktif', True).execute()
                    if admin_result.data:
                        receiver_id = admin_result.data[0]['id']
                        st.info("📧 Mesaj yöneticiye gönderilecek")
                    else:
                        st.error("⚠️ Admin kullanıcı bulunamadı")
                        receiver_id = None
                
                subject = st.text_input("📌 Konu", key="msg_subject")
                message = st.text_area("✍️ Mesaj", height=200, key="msg_content")
                
                submit = st.form_submit_button("📨 Gönder", use_container_width=True)
            except Exception as e:
                st.error("Kullanıcı listesi yüklenirken bağlantı hatası oluştu. Lütfen sayfayı yenileyin.")
                print(f"Yeni mesaj formu hatası: {e}")
                receiver_id = None
                subject = None
                message = None
                submit = False
            
            if submit and receiver_id:
                if subject and message:
                    try:
                        supabase.table('messages').insert({
                            'sender_id': st.session_state.user['id'],
                            'receiver_id': receiver_id,
                            'subject': subject,
                            'message': message,
                            'is_read': False
                        }).execute()
                        
                        st.success("✅ Mesaj başarıyla gönderildi!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")
                else:
                    st.warning("⚠️ Lütfen konu ve mesaj alanlarını doldurun")


elif selected == "Raporlar":
    st.title("📊 Maliyet ve Analiz Raporları")
    
    # SON 10 BAKIM HAREKETİ - SİLME BUTONU İLE
    st.markdown("### 🔥 Son 10 Bakım Hareketi (Silme Özellikli)")
    
    try:
        # Son 10 bakım kaydını çek (tarihe göre sıralı)
        son_bakimlar_result = supabase.table("maintenance_logs").select("*").order("bakim_tarihi", desc=True).limit(10).execute()
        son_bakimlar = son_bakimlar_result.data
        
        if son_bakimlar:
            for log_data in son_bakimlar:
                log_id = log_data['id']
                
                # Asansör bilgisini getir
                elevator_info = ""
                if log_data.get('elevator_id'):
                    elev_result = supabase.table("elevators").select("*").eq("id", log_data['elevator_id']).execute()
                    if elev_result.data:
                        elev_enriched = enrich_elevators(elev_result.data)
                        if elev_enriched:
                            e = elev_enriched[0]
                            bina = e.get('bina', '-')
                            blok = e.get('blok', '-')
                            asansor = e.get('kimlik', '-')
                            elevator_info = f"🏢 {bina} | 🏛️ {blok} | 🛗 {asansor}"
                
                # Her kayıt için bir kutu oluştur
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        tarih_str = log_data.get('bakim_tarihi', 'Tarihsiz')
                        
                        teknisyen = log_data.get('teknisyen', '-')
                        yapilan_islem = log_data.get('yapilan_islem', '-')
                        durum = log_data.get('durum', '-')
                        notlar = log_data.get('notlar', '-')
                        parca_adi = log_data.get('parca_adi', '')
                        
                        # Parça bilgisi varsa göster
                        parca_info = f" | 🔧 Parça: {parca_adi}" if parca_adi else ""
                        
                        st.markdown(f"""
                        **📅 {tarih_str}** | {elevator_info}  
                        **İşlem:** {yapilan_islem} | **Teknisyen:** {teknisyen} | **Durum:** {durum}{parca_info}  
                        **Notlar:** {notlar}
                        """)
                    
                    with col2:
                        if st.button("🗑️ Sil", key=f"sil_{log_id}", type="secondary"):
                            supabase.table("maintenance_logs").delete().eq("id", log_id).execute()
                            st.success("✅ Silindi!")
                            time.sleep(0.5)
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("Henüz bakım kaydı yok.")
    except Exception as e:
        st.error(f"Hata: {e}")
    
    st.markdown("---")
    st.markdown("### 📅 Tarih Aralığı ile Detaylı Rapor")
    
    st.markdown("### 📅 Tarih Aralığı Seçin")
    col1, col2 = st.columns(2)
    with col1:
        baslangic = st.date_input("Başlangıç Tarihi", value=datetime.now() - timedelta(days=30))
    with col2:
        bitis = st.date_input("Bitiş Tarihi", value=datetime.now())
    
    if st.button("🔍 Rapor Oluştur"):
        try:
            # Tüm bakım kayıtlarını çek
            bakim_logs_result = supabase.table("maintenance_logs").select("*").execute()
            bakim_list = bakim_logs_result.data
            
            if len(bakim_list) == 0:
                st.warning("⚠️ Seçilen tarih aralığında bakım kaydı bulunamadı.")
            else:
                # Her bakım için asansör bilgilerini zenginleştir
                for log in bakim_list:
                    if log.get('elevator_id'):
                        elev_result = supabase.table("elevators").select("*").eq("id", log['elevator_id']).execute()
                        if elev_result.data:
                            enriched = enrich_elevators(elev_result.data)
                            if enriched:
                                log['bina'] = enriched[0].get('bina', '-')
                                log['blok'] = enriched[0].get('blok', '-')
                                log['asansor_kimlik'] = enriched[0].get('kimlik', '-')
                
                df_bakim = pd.DataFrame(bakim_list)
                
                # Tarih filtreleme
                if 'bakim_tarihi' in df_bakim.columns:
                    df_bakim['bakim_tarihi'] = pd.to_datetime(df_bakim['bakim_tarihi'])
                    df_filtered = df_bakim[
                        (df_bakim['bakim_tarihi'] >= pd.to_datetime(baslangic)) & 
                        (df_bakim['bakim_tarihi'] <= pd.to_datetime(bitis))
                    ]
                else:
                    df_filtered = df_bakim
                
                if len(df_filtered) == 0:
                    st.warning("⚠️ Seçilen tarih aralığında bakım kaydı bulunamadı.")
                else:
                    st.success(f"✅ {len(df_filtered)} adet bakım kaydı bulundu!")
                    
                    # İstatistikler
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🔧 İşlem Sayısı", len(df_filtered))
                    with col2:
                        teknisyen_sayisi = df_filtered['teknisyen'].nunique() if 'teknisyen' in df_filtered.columns else 0
                        st.metric("👷 Teknisyen Sayısı", teknisyen_sayisi)
                    with col3:
                        bina_sayisi = df_filtered['bina'].nunique() if 'bina' in df_filtered.columns else 0
                        st.metric("🏢 Farklı Bina", bina_sayisi)
                    
                    st.markdown("---")
                    
                    # TEKNİSYEN BAZINDA DAĞILIM
                    st.subheader("👷 Teknisyen Bazında İşlem Sayısı")
                    if 'teknisyen' in df_filtered.columns:
                        teknisyen_dagilim = df_filtered.groupby('teknisyen').size().reset_index(name='islem_sayisi')
                        teknisyen_dagilim = teknisyen_dagilim.sort_values('islem_sayisi', ascending=False)
                        
                        fig_teknisyen = px.bar(
                            teknisyen_dagilim,
                            x='teknisyen',
                            y='islem_sayisi',
                            title='Teknisyen Bazlı İşlem Dağılımı',
                            labels={'islem_sayisi': 'İşlem Sayısı', 'teknisyen': 'Teknisyen'},
                            color='islem_sayisi',
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig_teknisyen, use_container_width=True)
                        
                        st.dataframe(teknisyen_dagilim, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    
                    # İŞLEM TÜRÜ BAZINDA DAĞILIM
                    st.subheader("⚙️ İşlem Türü Bazında Dağılım")
                    if 'yapilan_islem' in df_filtered.columns:
                        islem_dagilim = df_filtered.groupby('yapilan_islem').size().reset_index(name='adet')
                        
                        fig_islem = px.pie(
                            islem_dagilim,
                            values='adet',
                            names='yapilan_islem',
                            title='İşlem Türlerine Göre Dağılım',
                            hole=0.4
                        )
                        st.plotly_chart(fig_islem, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # DETAYLI TABLO
                    st.subheader("📋 Detaylı Kayıt Listesi")
                    display_columns = []
                    col_names = {}
                    
                    if 'bakim_tarihi' in df_filtered.columns:
                        display_columns.append('bakim_tarihi')
                        col_names['bakim_tarihi'] = '📅 Tarih'
                    if 'bina' in df_filtered.columns:
                        display_columns.append('bina')
                        col_names['bina'] = '🏢 Bina'
                    if 'blok' in df_filtered.columns:
                        display_columns.append('blok')
                        col_names['blok'] = '🏛️ Blok'
                    if 'asansor_kimlik' in df_filtered.columns:
                        display_columns.append('asansor_kimlik')
                        col_names['asansor_kimlik'] = '🛗 Asansör'
                    if 'yapilan_islem' in df_filtered.columns:
                        display_columns.append('yapilan_islem')
                        col_names['yapilan_islem'] = '⚙️ İşlem'
                    if 'teknisyen' in df_filtered.columns:
                        display_columns.append('teknisyen')
                        col_names['teknisyen'] = '👷 Teknisyen'
                    if 'durum' in df_filtered.columns:
                        display_columns.append('durum')
                        col_names['durum'] = '📊 Durum'
                    if 'parca_adi' in df_filtered.columns:
                        display_columns.append('parca_adi')
                        col_names['parca_adi'] = '🔧 Parça'
                    if 'degisim_tarihi' in df_filtered.columns:
                        display_columns.append('degisim_tarihi')
                        col_names['degisim_tarihi'] = '📅 Değişim Tarihi'
                    if 'notlar' in df_filtered.columns:
                        display_columns.append('notlar')
                        col_names['notlar'] = '📝 Notlar'
                    
                    if display_columns:
                        df_display = df_filtered[display_columns].copy()
                        df_display = df_display.rename(columns=col_names)
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            hide_index=True
                        )
                    
        except Exception as e:
            st.error(f"Rapor oluştururken hata: {e}")

# === VERİ YÜKLEME (EXCEL) ===
elif selected == "Veri Yükleme":
    st.title("📥 Excel'den Toplu Veri Aktarımı")
    
    st.info("📌 **BLOK SİSTEMİ EKLENDİ!** Artık Abdurrahman Gazi A Blok ile C Blok birbirine karışmayacak!")
    
    st.markdown("""
    ### 📋 Excel Formatı (Tam Bu Şekilde Olmalı):
    
    | Bina Adi | Blok | Kimlik No | Tip | Etiket |
    |---------|------|-----------|-------|-----|--------|
    | Abdurrahman Gazi Yurdu | A Blok | TR-25-001 | Otis | İnsan | Yeşil |
    | Abdurrahman Gazi Yurdu | B Blok | TR-25-002 | Mitsubishi | İnsan | Mavi |
    | Rabia Hatun Yurdu | A Blok | TR-25-010 | Schindler | Yük | Yeşil |
    
    ⚠️ **DİKKAT:** Sütun başlıkları aynen bu şekilde olmalı (büyük-küçük harf önemli)
    """)
    
    uploaded_file = st.file_uploader("Excel Dosyasını Sürükleyin", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("📊 Önizleme:")
            st.dataframe(df.head())
            
            if st.button("✅ Verileri Veritabanına Aktar"):
                basarili = 0
                hatali = 0
                
                # İlerleme çubuğu
                bar = st.progress(0)
                total_rows = len(df)
                
                # Bina adlarını UUID'ye map et
                buildings_result = supabase.table("buildings").select("id, bina_adi").execute()
                bina_map = {b['bina_adi']: b['id'] for b in buildings_result.data}
                
                for index, row in df.iterrows():
                    try:
                        bina_adi = row['Bina Adi']
                        building_id = bina_map.get(bina_adi)
                        
                        if not building_id:
                            st.warning(f"Satır {index+1}: {bina_adi} binası bulunamadı, önce bina eklemeniz gerekiyor!")
                            hatali += 1
                            continue
                        
                        # Satır satır oku ve kaydet - BLOK ALANI EKLENDİ
                        supabase.table("elevators").insert({
                            "building_id": building_id,
                            "blok": row.get('Blok', '-'),  # BLOK EKLENDİ
                            "kimlik": str(row['Kimlik No']),

                            "tip": row.get('Tip', 'İnsan'),
                            "etiket": row.get('Etiket', 'Yeşil')
                        }).execute()
                        
                        basarili += 1
                    except Exception as e:
                        st.warning(f"Satır {index+1} hatası: {e}")
                        hatali += 1
                    
                    # Barı güncelle
                    bar.progress((index + 1) / total_rows)
                
                if hatali > 0:
                    st.warning(f"⚠️ İşlem tamamlandı ama {hatali} satır yüklenemedi. Excel sütun başlıklarını ve bina adlarını kontrol edin!")
                st.success(f"✅ {basarili} asansör başarıyla eklendi!")
                
        except Exception as e:
            st.error(f"❌ Excel okunurken hata oluştu: {e}")
            st.info("📝 Excel'deki sütun başlıklarının yukarıdaki formatta olduğundan emin olun.")

# === KULLANICI YÖNETİMİ (SADECE ADMIN) ===
elif selected == "👥 Kullanıcı Yönetimi":
    st.title("👥 Kullanıcı Yönetimi")
    
    tab1, tab2 = st.tabs(["➕ Yeni Kullanıcı Ekle", "📋 Kullanıcı Listesi"])
    
    with tab1:
        st.markdown("### ➕ Yeni Kullanıcı Oluştur")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("👤 Kullanıcı Adı", placeholder="ör: ahmet_yilmaz")
            new_password = st.text_input("🔑 Şifre", type="password", placeholder="Güçlü şifre")
        with col2:
            new_rol = st.selectbox("🔐 Rol", ["bina_yetkilisi", "admin"])
            
            # Bina seçimi (sadece bina yetkilisi için)
            buildings_result = supabase.table('buildings').select('*').execute()
            building_options = ["Seçiniz..."] + [b['bina_adi'] for b in buildings_result.data]
            selected_building_name = st.selectbox("🏢 Bina", building_options, disabled=(new_rol == "admin"))
        
        if st.button("✅ Kullanıcı Oluştur", type="primary", use_container_width=True):
            if new_username and new_password:
                if new_rol == "bina_yetkilisi" and selected_building_name == "Seçiniz...":
                    st.error("❌ Bina yetkilisi için bina seçimi zorunludur!")
                else:
                    try:
                        # Bina ID'sini bul
                        building_id = None
                        if new_rol == "bina_yetkilisi":
                            building = next((b for b in buildings_result.data if b['bina_adi'] == selected_building_name), None)
                            building_id = building['id'] if building else None
                        
                        # Şifreyi hashle
                        hashed_pw = hash_password(new_password)
                        
                        # Kullanıcıyı ekle
                        supabase.table('users').insert({
                            'username': new_username,
                            'password_hash': hashed_pw,
                            'building_id': building_id,
                            'rol': new_rol,
                            'aktif': True
                        }).execute()
                        
                        st.success(f"✅ Kullanıcı '{new_username}' başarıyla oluşturuldu!")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
            else:
                st.warning("⚠️ Kullanıcı adı ve şifre gereklidir!")
    
    with tab2:
        st.markdown("### 📋 Kayıtlı Kullanıcılar")
        st.markdown("---")
        
        try:
            users_result = supabase.table('users').select('*').execute()
            users = users_result.data
            
            if users:
                # Kullanıcıları tablo olarak göster
                for idx, user in enumerate(users):
                    # Bina adını al
                    building_name = "-"
                    if user.get('building_id'):
                        building_result = supabase.table('buildings').select('bina_adi').eq('id', user['building_id']).execute()
                        if building_result.data:
                            building_name = building_result.data[0]['bina_adi']
                    
                    # Kullanıcı kartı
                    st.markdown(f"""
                    <div style="background: white; padding: 15px 20px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {'#E30A17' if user['rol'] == 'admin' else '#667eea'};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 18px;">👤 {user['username']}</strong>
                                <span style="margin-left: 15px; background: {'#E30A17' if user['rol'] == 'admin' else '#667eea'}; color: white; padding: 6px 15px; border-radius: 15px; font-size: 14px; font-weight: 600;">
                                    {'🔑 Admin' if user['rol'] == 'admin' else f'🏢 {building_name}'}
                                </span>
                            </div>
                            <span style="color: #999; font-size: 12px;">📅 {user.get('created_at', '-')[:10]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # İşlem butonları
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        with st.form(f"change_pw_{user['id']}_{idx}"):
                            col_pw1, col_pw2 = st.columns([3, 1])
                            with col_pw1:
                                new_pw = st.text_input("Yeni Şifre", type="password", key=f"pw_{user['id']}_{idx}", placeholder="Yeni şifre girin")
                            with col_pw2:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.form_submit_button("🔑 Değiştir", use_container_width=True):
                                    if new_pw:
                                        try:
                                            hashed = hash_password(new_pw)
                                            supabase.table('users').update({'password_hash': hashed}).eq('id', user['id']).execute()
                                            st.success("✅ Şifre güncellendi!")
                                            time.sleep(1)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Hata: {e}")
                    
                    with col2:
                        if user['rol'] != 'admin':
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button(f"🗑️ Kullanıcıyı Sil", key=f"del_{user['id']}_{idx}", type="secondary"):
                                try:
                                    supabase.table('users').delete().eq('id', user['id']).execute()
                                    log_activity(
                                        st.session_state.user['id'],
                                        st.session_state.user['username'],
                                        'kullanici_silindi',
                                        None,
                                        None,
                                        f"Silinen kullanıcı: {user['username']}"
                                    )
                                    st.success(f"✅ '{user['username']}' silindi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                    
                    st.markdown("---")
            else:
                st.info("📭 Henüz kullanıcı yok.")
        except Exception as e:
            st.error(f"❌ Kullanıcılar yüklenemedi: {e}")

# === AKTİVİTE LOGU (SADECE ADMIN) ===
elif selected == "📊 Aktivite Logu":
    st.title("📊 Kullanıcı Aktivite Logu")
    st.markdown("### Kim Ne Yaptı?")
    st.markdown("---")
    
    # Filtreler ve Toplu İşlem
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        users_result = supabase.table('users').select('username').execute()
        user_filter = st.selectbox("👤 Kullanıcı", ["Tümü"] + [u['username'] for u in users_result.data])
    with col2:
        action_filter = st.selectbox("🔧 İşlem", ["Tümü", "bakım_eklendi", "asansör_eklendi", "kullanıcı_eklendi", "kullanıcı_silindi"])
    with col3:
        limit = st.selectbox("📊 Kayıt Sayısı", [50, 100, 200, 500], index=0)
    with col4:
        toplu_secim = st.checkbox("☑️ Toplu Seçim", help="Kayıtları seçerek toplu silebilirsiniz")
    
    try:
        # Logları çek
        query = supabase.table('activity_logs').select('*').order('created_at', desc=True).limit(limit)
        
        if user_filter != "Tümü":
            query = query.eq('username', user_filter)
        if action_filter != "Tümü":
            query = query.eq('action', action_filter)
        
        logs_result = query.execute()
        logs = logs_result.data
        
        if logs:
            st.markdown(f"### 📋 {len(logs)} Aktivite Kaydı")
            
            # Toplu silme seçenekleri
            if toplu_secim:
                col_a, col_b, col_c = st.columns([1, 1, 4])
                with col_a:
                    if st.button("✅ Tümünü Seç"):
                        for log in logs:
                            st.session_state[f"select_log_{log['id']}"] = True
                        st.rerun()
                with col_b:
                    if st.button("❌ Tümünü Kaldır"):
                        for log in logs:
                            st.session_state[f"select_log_{log['id']}"] = False
                        st.rerun()
                
                # Seçili kayıtları sil
                selected_logs = [log['id'] for log in logs if st.session_state.get(f"select_log_{log['id']}", False)]
                if selected_logs:
                    st.warning(f"⚠️ {len(selected_logs)} kayıt seçildi")
                    if st.button(f"🗑️ Seçilenleri Sil ({len(selected_logs)} kayıt)", type="primary"):
                        if st.session_state.get('confirm_bulk_delete'):
                            try:
                                for log_id in selected_logs:
                                    supabase.table('activity_logs').delete().eq('id', log_id).execute()
                                st.success(f"✅ {len(selected_logs)} aktivite kaydı silindi!")
                                # Seçimleri temizle
                                for log_id in selected_logs:
                                    if f"select_log_{log_id}" in st.session_state:
                                        del st.session_state[f"select_log_{log_id}"]
                                st.session_state.confirm_bulk_delete = False
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Hata: {e}")
                        else:
                            st.session_state.confirm_bulk_delete = True
                            st.warning("⚠️ Emin misiniz? Tekrar basın!")
                            time.sleep(2)
                            st.rerun()
            
            st.markdown("---")
            
            for log in logs:
                # Renk kodları
                action_colors = {
                    'bakım_eklendi': '#28a745',
                    'asansör_eklendi': '#17a2b8',
                    'kullanıcı_eklendi': '#ffc107',
                    'kullanıcı_silindi': '#dc3545'
                }
                color = action_colors.get(log['action'], '#6c757d')
                
                if toplu_secim:
                    col1, col2, col3 = st.columns([0.5, 8.5, 1])
                    with col1:
                        st.checkbox("", key=f"select_log_{log['id']}", label_visibility="collapsed")
                    with col2:
                        st.markdown(f"""
                        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="color: {color};">👤 {log['username']}</strong> • 
                                    <span style="color: #666;">{log['action'].replace('_', ' ').title()}</span>
                                </div>
                                <span style="color: #999; font-size: 12px;">📅 {log['created_at'][:16]}</span>
                            </div>
                            {f"<div style='margin-top: 8px; color: #555;'>🏢 <strong>{log['building_name']}</strong>" if log.get('building_name') else ""}
                            {f" • 🏘️ {log['elevator_name']}" if log.get('elevator_name') else ""}</div>
                            {f"<div style='margin-top: 5px; color: #888; font-size: 13px;'>📝 {log['details']}</div>" if log.get('details') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        if st.button("🗑️", key=f"delete_single_{log['id']}", help="Bu kaydı sil"):
                            if st.session_state.get(f"confirm_single_delete_{log['id']}"):
                                try:
                                    supabase.table('activity_logs').delete().eq('id', log['id']).execute()
                                    st.success("✅ Silindi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                            else:
                                st.session_state[f"confirm_single_delete_{log['id']}"] = True
                                st.warning("⚠️ Tekrar!")
                                time.sleep(2)
                                st.rerun()
                else:
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="color: {color};">👤 {log['username']}</strong> • 
                                    <span style="color: #666;">{log['action'].replace('_', ' ').title()}</span>
                                </div>
                                <span style="color: #999; font-size: 12px;">📅 {log['created_at'][:16]}</span>
                            </div>
                            {f"<div style='margin-top: 8px; color: #555;'>🏢 <strong>{log['building_name']}</strong>" if log.get('building_name') else ""}
                            {f" • 🏘️ {log['elevator_name']}" if log.get('elevator_name') else ""}</div>
                            {f"<div style='margin-top: 5px; color: #888; font-size: 13px;'>📝 {log['details']}</div>" if log.get('details') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("🗑️", key=f"delete_log_{log['id']}", help="Aktivite kaydını sil"):
                            if st.session_state.get(f"confirm_log_delete_{log['id']}"):
                                try:
                                    supabase.table('activity_logs').delete().eq('id', log['id']).execute()
                                    st.success("✅ Aktivite kaydı silindi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                            else:
                                st.session_state[f"confirm_log_delete_{log['id']}"] = True
                                st.warning("⚠️ Tekrar bas!")
                                time.sleep(2)
                                st.rerun()
        else:
            st.info("📭 Seçili filtrelere göre aktivite bulunamadı.")
    except Exception as e:
        st.error(f"❌ Loglar yüklenemedi: {e}")

# === ÖDENEK YÖNETİMİ (SADECE ADMIN) ===
elif selected == "💰 Ödenek Yönetimi":
    st.title("💰 Ödenek Talepleri Yönetimi")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⏳ İl Müdürlük Bekleyen", "✅ İl Müdürlük Onaylanan", "❌ İl Müdürlük Reddedilen", "📤 Ankara'ya Bildirilecek", "🏛️ Ankara Onayları"])
    
    with tab1:
        st.subheader("⏳ Bekleyen Ödenek Talepleri")
        
        try:
            talepler_result = supabase.table('odenek_talepleri')\
                .select('*')\
                .eq('durum', 'Beklemede')\
                .order('talep_tarihi', desc=False)\
                .execute()
            
            if talepler_result.data:
                for idx, talep in enumerate(talepler_result.data):
                    # Bina bilgisi
                    building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                    bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                    
                    # Asansör bilgisi (varsa)
                    if talep.get('elevator_id'):
                        elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                        if elevator_info.data:
                            elev = enrich_elevators(elevator_info.data)[0]
                            hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                        else:
                            hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                    else:
                        hedef_str = f"{bina_adi} (Tüm Bina)"
                    
                    # Talep eden kullanıcı
                    user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                    talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                    
                    # Bakım kaydı varsa getir
                    bakim_str = ""
                    if talep.get('maintenance_id'):
                        bakim_info = supabase.table('maintenance_logs').select('*').eq('id', talep['maintenance_id']).execute()
                        if bakim_info.data:
                            bakim = bakim_info.data[0]
                            servis_no = bakim.get('bakim_servis_no', 'Yok')
                            bakim_str = f"<p style='margin: 8px 0; color: #4A5568;'><strong>🔗 İlişkili Bakım:</strong> {servis_no} - {bakim.get('yapilan_islem', '')} ({bakim.get('bakim_tarihi', '')})</p>"
                    
                    # Ankara'ya bildirilme tarihi
                    ankara_str = ""
                    if talep.get('ankara_talep_tarihi'):
                        ankara_user_info = supabase.table('users').select('username').eq('id', talep['ankara_talep_eden_user_id']).execute()
                        ankara_bildiren = ankara_user_info.data[0]['username'] if ankara_user_info.data else 'Bilinmeyen'
                        ankara_str = f"<p style='margin: 8px 0; color: #4A5568; background: #fff3cd; padding: 8px; border-radius: 5px;'><strong>📤 Ankara'ya Bildirildi:</strong> {format_tarih(talep['ankara_talep_tarihi'])} ({ankara_bildiren})</p>"
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #ffc107;">
                        <h4 style="margin: 0 0 15px 0; color: #2D3748;">{hedef_str}</h4>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Bize Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                        {bakim_str}
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # İl Müdürlük Onay/Red işlemleri
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        onay_notu = st.text_input("💬 İl Müdürlük Notu (opsiyonel)", key=f"note_{talep['id']}")
                    with col2:
                        if st.button("✅ Onayla", key=f"approve_{talep['id']}", type="primary"):
                            try:
                                supabase.table('odenek_talepleri').update({
                                    'durum': 'Onaylandı',
                                    'onaylayan_user_id': st.session_state.user['id'],
                                    'onay_tarihi': datetime.now().isoformat(),
                                    'onay_notu': onay_notu if onay_notu else None
                                }).eq('id', talep['id']).execute()
                                
                                log_activity(
                                    st.session_state.user['id'],
                                    st.session_state.user['username'],
                                    'odenek_onaylandi',
                                    bina_adi,
                                    hedef_str,
                                    f"{talep['tutar']:.2f} TL ödenek İl Müdürlük tarafından onaylandı"
                                )
                                
                                st.success("✅ İl Müdürlük onayı verildi!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Hata: {e}")
                    
                    with col3:
                        if st.button("❌ Reddet", key=f"reject_{talep['id']}"):
                            try:
                                supabase.table('odenek_talepleri').update({
                                    'durum': 'Reddedildi',
                                    'onaylayan_user_id': st.session_state.user['id'],
                                    'onay_tarihi': datetime.now().isoformat(),
                                    'onay_notu': onay_notu if onay_notu else None
                                }).eq('id', talep['id']).execute()
                                
                                log_activity(
                                    st.session_state.user['id'],
                                    st.session_state.user['username'],
                                    'odenek_reddedildi',
                                    bina_adi,
                                    hedef_str,
                                    f"{talep['tutar']:.2f} TL ödenek reddedildi"
                                )
                                
                                st.warning("❌ Talep reddedildi!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Hata: {e}")
                    
                    st.markdown("---")
            else:
                st.info("📭 Bekleyen ödenek talebi bulunmuyor.")
        except Exception as e:
            st.error(f"❌ Talepler getirilemedi: {e}")
    
    with tab2:
        st.subheader("✅ Onaylanan Ödenek Talepleri")
        
        try:
            talepler_result = supabase.table('odenek_talepleri')\
                .select('*')\
                .eq('durum', 'Onaylandı')\
                .order('onay_tarihi', desc=True)\
                .execute()
            
            if talepler_result.data:
                total_onaylanan = sum(t['tutar'] for t in talepler_result.data)
                st.success(f"💰 Toplam Onaylanan Tutar: **{total_onaylanan:,.2f} TL**")
                st.markdown("---")
                
                for talep in talepler_result.data:
                    # Bina bilgisi
                    building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                    bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                    
                    # Asansör bilgisi (varsa)
                    if talep.get('elevator_id'):
                        elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                        if elevator_info.data:
                            elev = enrich_elevators(elevator_info.data)[0]
                            hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                        else:
                            hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                    else:
                        hedef_str = f"{bina_adi} (Tüm Bina)"
                    
                    # Talep eden kullanıcı
                    user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                    talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                    
                    # Onaylayan kullanıcı
                    onaylayan_info = supabase.table('users').select('username').eq('id', talep['onaylayan_user_id']).execute()
                    onaylayan = onaylayan_info.data[0]['username'] if onaylayan_info.data else 'Bilinmeyen'
                    
                    # Ankara'ya bildirilme tarihi
                    ankara_str = ""
                    if talep.get('ankara_talep_tarihi'):
                        ankara_user_info = supabase.table('users').select('username').eq('id', talep['ankara_talep_eden_user_id']).execute()
                        ankara_bildiren = ankara_user_info.data[0]['username'] if ankara_user_info.data else 'Bilinmeyen'
                        ankara_str = f"<p style='margin: 8px 0; color: #4A5568; background: #fff3cd; padding: 8px; border-radius: 5px;'><strong>📤 Ankara'ya Bildirildi:</strong> {format_tarih(talep['ankara_talep_tarihi'])} ({ankara_bildiren})</p>"
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #28a745;">
                        <h4 style="margin: 0 0 15px 0; color: #2D3748;">🏢 {hedef_str}</h4>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Bize Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                        {ankara_str}
                        <p style="margin: 8px 0; color: #4A5568;"><strong>✅ Onaylayan:</strong> {onaylayan}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Onay Tarihi:</strong> {format_tarih(talep.get('onay_tarihi', '-'))}</p>
                        {f"<p style='margin: 8px 0; color: #4A5568;'><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>" if talep.get('aciklama') else ""}
                        {f"<p style='margin: 8px 0; color: #4A5568;'><strong>💬 Onay Notu:</strong> {talep['onay_notu']}</p>" if talep.get('onay_notu') else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 Onaylanan ödenek talebi bulunmuyor.")
        except Exception as e:
            st.error(f"❌ Talepler getirilemedi: {e}")
    
    with tab3:
        st.subheader("❌ Reddedilen Ödenek Talepleri")
        
        try:
            talepler_result = supabase.table('odenek_talepleri')\
                .select('*')\
                .eq('durum', 'Reddedildi')\
                .order('onay_tarihi', desc=True)\
                .execute()
            
            if talepler_result.data:
                for talep in talepler_result.data:
                    # Bina ve asansör bilgisi
                    building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                    bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                    
                    # Asansör bilgisi (varsa)
                    if talep.get('elevator_id'):
                        elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                        if elevator_info.data:
                            elev = enrich_elevators(elevator_info.data)[0]
                            hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                        else:
                            hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                    else:
                        hedef_str = f"{bina_adi} (Tüm Bina)"
                    
                    user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                    talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                    
                    onaylayan_info = supabase.table('users').select('username').eq('id', talep['onaylayan_user_id']).execute()
                    onaylayan = onaylayan_info.data[0]['username'] if onaylayan_info.data else 'Bilinmeyen'
                    
                    # Ankara'ya bildirilme tarihi
                    ankara_str = ""
                    if talep.get('ankara_talep_tarihi'):
                        ankara_user_info = supabase.table('users').select('username').eq('id', talep['ankara_talep_eden_user_id']).execute()
                        ankara_bildiren = ankara_user_info.data[0]['username'] if ankara_user_info.data else 'Bilinmeyen'
                        ankara_str = f"<p style='margin: 8px 0; color: #4A5568; background: #fff3cd; padding: 8px; border-radius: 5px;'><strong>📤 Ankara'ya Bildirildi:</strong> {format_tarih(talep['ankara_talep_tarihi'])} ({ankara_bildiren})</p>"
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #dc3545;">
                        <h4 style="margin: 0 0 15px 0; color: #2D3748;">{hedef_str}</h4>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Bize Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                        {ankara_str}
                        <p style="margin: 8px 0; color: #4A5568;"><strong>❌ Reddeden:</strong> {onaylayan}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Red Tarihi:</strong> {format_tarih(talep.get('onay_tarihi', '-'))}</p>
                        {f"<p style='margin: 8px 0; color: #4A5568;'><strong>💬 Red Notu:</strong> {talep['onay_notu']}</p>" if talep.get('onay_notu') else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 Reddedilen ödenek talebi bulunmuyor.")
        except Exception as e:
            st.error(f"❌ Talepler getirilemedi: {e}")    
    with tab4:
        st.subheader("📤 Ankara'ya Bildirilecek Talepler")
        st.info("💡 İl Müdürlük tarafından onaylandı, Ankara'ya bildirilmesi gereken talepler")
        
        try:
            talepler_result = supabase.table('odenek_talepleri')\
                .select('*')\
                .eq('durum', 'Onaylandı')\
                .is_('ankara_talep_tarihi', 'null')\
                .order('onay_tarihi', desc=False)\
                .execute()
            
            if talepler_result.data:
                for talep in talepler_result.data:
                    # Bina bilgisi
                    building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                    bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                    
                    # Asansör bilgisi (varsa)
                    if talep.get('elevator_id'):
                        elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                        if elevator_info.data:
                            elev = enrich_elevators(elevator_info.data)[0]
                            hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                        else:
                            hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                    else:
                        hedef_str = f"{bina_adi} (Tüm Bina)"
                    
                    # Talep eden kullanıcı
                    user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                    talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                    
                    # Onaylayan kullanıcı
                    onaylayan_info = supabase.table('users').select('username').eq('id', talep['onaylayan_user_id']).execute()
                    onaylayan = onaylayan_info.data[0]['username'] if onaylayan_info.data else 'Bilinmeyen'
                    
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #17a2b8;">
                        <h4 style="margin: 0 0 15px 0; color: #2D3748;">🏢 {hedef_str}</h4>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Talep Tarihi:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>✅ İl Müd. Onaylayan:</strong> {onaylayan}</p>
                        <p style="margin: 8px 0; color: #4A5568;"><strong>📅 İl Müd. Onay:</strong> {format_tarih(talep.get('onay_tarihi', '-'))}</p>
                        {f"<p style='margin: 8px 0; color: #4A5568;'><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>" if talep.get('aciklama') else ""}
                        {f"<p style='margin: 8px 0; color: #4A5568;'><strong>💬 İl Müd. Notu:</strong> {talep['onay_notu']}</p>" if talep.get('onay_notu') else ""}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📤 Ankara'ya Bildir", key=f"ankara_bildir_{talep['id']}", type="primary"):
                        try:
                            supabase.table('odenek_talepleri').update({
                                'ankara_talep_tarihi': datetime.now().isoformat(),
                                'ankara_talep_eden_user_id': st.session_state.user['id']
                            }).eq('id', talep['id']).execute()
                            
                            log_activity(
                                st.session_state.user['id'],
                                st.session_state.user['username'],
                                'ankara_talep',
                                bina_adi,
                                hedef_str,
                                f"{talep['tutar']:.2f} TL ödenek Ankara'ya bildirildi"
                            )
                            
                            st.success("📤 Ankara'ya bildirildi!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Hata: {e}")
                    
                    st.markdown("---")
            else:
                st.info("📭 Ankara'ya bildirilecek talep bulunmuyor.")
        except Exception as e:
            st.error(f"❌ Talepler getirilemedi: {e}")
    
    with tab5:
        st.subheader("🏛️ Ankara Onayları")
        
        tab5_1, tab5_2, tab5_3 = st.tabs(["⏳ Ankara'da Bekleyen", "✅ Ankara Onaylı", "❌ Ankara Reddetti"])
        
        with tab5_1:
            st.info("💡 Ankara'ya bildirildi, Ankara kararı bekleniyor")
            
            try:
                talepler_result = supabase.table('odenek_talepleri')\
                    .select('*')\
                    .eq('durum', 'Onaylandı')\
                    .not_.is_('ankara_talep_tarihi', 'null')\
                    .eq('ankara_durum', 'Beklemede')\
                    .order('ankara_talep_tarihi', desc=False)\
                    .execute()
                
                if talepler_result.data:
                    for talep in talepler_result.data:
                        # Bina bilgisi
                        building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                        bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                        
                        # Asansör bilgisi (varsa)
                        if talep.get('elevator_id'):
                            elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                            if elevator_info.data:
                                elev = enrich_elevators(elevator_info.data)[0]
                                hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                            else:
                                hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                        else:
                            hedef_str = f"{bina_adi} (Tüm Bina)"
                        
                        # Talep eden kullanıcı
                        user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                        talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                        
                        # Ankara'ya bildiren
                        ankara_bildiren_info = supabase.table('users').select('username').eq('id', talep['ankara_talep_eden_user_id']).execute()
                        ankara_bildiren = ankara_bildiren_info.data[0]['username'] if ankara_bildiren_info.data else 'Bilinmeyen'
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #ffc107;">
                            <h4 style="margin: 0 0 15px 0; color: #2D3748;">🏢 {hedef_str}</h4>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 İlk Talep:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📤 Ankara'ya Bildirildi:</strong> {format_tarih(talep['ankara_talep_tarihi'])} ({ankara_bildiren})</p>
                            {f"<p style='margin: 8px 0; color: #4A5568;'><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>" if talep.get('aciklama') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Ankara Onay/Red
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            ankara_notu = st.text_input("💬 Ankara Notu (opsiyonel)", key=f"ankara_note_{talep['id']}")
                        with col2:
                            if st.button("✅ Ankara Onayladı", key=f"ankara_onayla_{talep['id']}", type="primary"):
                                try:
                                    supabase.table('odenek_talepleri').update({
                                        'ankara_durum': 'Onaylandı',
                                        'ankara_onaylayan_user_id': st.session_state.user['id'],
                                        'ankara_onay_tarihi': datetime.now().isoformat(),
                                        'ankara_onay_notu': ankara_notu if ankara_notu else None
                                    }).eq('id', talep['id']).execute()
                                    
                                    log_activity(
                                        st.session_state.user['id'],
                                        st.session_state.user['username'],
                                        'ankara_onaylandi',
                                        bina_adi,
                                        hedef_str,
                                        f"{talep['tutar']:.2f} TL ödenek Ankara tarafından onaylandı"
                                    )
                                    
                                    st.success("✅ Ankara onayı verildi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                        with col3:
                            if st.button("❌ Ankara Reddetti", key=f"ankara_reddet_{talep['id']}"):
                                try:
                                    supabase.table('odenek_talepleri').update({
                                        'ankara_durum': 'Reddedildi',
                                        'ankara_onaylayan_user_id': st.session_state.user['id'],
                                        'ankara_onay_tarihi': datetime.now().isoformat(),
                                        'ankara_onay_notu': ankara_notu if ankara_notu else None
                                    }).eq('id', talep['id']).execute()
                                    
                                    log_activity(
                                        st.session_state.user['id'],
                                        st.session_state.user['username'],
                                        'ankara_reddedildi',
                                        bina_adi,
                                        hedef_str,
                                        f"{talep['tutar']:.2f} TL ödenek Ankara tarafından reddedildi"
                                    )
                                    
                                    st.warning("❌ Ankara tarafından reddedildi!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hata: {e}")
                        
                        st.markdown("---")
                else:
                    st.info("📭 Ankara'da bekleyen talep bulunmuyor.")
            except Exception as e:
                st.error(f"❌ Talepler getirilemedi: {e}")
        
        with tab5_2:
            st.success("✅ Ankara tarafından onaylanan talepler")
            
            try:
                talepler_result = supabase.table('odenek_talepleri')\
                    .select('*')\
                    .eq('ankara_durum', 'Onaylandı')\
                    .order('ankara_onay_tarihi', desc=True)\
                    .execute()
                
                if talepler_result.data:
                    total_ankara_onay = sum(t['tutar'] for t in talepler_result.data)
                    st.success(f"💰 Ankara Onaylı Toplam: **{total_ankara_onay:,.2f} TL**")
                    st.markdown("---")
                    
                    for talep in talepler_result.data:
                        # Bina bilgisi
                        building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                        bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                        
                        # Asansör bilgisi (varsa)
                        if talep.get('elevator_id'):
                            elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                            if elevator_info.data:
                                elev = enrich_elevators(elevator_info.data)[0]
                                hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                            else:
                                hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                        else:
                            hedef_str = f"{bina_adi} (Tüm Bina)"
                        
                        # Talep eden kullanıcı
                        user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                        talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #28a745;">
                            <h4 style="margin: 0 0 15px 0; color: #2D3748;">🏢 {hedef_str}</h4>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 İlk Talep:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Ankara Onay:</strong> {format_tarih(talep.get('ankara_onay_tarihi', '-'))}</p>
                            {f"<p style='margin: 8px 0; color: #4A5568;'><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>" if talep.get('aciklama') else ""}
                            {f"<p style='margin: 8px 0; color: #4A5568;'><strong>💬 Ankara Notu:</strong> {talep['ankara_onay_notu']}</p>" if talep.get('ankara_onay_notu') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("📭 Ankara onaylı talep bulunmuyor.")
            except Exception as e:
                st.error(f"❌ Talepler getirilemedi: {e}")
        
        with tab5_3:
            st.error("❌ Ankara tarafından reddedilen talepler")
            
            try:
                talepler_result = supabase.table('odenek_talepleri')\
                    .select('*')\
                    .eq('ankara_durum', 'Reddedildi')\
                    .order('ankara_onay_tarihi', desc=True)\
                    .execute()
                
                if talepler_result.data:
                    for talep in talepler_result.data:
                        # Bina bilgisi
                        building_info = supabase.table('buildings').select('*').eq('id', talep['building_id']).execute()
                        bina_adi = building_info.data[0]['bina_adi'] if building_info.data else 'Bilinmeyen'
                        
                        # Asansör bilgisi (varsa)
                        if talep.get('elevator_id'):
                            elevator_info = supabase.table('elevators').select('*').eq('id', talep['elevator_id']).execute()
                            if elevator_info.data:
                                elev = enrich_elevators(elevator_info.data)[0]
                                hedef_str = f"{bina_adi} - {elev.get('blok', '-')} - {elev.get('kimlik', '-')}"
                            else:
                                hedef_str = f"{bina_adi} (Asansör bulunamadı)"
                        else:
                            hedef_str = f"{bina_adi} (Tüm Bina)"
                        
                        # Talep eden kullanıcı
                        user_info = supabase.table('users').select('username').eq('id', talep['talep_eden_user_id']).execute()
                        talep_eden = user_info.data[0]['username'] if user_info.data else 'Bilinmeyen'
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #dc3545;">
                            <h4 style="margin: 0 0 15px 0; color: #2D3748;">🏢 {hedef_str}</h4>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>👤 Talep Eden:</strong> {talep_eden}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>💵 Tutar:</strong> {talep['tutar']:.2f} TL</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 İlk Talep:</strong> {format_tarih(talep['talep_tarihi'])}</p>
                            <p style="margin: 8px 0; color: #4A5568;"><strong>📅 Ankara Red:</strong> {format_tarih(talep.get('ankara_onay_tarihi', '-'))}</p>
                            {f"<p style='margin: 8px 0; color: #4A5568;'><strong>📝 Açıklama:</strong> {talep['aciklama']}</p>" if talep.get('aciklama') else ""}
                            {f"<p style='margin: 8px 0; color: #4A5568;'><strong>💬 Ankara Red Notu:</strong> {talep['ankara_onay_notu']}</p>" if talep.get('ankara_onay_notu') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("📭 Ankara tarafından reddedilen talep bulunmuyor.")
            except Exception as e:
                st.error(f"❌ Talepler getirilemedi: {e}")