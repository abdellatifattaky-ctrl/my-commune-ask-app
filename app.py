import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- 1. الدوال المساعدة (Helper Functions) ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        return f"{words} DIRHAMS"
    except: return "________________"

def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

def set_global_font(doc):
    for p in doc.paragraphs:
        for run in p.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(12)

# --- 2. إعدادات الواجهة ---
st.set_page_config(page_title="Système Intégré - Askaouen", layout="wide")

if 'p_name' not in st.session_state: st.session_state.p_name = "MOHAMED ZILALI"
if 'd_name' not in st.session_state: st.session_state.d_name = "M BAREK BAK"
if 't_name' not in st.session_state: st.session_state.t_name = "ABDELLATIF ATTAKY"

with st.sidebar:
    st.header("👥 لجنة الإشراف")
    st.session_state.p_name = st.text_input("رئيس اللجنة", st.session_state.p_name)
    st.session_state.d_name = st.text_input("مدير المصالح", st.session_state.d_name)
    st.session_state.t_name = st.text_input("التقني الجماعي", st.session_state.t_name)
    st.divider()
    st.info("جماعة أسكاون - نظام تدبير سندات الطلب")

# --- 3. نظام الخانات (Tabs) ---
t1, t2, t3, t4, t5, t6 = st.tabs([
    "🏗️ إعداد السند", "📑 المحاضر (PVs)", "✉️ التبليغ (Notif)", 
    "🚦 أمر الخدمة (OS)", "✅ الاستلام (PV-R)", "📸 ألبوم الصور"
])

# --- TAB 1: إعداد السند والمتنافسين ---
with t1:
    st.header("1️⃣ إدخال بيانات السند والمتنافسين")
    c1, c2 = st.columns(2)
    with c1:
        num_bc = st.text_input("رقم سند الطلب (N° BC)", "01/ASK/2026")
        obj_bc = st.text_area("موضوع سند الطلب (Objet)", "شراء مواد التجهيز...")
    with c2:
        date_pub = st.date_input("تاريخ النشر بالبوابة", date.today())
        winner_co = st.text_input("اسم الشركة الفائزة", "STE OUBRAIM SARL")
    
    st.subheader("📊 لائحة المتنافسين والأسعار")
    df_init = pd.DataFrame([
        {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
        {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
        {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
        {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
        {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
    ])
    data = st.data_editor(df_init, use_container_width=True)

# --- TAB 2: المحاضر (بكل التفاصيل القانونية) ---
with t2:
    st.header("2️⃣ استخراج المحاضر الرسمية")
    col_pv, col_opt = st.columns(2)
    pv_num = col_pv.selectbox("رقم المحضر الحالي:", [1,2,3,4,5,6])
    is_infruct = col_opt.checkbox("🚩 محضر غير مثمر (PV Infructueux)")
    is_final = col_opt.toggle("✅ إسناد نهائي (Attribution Finale)")
    
    if st.button("🚀 توليد وتحميل المحضر"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        
        if is_infruct:
            doc.add_paragraph("\nLa commission constate qu'aucune offre n'est avantageuse. En conséquence, la procédure est déclarée INFRUCTUEUSE.").bold = True
        else:
            idx = min(pv_num-1, len(data)-1)
            c_name = data.iloc[idx]['Nom']
            c_amt = data.iloc[idx]['Montant']
            amt_txt = format_to_words_fr(c_amt)
            
            if pv_num == 1:
                doc.add_paragraph(f"Après examen des offres, le président invite la société {c_name} pour un montant de {c_amt} DH TTC ({amt_txt}) à confirmer son offre.")
            
            if not is_final:
                next_day = date.today() + timedelta(days=1)
                doc.add_paragraph(f"\nLe président suspend la séance et fixe un rendez-vous le {next_day.strftime('%d/%m/%Y')} ou sur invitation.")
            else:
                doc.add_paragraph(f"\nLe président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {c_name}.").bold = True
        
        set_global_font(doc)
        bio = BytesIO(); doc.save(bio)
        st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}.docx")

# --- TAB 3: التبليغ (Notification) ---
with t3:
    st.header("3️⃣ رسالة التبليغ (Notification)")
    notif_dt = st.date_input("تاريخ رسالة التبليغ", date.today())
    if st.button("📄 توليد رسالة التبليغ"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_paragraph(f"\nAskaouen, le {notif_dt.strftime('%d/%m/%Y')}")
        doc.add_paragraph(f"\nA Monsieur le Directeur de la société {winner_co}")
        doc.add_paragraph("\nObjet : Notification d'acceptation de votre offre.")
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer que votre offre concernant {obj_bc} a été acceptée...")
        set_global_font(doc)
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل رسالة التبليغ", bio.getvalue(), "Notification.docx")

# --- TAB 4: أمر الخدمة وحساب الآجال (OS) ---
with t4:
    st.header("4️⃣ أمر الخدمة (Ordre de Service)")
    os_dt = st.date_input("تاريخ بداية الأشغال", date.today())
    délai = st.number_input("مدة الإنجاز (بالأيام)", min_value=1, value=15)
    end_dt = os_dt + timedelta(days=délai)
    st.info(f"📅 تاريخ نهاية الأشغال المتوقع: {end_dt.strftime('%d/%m/%Y')}")
    
    if st.button("🚦 توليد Ordre de Service"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_heading("ORDRE DE SERVICE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nA la société : {winner_co}")
        doc.add_paragraph(f"En exécution du BC {num_bc}, vous êtes prescrit de commencer les prestations le {os_dt}.")
        doc.add_paragraph(f"Le délai d'exécution est fixé à {délai} jours. La date limite est le {end_dt}.")
        set_global_font(doc)
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل O.S", bio.getvalue(), "OS.docx")

# --- TAB 5: محضر الاستلام (PV Reception) ---
with t5:
    st.header("5️⃣ محضر الاستلام")
    rec_dt = st.date_input("تاريخ الاستلام الفعلي", date.today())
    rec_type = st.radio("نوع الاستلام", ["Provisoire", "Définitif"])
    if st.button("✅ توليد محضر الاستلام"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_heading(f"PV DE RECEPTION {rec_type.upper()}", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le {rec_dt}, la commission constate que les prestations fournies par {winner_co} sont conformes...")
        set_global_font(doc)
        bio = BytesIO(); doc.save(bio)
        st.download_button(f"📥 تحميل محضر {rec_type}", bio.getvalue(), f"PV_Reception_{rec_type}.docx")

# --- TAB 6: ألبوم الصور التقني ---
with t6:
    st.header("6️⃣ ألبوم صور سند الطلب")
    uploaded_imgs = st.file_uploader("ارفع صور الإنجاز (JPG/PNG)", accept_multiple_files=True)
    if uploaded_imgs:
        doc_p = Document()
        doc_p.add_heading("ALBUM PHOTOS - BC " + num_bc, 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        for i, img in enumerate(uploaded_imgs):
            st.image(img, width=250)
            cap = st.text_input(f"وصف تقني للصورة {i+1}", key=f"img_cap_{i}")
            doc_p.add_picture(img, width=Inches(4))
            doc_p.add_paragraph(cap).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc_p.add_paragraph("\n")
        
        bio_p = BytesIO(); doc_p.save(bio_p)
        st.download_button("🖼️ تحميل ألبوم الصور المنسق", bio_p.getvalue(), "Album_Photos.docx")
