import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- 1. الإعدادات والوظائف المساعدة ---
st.set_page_config(page_title="Askaouen Pro - Control Panel", layout="wide")

def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0: text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else: text += " ,00CTS"
        return text
    except: return "________________"

# --- 2. نصوص المحاضر (القوالب الثابتة) - غيرها من هنا كما تريد ---
txt_header_fr = "De la commission d’ouverture des plis\nProcédure Bon de commande"
txt_loi_art91 = "la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431."

# جملة التعليق والاستدعاء (تعدل هنا مرة واحدة لتتغير في كل الكود)
txt_suspendre = "et suspend la séance et fixe un rendez-vous le {next_date} ou sur invitation."

# جملة الإسناد النهائي
txt_attribution_finale = "Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {nom_ste} pour un montant de : {montant} Dhs TTC ({montant_lettres})."

# جملة استبعاد الشركة السابقة
txt_ecartement = "Après vérification du portail des marchés publics, la commission constate que la société {prev_ste} n’a pas confirmé son offre par lettre de confirmation."

# --- 3. واجهة المستخدم ---
st.title("🏛️ لوحة التحكم في نصوص المحاضر - جماعة أسكاون")

with st.sidebar:
    st.header("👤 أعضاء اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📝 معلومات سند الطلب", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° BC", "01/ASK/2026")
    obj_bc = st.text_area("Objet", "Achat de fournitures...")

data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

col_v1, col_v2, col_v3 = st.columns(3)
pv_num = col_v1.selectbox("رقم المحضر:", [1, 2, 3, 4, 5, 6])
reunion_date = col_v2.date_input("تاريخ الجلسة", date.today())

is_final = False
if pv_num == 6:
    res_6 = st.radio("النتيجة:", ["Attribution", "Infructueux"])
    is_final = (res_6 == "Attribution")
else:
    is_final = st.checkbox(f"✅ إسناد نهائي للشركة رقم {pv_num}")
    if not is_final:
        next_dt = col_v3.date_input("موعد الجلسة القادمة", date.today() + timedelta(days=1))

# --- 4. معالج المستند ---
if st.button("🚀 إنشاء المستند"):
    doc = Document()
    # (الترويسة...)
    section = doc.sections[0]
    header = section.header
    ht = header.add_table(1, 2, Inches(6.5))
    ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(txt_header_fr).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à 10h00mn, {txt_loi_art91}")

    idx = pv_num - 1
    curr = data.iloc[idx]
    amt_words = format_to_words_fr(curr['Montant'])

    if pv_num == 1:
        p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} (moins disant) pour {curr['Montant']} Dhs TTC ({amt_words}) à confirmer son offre, ")
        p.add_run(txt_suspendre.format(next_date=next_dt.strftime('%d/%m/%Y'))).bold = True
    else:
        prev_ste = data.iloc[idx-1]['Nom']
        doc.add_paragraph(txt_ecartement.format(prev_ste=prev_ste))
        
        if is_final:
            doc.add_paragraph(f"La commission constate que la société {curr['Nom']} a confirmé son offre.")
            p_res = doc.add_paragraph(txt_attribution_finale.format(nom_ste=curr['Nom'], montant=curr['Montant'], montant_lettres=amt_words))
            p_res.bold = True
        else:
            p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} ({pv_num}éme rang) pour {curr['Montant']} Dhs TTC ({amt_words}) à confirmer son offre, ")
            p.add_run(txt_suspendre.format(next_date=next_dt.strftime('%d/%m/%Y'))).bold = True

    # التوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل المحضر {pv_num}", bio.getvalue(), f"PV_{pv_num}.docx")
