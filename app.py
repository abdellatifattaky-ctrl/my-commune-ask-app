import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة تحويل المبالغ المالية ---
def format_money_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(int(val), lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ET ZERO CENTIMES"
        return text
    except: return "________________"

# --- إعدادات الواجهة ---
st.set_page_config(page_title="Commune Askaouen ERP", layout="wide")

# --- القائمة الجانبية لإدارة الإعدادات ---
st.sidebar.title("⚙️ إعدادات المنصة")
mode = st.sidebar.selectbox("نوع المسطرة القانونية:", ["Bon de Commande (BC)", "Appel d'Offres (AO)"])
task = st.sidebar.radio("المهمة المطلوبة:", ["المحاضر (PVs)", "أوامر الخدمة (OS)", "المراسلات & الالتزام"])

st.sidebar.divider()
st.sidebar.subheader("✍️ لجنة الإشراف")
pres = st.sidebar.text_input("الرئيس", "MOHAMED ZILALI")
dir_serv = st.sidebar.text_input("مدير المصالح", "M BAREK BAK")
tech = st.sidebar.text_input("التقني", "ABDELLATIF ATTAKY")

# --- محرك البيانات الرئيسي ---
st.title(f"🏛️ إدارة {mode} - جماعة أسكاون")

col_a, col_b = st.columns(2)
num_ref = col_a.text_input("رقم السند / الصفقة", "01/ASK/2026")
obj_ref = col_b.text_input("موضوع المشروع", "تطوير السوق الأسبوعي / توريد معدات")

# --- قسم الجداول ---
st.subheader("📋 بيانات المتنافسين / المقاول")
df_init = pd.DataFrame([{"Nom": "STE EXAMPLE SARL", "Montant": "140000.00"}])
data = st.data_editor(df_init, use_container_width=True, num_rows="dynamic")

# --- توليد المستندات بناءً على المهمة ---
st.divider()

if task == "المحاضر (PVs)":
    pv_num = st.slider("رقم المحضر", 1, 5)
    if st.button("توليد المحضر الرسمي"):
        # (هنا يوضع كود توليد المحاضر الذي ضبطناه سابقاً)
        st.info("سيتم توليد المحضر رقم " + str(pv_num))

elif task == "أوامر الخدمة (OS)":
    os_type = st.selectbox("نوع أمر الخدمة:", ["Commencement (بداية)", "Arrêt (توقف)", "Reprise (استئناف)"])
    os_date = st.date_input("تاريخ الأمر")
    
    if st.button(f"توليد {os_type}"):
        doc = Document()
        # إضافة الترويسة المقلوبة والتنسيق (نفس منطق الكود السابق)
        p = doc.add_paragraph()
        p.add_run(f"ORDRE DE SERVICE : {os_type}\n").bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Il est ordonné à l'entreprise {data.iloc[0]['Nom']} de procéder à l'exécution (ou arrêt/reprise) des travaux relatifs à {obj_ref} à compter du {os_date}.")
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل أمر الخدمة", bio.getvalue(), f"OS_{os_type}.docx")

elif task == "المراسلات & الالتزام":
    st.info("في انتظار الصيغة الرسمية التي ستزودني بها لدمجها هنا.")

# --- رسالة تشجيعية ---
st.success("🚀 المنصة جاهزة للاختبار غداً على الحاسوب!")
