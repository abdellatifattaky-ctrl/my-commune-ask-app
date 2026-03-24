import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# دالة تحويل المبالغ إلى حروف بالفرنسية
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        # إضافة السنتيمات
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ,00CTS"
        return text
    except: return "________________"

st.set_page_config(page_title="Commune Askaouen - PV Final", layout="wide")

# القائمة الجانبية للجنة
st.sidebar.header("Membres de la commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ نظام توليد المحاضر - جماعة أسكاون")

# إدخال البيانات
with st.expander("📝 معلومات الملف العام"):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2025")
    date_pub = c2.date_input("Date de publication", date(2025, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle pour les travaux divers.")

# جدول المتنافسين
st.subheader("📊 قائمة المتنافسين الخمسة")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

# اختيار المحضر والسيناريو
st.divider()
pv_num = st.selectbox("رقم المحضر الحالي:", [1, 2, 3, 4, 5])
is_final_attribution = st.checkbox("✅ هل هذا هو محضر الإسناد النهائي (Attribution)؟")
reunion_date = st.date_input("تاريخ اجتماع اليوم", date.today())
reunion_hour = st.text_input("الساعة", "12h00mn")
next_rdv = st.date_input("موعد الجلسة القادمة (في حالة عدم الإسناد)")

if st.button("🚀 توليد المحضر الآن"):
    doc = Document()
    
    # الترويسة
    header = doc.sections[0].header
    htable =
