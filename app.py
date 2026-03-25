import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# --- 1. التنسيق الجمالي (Lacoste Style) ---
st.set_page_config(page_title="Commune Askaouen - Système PV", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #004526 !important; }
    .stButton>button {
        background-color: #004526;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# دالة تحويل الأرقام لحروف
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

# --- 2. الواجهة الرئيسية ---
st.title("🏛️ نظام تدبير سندات الطلب - جماعة أسكاون")

with st.sidebar:
    st.header("Membres de la Commission")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📝 Détails Administratifs", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° BC", "01/ASK/2026")
    date_pub = col2.date_input("Date de publication", date(2026, 3, 25))
    obj_bc = st.text_area("Objet", "Achat de fournitures...")

st.subheader("📊 Liste des concurrents (Max 5)")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

st.divider()

col_pv, col_date, col_hour = st.columns(3)
pv_num = col_pv.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
reunion_date = col_date.date_input("Date de la séance", date.today())
reunion_hour = col_hour.text_input("Heure", "10h00mn")

# منطق المحضر السادس
is_infructueux = False
is_final_attr = False
if pv_num == 6:
    res_6 = st.radio("Résultat du 6éme PV:", ["Attribution (إسناد الشركة 5)", "B.C Infructueux (غير مثمر)"])
    if res_6 == "B.C Infructueux (غير مثمر)": is_infructueux = True
    else: is_final_attr = True
else:
    is_final_attr = st.checkbox("✅ PV d'attribution finale")

if st.button("🚀 إنشاء المحضر النهائي"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    
    # الترويسة
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")
    title = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # المتن بالأمانة النصية الفرنسية
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

    idx = pv_num - 1 if pv_num <= 5 else 4
    if pv_num == 1:
        doc.add_paragraph("Après vérification du portail, les soumissionnaires sont :")
        # (رسم الجدول...)
        curr = data.iloc[0]
        doc.add_paragraph(f"Le président invite la société {curr['Nom']} (moins disant) à confirmer son offre.")
    else:
        prev_name = data.iloc[idx-1]['Nom']
        doc.add_paragraph(f"La commission constate que la société {prev_name} n’a pas confirmé son offre.")
        
        if is_infructueux:
            p = doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            inf = doc.add_paragraph("INFRUCTUEUX")
            inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            inf.bold = True
        elif is_final_attr:
            curr = data.iloc[idx]
            amt_w = format_to_words_fr(curr['Montant'])
            doc.add_paragraph(f"La commission VALIDE la confirmation et ATTRIBUE le BC à la société {curr['Nom']} pour {curr['Montant']} Dhs TTC ({amt_w}).").bold = True

    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
