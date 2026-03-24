import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# دالة تحويل المبالغ إلى حروف فرنسية
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ,00CTS"
        return text
    except: return "________________"

st.set_page_config(page_title="Commune Askaouen - PV App", layout="wide")

# القائمة الجانبية
st.sidebar.header("اللجنة الإدارية")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ نظام توليد المحاضر - جماعة أسكاون")

# إدخال البيانات
with st.expander("📝 معلومات الملف"):
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
is_final = st.checkbox("✅ هل هذا هو محضر الإسناد النهائي (Attribution)؟")
reunion_date = st.date_input("تاريخ اجتماع اليوم", date.today())
reunion_hour = st.text_input("الساعة", "12h00mn")
next_rdv = st.date_input("موعد الجلسة القادمة")

if st.button("🚀 توليد المحضر الآن"):
    doc = Document()
    header = doc.sections[0].header
    htable = header.add_table(1, 2, Inches(6))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission d’ouverture des plis composée comme suit :")
    doc.add_paragraph(f"- {p_name} : Président de la commission\n- {d_name} : Directeur du service\n- {t_name} : Technicien de la commune")
    
    doc.add_paragraph(f"S’est réunie... concernant l’avis n° {num_bc} publié le : {date_pub}...")

    idx = pv_num - 1
    current_co = data.iloc[idx]

    if pv_num == 1:
        doc.add_paragraph("Les soumissionnaires (Top 5) :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        for _, r in data.iterrows():
            row = tab.add_row().cells
            row[0].text, row[1].text, row[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        amt_w = format_to_words_fr(current_co['Montant'])
        doc.add_paragraph(f"\nLe président invite {current_co['Nom']} pour {current_co['Montant']} DH ({amt_w}) à confirmer son offre le {next_rdv}.")
    else:
        prev_co = data.iloc[idx - 1]
        # الجملة التي طلبتها بدقة:
        doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société {prev_co['Nom']} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_final:
            doc.add_paragraph(f"Après vérification... la commission constate que la société : {current_co['Nom']} a confirmé son offre par lettre de confirmation.")
            amt_w = format_to_words_fr(current_co['Montant'])
            p_final = doc.add_paragraph(f"Le رئيس VALIDE la confirmation et ATTRIBUE le bon de commande à {current_co['Nom']} pour {current_co['Montant']} DH ({amt_w}).")
            p_final.bold = True
        else:
            amt_w = format_to_words_fr(current_co['Montant'])
            doc.add_paragraph(f"Le رئيس invite {current_co['Nom']} ({pv_num}éme) pour {current_co['Montant']} DH ({amt_w}) à confirmer son offre le {next_rdv}.")

    doc.add_paragraph(f"\nAskaouen le {date.today()}\n")
    sig = doc.add_paragraph(f"{p_name}             {d_name}             {t_name}")
    sig.alignment = WD_ALIGN_PARAGRAPH.CENTER

    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل ملف Word", bio.getvalue(), f"PV_{pv_num}.docx")
