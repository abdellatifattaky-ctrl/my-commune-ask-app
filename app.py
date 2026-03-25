import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# 1. دالة تحويل المبالغ
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else: text += " ,00CTS"
        return text
    except: return "________________"

# 2. إعدادات الصفحة وحفظ البيانات (Session State)
st.set_page_config(page_title="Commune Askaouen", layout="wide")

if 'p_name' not in st.session_state: st.session_state.p_name = "MOHAMED ZILALI"
if 'd_name' not in st.session_state: st.session_state.d_name = "M BAREK BAK"
if 't_name' not in st.session_state: st.session_state.t_name = "ABDELLATIF ATTAKY"

# 3. الواجهة الجانبية
st.sidebar.header("👤 أعضاء اللجنة")
st.session_state.p_name = st.sidebar.text_input("Président", st.session_state.p_name)
st.session_state.d_name = st.sidebar.text_input("Directeur", st.session_state.d_name)
st.session_state.t_name = st.sidebar.text_input("Technicien", st.session_state.t_name)

# 4. العنوان الرئيسي
st.title("🏛️ نظام استخراج المحاضر - جماعة أسكاون")

# 5. البيانات الإدارية
with st.expander("📝 تفاصيل الملف", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication", date(2025, 3, 25))
    obj_bc = st.text_area("Objet", "Achat de matériel...")

# 6. جدول الشركات الخمس
st.subheader("📊 قائمة المتنافسين")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True, num_rows="dynamic")

# 7. خيارات المحضر
st.divider()
col_a, col_b, col_c = st.columns(3)
pv_num = col_a.selectbox("رقم المحضر:", [1, 2, 3, 4, 5, 6])
reunion_date = col_c.date_input("تاريخ الجلسة", date.today())
reunion_hour = col_b.text_input("الساعة", "10h00mn")

# منطق المحضر 6 أو الإسناد النهائي
is_infructueux = False
is_final_attr = False
if pv_num == 6:
    res_6 = st.radio("نتيجة المحضر 6:", ["Attribution", "Infructueux"])
    is_infructueux = (res_6 == "Infructueux")
    is_final_attr = (res_6 == "Attribution")
else:
    is_final_attr = st.checkbox("✅ هل هذا هو محضر الإسناد النهائي؟")

# 8. زر الإنشاء والبرمجة الداخلية
if st.button("🚀 إنشاء وتحميل المحضر"):
    doc = Document()
    section = doc.sections[0]
    
    # الرأس (Header)
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nCOMMUNE ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان في الصفحة
    doc.add_heading(f"Procès Verbal N° {pv_num}", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Objet: {obj_bc}").bold = True

    # منطق اختيار الشركة بناء على رقم المحضر
    idx = min(pv_num - 1, len(data) - 1)
    curr_co = data.iloc[idx]['Nom']
    curr_amt = data.iloc[idx]['Montant']
    
    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission s'est réunie...")
    
    if is_final_attr:
        doc.add_paragraph(f"Conclusion: Attribution à {curr_co} pour {curr_amt} DH.")
    elif is_infructueux:
        doc.add_paragraph("Conclusion: Le Bon de Commande est Infructueux.")
    else:
        doc.add_paragraph(f"La commission invite la société {curr_co} à confirmer son offre.")

    # التوقيعات
    doc.add_paragraph("\nSignatures:")
    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.rows[0].cells[0].text = "Président"
    sig_tab.rows[0].cells[1].text = "Directeur"
    sig_tab.rows[0].cells[2].text = "Technicien"
    sig_tab.rows[1].cells[0].text = st.session_state.p_name
    sig_tab.rows[1].cells[1].text = st.session_state.d_name
    sig_tab.rows[1].cells[2].text = st.session_state.t_name

    # تحويل الملف للتحميل
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل المحضر {pv_num}", bio.getvalue(), f"PV_{pv_num}.docx")
    st.success("تم تجهيز الملف بنجاح!")
