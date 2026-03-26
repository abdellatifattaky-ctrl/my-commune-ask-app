import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- 1. الدوال المساعدة ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        text = f"{words} DIRHAMS"
        return text
    except: return "________________"

def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- 2. إعدادات الواجهة ---
st.set_page_config(page_title="Askaouen Digital System", layout="wide")

if 'p_name' not in st.session_state: st.session_state.p_name = "MOHAMED ZILALI"
if 'd_name' not in st.session_state: st.session_state.d_name = "M BAREK BAK"
if 't_name' not in st.session_state: st.session_state.t_name = "ABDELLATIF ATTAKY"

# --- 3. نظام الخانات (Tabs) ---
t1, t2, t3, t4, t5, t6 = st.tabs([
    "🏗️ إعداد السند", "📑 المحاضر (PVs)", "✉️ التبليغ (Notif)", 
    "🚦 أمر الخدمة (OS)", "✅ الاستلام (PV-R)", "📸 ألبوم الصور"
])

# --- الخانة 1: إعداد السند والمتنافسين ---
with t1:
    st.header("1️⃣ إعداد بيانات السند")
    col_a, col_b = st.columns(2)
    with col_a:
        num_bc = st.text_input("N° BC", "01/ASK/2026")
        obj_bc = st.text_area("Objet du BC", "Achat de matériel...")
    with col_b:
        date_pub = st.date_input("Date Publication Portail", date.today())
        winner_name = st.text_input("الشركة الفائزة (للمراحل اللاحقة)", "STE OUBRAIM SARL")

    st.subheader("📊 لائحة المتنافسين (Top 5)")
    df_init = pd.DataFrame([
        {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
        {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
        {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
        {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
        {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
    ])
    data = st.data_editor(df_init, use_container_width=True)

# --- الخانة 2: المحاضر (PVs) ---
with t2:
    st.header("2️⃣ استخراج المحاضر القانونية")
    c_pv, c_dt = st.columns(2)
    pv_num = c_pv.selectbox("رقم المحضر:", [1,2,3,4,5,6])
    is_attr = st.checkbox("هل هذا محضر الإسناد النهائي؟")
    
    if st.button("🚀 توليد المحضر المختار"):
        doc = Document()
        add_askaouen_header(doc)
        # (هنا يوضع منطق النصوص الذي ضبطناه سابقا: suspend la séance...)
        doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        # ... تكملة النص ...
        bio = BytesIO(); doc.save(bio)
        st.download_button(f"📥 تحميل PV {pv_num}", bio.getvalue(), f"PV_{pv_num}.docx")

# --- الخانة 3: التبليغ (Notification) ---
with t3:
    st.header("3️⃣ رسالة تبليغ المصادقة")
    notif_date = st.date_input("تاريخ رسالة التبليغ", date.today())
    if st.button("📄 توليد رسالة Notification"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_paragraph(f"\nAskaouen, le {notif_date.strftime('%d/%m/%Y')}")
        doc.add_paragraph(f"\nA Monsieur le Directeur de la société {winner_name}")
        doc.add_paragraph("\nObjet : Notification d'acceptation de votre offre.")
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer أن عرضكم المتعلق بـ {obj_bc} قد تم قبوله...")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل Notification", bio.getvalue(), "Notification.docx")

# --- الخانة 4: أمر الخدمة (OS) ---
with t4:
    st.header("4️⃣ أمر الخدمة (Ordre de Service)")
    os_date = st.date_input("Date d'O.S", date.today())
    deadline = st.number_input("آجال التنفيذ (أيام)", value=15)
    if st.button("🚦 توليد Ordre de Service"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_heading("ORDRE DE SERVICE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nA la société : {winner_name}")
        doc.add_paragraph(f"\nVous êtes prescrit par le présent OS de commencer les travaux/livraisons le {os_date}...")
        doc.add_paragraph(f"Le délai d'exécution est de {deadline} jours.")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل O.S", bio.getvalue(), "OS.docx")

# --- الخانة 5: الاستلام (Réception) ---
with t5:
    st.header("5️⃣ محضر الاستلام")
    rec_date = st.date_input("تاريخ الاستلام الفعلي", date.today())
    rec_type = st.radio("نوع الاستلام", ["Provisoire", "Définitif"])
    if st.button("✅ توليد محضر الاستلام"):
        doc = Document()
        add_askaouen_header(doc)
        doc.add_heading(f"PV DE RECEPTION {rec_type.upper()}", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nLa commission constate que les prestations de {winner_name} sont conformes...")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل محضر الاستلام", bio.getvalue(), "PV_Reception.docx")

# --- الخانة 6: ألبوم الصور ---
with t6:
    st.header("6️⃣ ألبوم صور تتبع الإنجاز")
    imgs = st.file_uploader("ارفع الصور هنا", accept_multiple_files=True)
    if imgs:
        for i, img in enumerate(imgs):
            st.image(img, width=300)
            st.text_input(f"وصف الصورة {i+1}", key=f"cap_{i}")
        st.button("🖼️ تصدير الألبوم كاملاً (قريباً)")
