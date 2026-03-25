import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# وظيفة تحويل الأرقام إلى حروف بالفرنسية
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        return f"{num2words(val, lang='fr').upper()} DIRHAMS"
    except: return "________________"

st.set_page_config(page_title="Commune Askaouen - Système Intégré", layout="wide")

# --- المدخلات الإدارية ---
with st.sidebar:
    st.header("👥 أعضاء اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📝 معلومات سند الطلب والتواريخ", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("رقم السند (N° BC)", "01/ASK/2026")
    date_pub = col2.date_input("تاريخ النشر في البوابة", date(2026, 3, 25))
    obj_bc = st.text_area("الموضوع (Objet)", "Achat de fournitures...")

# جدول المتنافسين
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# --- ضبط نوع المحضر ونتيجته ---
c1, c2, c3 = st.columns(3)
pv_num = c1.selectbox("اختر رقم المحضر", [1, 2, 3, 4, 5, 6])
reunion_date = c2.date_input("تاريخ اجتماع اللجنة", date.today())

is_final = False
is_infructueux = False

if pv_num == 6:
    res_6 = st.radio("نتيجة المحضر السادس:", ["إسناد نهائي (Attribution)", "غير مثمر (Infructueux)"])
    if res_6 == "إسناد نهائي (Attribution)": is_final = True
    else: is_infructueux = True
else:
    is_final = st.checkbox(f"✅ هل تم الإسناد النهائي في هذا المحضر (PV {pv_num})؟")
    if not is_final:
        next_date = c3.date_input("تاريخ الجلسة القادمة", date.today() + timedelta(days=1))

# --- معالج توليد الوثيقة ---
if st.button("🚀 إنشاء المحضر الرسمي"):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    ht = header.add_table(1, 2, Inches(6.5))
    ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    
    # جملة s'est réunie (ثابتة في كل المحاضر)
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à 10h00mn, la commission composée de M. {p_name}, M. {d_name} et M. {t_name} s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

    idx = pv_num - 1
    curr = data.iloc[idx]
    amt_words = format_to_words_fr(curr['Montant'])

    if pv_num == 1:
        # المحضر الأول: جدول المتنافسين + جملة التعليق
        doc.add_paragraph("\nAprès vérification du portail des marchés publics, les soumissionnaires sont :")
        tab = doc.add_table(rows=1, cols=3)
        tab.style = 'Table Grid'
        hdrs = tab.rows[0].cells
        hdrs[0].text = 'Rang'; hdrs[1].text = 'Nom du concurrent'; hdrs[2].text = 'Montant (TTC)'
        for _, row in data.iterrows():
            cells = tab.add_row().cells
            cells[0].text, cells[1].text, cells[2].text = str(row['Rang']), str(row['Nom']), str(row['Montant'])
        
        p = doc.add_paragraph(f"\nLe président invite la société : {curr['Nom']} (moins disant) pour {curr['Montant']} Dhs TTC ({amt_words}) à confirmer son offre, ")
        p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True
    
    else:
        # المحاضر من 2 إلى 6
        prev_name = data.iloc[idx-1]['Nom']
        doc.add_paragraph(f"La commission constate que la société {prev_name} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_infructueux:
            # نص المحضر السادس في حالة "غير مثمر"
            doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :").alignment = WD_ALIGN_PARAGRAPH.CENTER
            res_p = doc.add_paragraph("INFRUCTUEUX")
            res_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            res_p.bold = True
        elif is_final:
            # نص الإسناد النهائي (سواء في المحضر 6 أو غيره)
            doc.add_paragraph(f"La commission constate que la société {curr['Nom']} a confirmé son offre.")
            p_final = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_words}).")
            p_final.bold = True
        else:
            # حالة استمرار المسطرة (التعليق والاستدعاء للموالي)
            p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} ({pv_num}éme rang) لتقديم تأكيدها، ")
            p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True

    # التوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل {pv_num} PV", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
