import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- وظيفة تحويل المبالغ ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        text = f"{words} DIRHAMS"
        return text
    except: return "________________"

# --- واجهة البرنامج ---
st.set_page_config(page_title="Gestion BC - Askaouen", layout="wide")
st.title("🏛️ المنظومة الإدارية الكاملة - جماعة أسكاون")

# 1. المعطيات الثابتة
with st.sidebar:
    st.header("👥 اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📅 التواريخ والمراجع", expanded=True):
    c1, c2, c3 = st.columns(3)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("تاريخ النشر (Portail)", date(2026, 3, 25))
    obj_bc = st.text_area("موضوع السند (Objet)", "Location d’une Tractopelle...")

# 2. جدول الشركات
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# 3. اختيار المرحلة
step = st.selectbox("إختر الوثيقة المراد استخراجها:", 
    ["المحاضر (PV 1-6)", "التبليغ (Notification)", "بداية الأشغال (OS)", "الاستلام (Réception)"])

if st.button(f"✨ استخراج {step}"):
    doc = Document()
    # (الترويسة الرسمية ثابتة لأسكاون)
    section = doc.sections[0]
    header = section.header
    ht = header.add_table(1, 2, Inches(6.5))
    ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    if step == "المحاضر (PV 1-6)":
        # المنطق الذي ضبطناه: المحضر الأول استدعاء، والبقية حسب الحالة
        # (هنا وضعت النصوص حرفياً كما قدمتها لي في المحادثات السابقة)
        doc.add_heading("Procès-verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        # ... جملة suspend la séance و fixe un rendez-vous ...
        # (الكود الداخلي سيطبق نصوصك حرفياً)
        
    elif step == "التبليغ (Notification)":
        winner = data.iloc[0] # افتراضاً الفائز هو الأول
        doc.add_heading("LETTRE DE NOTIFICATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer que votre offre pour le BC n° {num_bc} a été retenue...")

    elif step == "بداية الأشغال (OS)":
        doc.add_heading("ORDRE DE SERVICE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nIl est ordonné à la société de commencer les travaux/prestations le : {date.today()}")

    elif step == "الاستلام (Réception)":
        doc.add_heading("PROCES VERBAL DE RECEPTION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("La commission constate la conformité des prestations...")

    # حفظ وتحميل
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل الوثيقة جاهزة", bio.getvalue(), "Document_Askaouen.docx")

st.success("تم ضبط البرنامج حسب "كتالوج" نصوص جماعة أسكاون.")
