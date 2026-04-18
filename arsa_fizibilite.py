import streamlit as st
import pandas as pd

# --- FONKSİYONLAR ---
def pmt_hesapla(anapara, aylik_faiz, vade):
    if anapara <= 0 or aylik_faiz <= 0 or vade <= 0:
        return 0
    r = aylik_faiz / 100
    return (anapara * r * (1 + r)**vade) / ((1 + r)**vade - 1)

def hesapla_rapor(veriler):
    taban_alani = veriler['arsa_alani'] * veriler['taks']
    cikma_alani = taban_alani * (veriler['cikma_orani'] / 100)
    normal_kat_alani = taban_alani + cikma_alani
    toplam_emsal_alani = veriler['arsa_alani'] * veriler['kaks']
    
    hesaplanan_kat = (toplam_emsal_alani - taban_alani) / normal_kat_alani + 1
    
    if veriler['max_kat_siniri'] > 0 and hesaplanan_kat > veriler['max_kat_siniri']:
        kat_sayisi = veriler['max_kat_siniri']
        kullanilan_emsal = taban_alani + (normal_kat_alani * (kat_sayisi - 1))
        emsal_ziyani = toplam_emsal_alani - kullanilan_emsal
    else:
        kat_sayisi = hesaplanan_kat
        kullanilan_emsal = toplam_emsal_alani
        emsal_ziyani = 0
    
    toplam_hasilat_alani = kullanilan_emsal * 1.25 
    
    dagilim = {
        "1+1": toplam_hasilat_alani * 0.20,
        "2+1": toplam_hasilat_alani * 0.50,
        "3+1": toplam_hasilat_alani * 0.30
    }
    birim_fiyatlar = {"1+1": veriler['fiyat_1_1'], "2+1": veriler['fiyat_2_1'], "3+1": veriler['fiyat_3_1']}
    
    uniteler = []
    toplam_hasilat = 0
    for tip, alan in dagilim.items():
        adet = int(alan / veriler[f'm2_{tip.replace("+","_")}'])
        if adet > 0:
            hasilat = adet * veriler[f'm2_{tip.replace("+","_")}'] * birim_fiyatlar[tip]
            toplam_hasilat += hasilat
            uniteler.append({"Tip": tip, "Adet": adet, "Birim m²": veriler[f'm2_{tip.replace("+","_")}'], "Satış Bedeli (TL)": hasilat})

    toplam_insaat_maliyeti = kullanilan_emsal * 1.25 * veriler['birim_maliyet'] 
    aylik_taksit = pmt_hesapla(veriler['kredi'], veriler['faiz'], veriler['vade'])
    toplam_faiz = (aylik_taksit * veriler['vade']) - veriler['kredi']
    
    hedef_kar_tutari = toplam_hasilat * (veriler['hedef_kar'] / 100)
    max_arsa_bedeli = toplam_hasilat - toplam_insaat_maliyeti - toplam_faiz - hedef_kar_tutari
    
    return {
        "taban_alani": taban_alani, "normal_kat_alani": normal_kat_alani, "kat_sayisi": kat_sayisi,
        "kullanilan_emsal": kullanilan_emsal, "emsal_ziyani": emsal_ziyani,
        "uniteler": pd.DataFrame(uniteler) if uniteler else pd.DataFrame(),
        "toplam_hasilat": toplam_hasilat, "toplam_maliyet": toplam_insaat_maliyeti,
        "toplam_faiz": toplam_faiz, "hedef_kar_tutari": hedef_kar_tutari, "max_arsa_bedeli": max_arsa_bedeli
    }

# --- GÜNCEL, RESMİ VE KURUMSAL ARAYÜZ TASARIMI ---
st.set_page_config(page_title="Arazi Değerleme Raporu", layout="wide", initial_sidebar_state="expanded")

# CSS Enjeksiyonu (Google Fonts ve Kurumsal Stil)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    /* Genel font ayarı */
    html, body, [class*="css"], .stMarkdown, p, label {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Başlıklar için resmi serif font */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        color: #1a365d !important;
    }

    /* Arka plan görseli */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Ana Rapor Panosu */
    .block-container {
        background-color: rgba(255, 255, 255, 0.96) !important;
        padding: 4rem 3rem !important;
        border-radius: 4px !important; /* Daha keskin, ciddi köşeler */
        box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.15) !important;
        margin-top: 40px;
        margin-bottom: 40px;
        border-top: 5px solid #1a365d; /* Kurumsal üst bant */
    }

    h1 { 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        text-align: center;
        font-size: 36px !important;
        margin-bottom: 5px;
    }
    
    .subtitle {
        text-align: center;
        color: #4a5568;
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 1px;
        margin-bottom: 40px;
        text-transform: uppercase;
    }

    /* Buton Tasarımı - Daha düz ve ağırbaşlı */
    .stButton>button {
        background-color: #1a365d !important;
        color: white !important; 
        border-radius: 3px !important;
        padding: 15px !important; 
        font-size: 14px !important; 
        font-weight: 600 !important; 
        border: none !important; 
        width: 100% !important; 
        transition: 0.3s !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { 
        background-color: #2b6cb0 !important; 
    }
    
    /* Metrik Değerleri */
    [data-testid="stMetricValue"] { 
        font-size: 24px !important; 
        color: #1a365d !important; 
        font-weight: 700 !important; 
        font-family: 'Montserrat', sans-serif !important;
    }
    [data-testid="stMetricLabel"] { 
        font-size: 12px !important; 
        color: #4a5568 !important; 
        font-weight: 600 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Nihai Sonuç Kutusu (Sadeleştirildi) */
    .final-box {
        background-color: #f7fafc;
        padding: 30px;
        border-left: 6px solid #2f855a;
        margin-top: 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .final-box-error {
        background-color: #fff5f5;
        padding: 30px;
        border-left: 6px solid #c53030;
        margin-top: 30px;
    }
    .final-box h2, .final-box-error h2 {
        font-size: 14px !important;
        color: #4a5568 !important;
        font-family: 'Montserrat', sans-serif !important;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .final-box h1 {
        font-size: 36px !important;
        color: #276749 !important;
        margin: 0;
        font-family: 'Montserrat', sans-serif !important;
        text-align: left;
    }
    .final-box-error h1 {
        font-size: 24px !important;
        color: #9b2c2c !important;
        margin: 0;
        text-align: left;
    }
    .final-box p, .final-box-error p {
        color: #718096;
        font-size: 13px;
        margin-top: 10px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Arazi Değerleme Raporu</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Gayrimenkul Yatırım ve Fizibilite Analiz Sistemi</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Girdi Parametreleri")
    
    with st.expander("İmar ve Arazi Verileri", expanded=True):
        arsa_alani = st.number_input("Arsa Alanı (m²)", value=2000)
        kaks = st.number_input("Emsal (KAKS)", value=3.0, step=0.1)
        taks = st.number_input("Taban Katsayısı (TAKS)", value=0.40, step=0.05)
        max_kat_siniri = st.number_input("Yençok (Kat Sınırı)", value=0, step=1)
        cikma_orani = st.slider("Çıkma Oranı (%)", 0, 20, 10)
    
    with st.expander("Maliyet ve Kar Hedefi", expanded=False):
        birim_maliyet = st.number_input("İnşaat m² Maliyeti (₺)", value=28000)
        hedef_kar = st.slider("Hedef Kar Marjı (%)", 5, 100, 35, step=5)
    
    with st.expander("Satış Birim Fiyatları", expanded=False):
        c_a, c_b = st.columns(2)
        m2_1_1 = c_a.number_input("1+1 m²", value=75)
        fiyat_1_1 = c_b.number_input("1+1 Satış", value=110000)
        m2_2_1 = c_a.number_input("2+1 m²", value=115)
        fiyat_2_1 = c_b.number_input("2+1 Satış", value=125000)
        m2_3_1 = c_a.number_input("3+1 m²", value=160)
        fiyat_3_1 = c_b.number_input("3+1 Satış", value=145000)

    with st.expander("Finansman Koşulları", expanded=False):
        kredi = st.number_input("Kredi Tutarı (₺)", value=60000000)
        vade = st.slider("Vade (Ay)", 6, 60, 24)
        faiz = st.number_input("Aylık Faiz (%)", value=3.7, step=0.1)

input_data = locals() 

if st.button("Analizi Başlat ve Raporu Üret", use_container_width=True):
    res = hesapla_rapor(input_data)
    
    st.markdown("#### Teknik Yapı Analizi")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Taban Alanı", f"{res['taban_alani']:,.0f} m²")
    m2.metric("Normal Kat Alanı", f"{res['normal_kat_alani']:,.0f} m²")
    m3.metric("Bina Yüksekliği", f"{res['kat_sayisi']:.1f} Kat")
    m4.metric("Gerçekleşen Emsal", f"{res['kullanilan_emsal']:,.0f} m²")
    
    if res['emsal_ziyani'] > 0:
        st.warning(f"Dikkat: Kat sınırından dolayı {res['emsal_ziyani']:,.0f} m² inşaat hakkı kullanılamadı.")
    
    st.divider()
    
    col_tablo, col_finans = st.columns([1, 1.2])
    
    with col_tablo:
        st.markdown("#### Bağımsız Bölüm Dağılımı")
        if not res['uniteler'].empty:
            st.dataframe(res['uniteler'], use_container_width=True, hide_index=True)
        
    with col_finans:
        st.markdown("#### Proje Finansal Tablosu")
        f1, f2 = st.columns(2)
        f1.info(f"Gider: Toplam İnşaat\n\n### {res['toplam_maliyet']:,.0f} ₺")
        f2.info(f"Gider: Finansman Faizi\n\n### {res['toplam_faiz']:,.0f} ₺")
        
        f3, f4 = st.columns(2)
        f3.warning(f"Gelir: Toplam Hasılat\n\n### {res['toplam_hasilat']:,.0f} ₺")
        f4.success(f"Net Kar (Beklenen)\n\n### {res['hedef_kar_tutari']:,.0f} ₺")
        
    if res['max_arsa_bedeli'] > 0:
        st.markdown(f"""
            <div class="final-box">
                <h2>Maksimum Arsa Satın Alma Bedeli</h2>
                <h1>{res['max_arsa_bedeli']:,.0f} ₺</h1>
                <p>Bu değer, projenin %{hedef_kar} kar marjını koruyabildiği tavan fiyattır.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="final-box-error">
                <h2>Risk Uyarısı</h2>
                <h1>Proje Zarar Üretiyor</h1>
                <p>Mevcut maliyet ve hasılat parametreleriyle bu arsa için teklif verilmesi finansal olarak uygun değildir.</p>
            </div>
        """, unsafe_allow_html=True)
        