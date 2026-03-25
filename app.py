import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

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

st.set_page_config(page_title="Commune Askaouen - Système PV", layout="wide")

st.sidebar.header("Membres de la Commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ نظام استخراج المحاضر - جماعة أسكاون")

with st.expander("📝 Détails Administratifs", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication", date(2026, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle pour les travaux divers.")

# حصر الجدول في 5 شركات كحد أقصى قانونياً
st.subheader("📊 Liste des concurrents (Max 5 selon la loi)")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "SOCIETE 1", "Montant": "60000.00"},
    {"Rang": 2, "Nom": "SOCIETE 2", "Montant": "70000.00"},
    {"Rang": 3, "Nom": "SOCIETE 3", "Montant": "80000.00"},
    {"Rang": 4, "Nom": "SOCIETE 4", "Montant": "90000.00"},
    {"Rang": 5, "Nom": "SOCIETE 5", "Montant": "100000.00"}
])
data = st.data_editor(df_init, use_container_width=True, num_rows="fixed")

st.divider()
c_pv1, c_pv2, c_pv3 = st.columns(3)
# المحضر السادس هو محضر الحسم النهائي
pv_num = c_pv1.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
is_final = c_pv2.checkbox("✅ Est-ce le PV d'attribution finale ?", value=(True if pv_num == 6 else False))
reunion_date = c_pv3.date_input("Date de la séance", date.today())

reunion_hour = st.text_input("Heure", "10h00mn")
next_rdv = st.date_input("Prochain RDV (Si nécessaire)")

if st.button("🚀 إنشاء المحضر المنسق"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2)

    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis s'est réunie conformément à l'article 91 du décret 2-22-431.")

    idx = pv_num - 1
    # معالجة خاصة للمحضر السادس (نهاية المسطرة)
    if pv_num == 6:
        prev = data.iloc[4] # الشركة الخامسة والأخيرة
        doc.add_paragraph(f"Après avoir épuisé la liste des 5 concurrents autorisés par la loi, et suite au défaut de confirmation de la société {prev['Nom']}...")
        doc.add_paragraph("La commission procède à la clôture de la procédure conformément à la réglementation en vigueur.").bold = True
    else:
        curr = data.iloc[idx]
        amt_w = format_to_words_fr(curr['Montant'])
        if pv_num == 1:
            # (نفس منطق المحضر الأول...)
            doc.add_paragraph(f"Le président invite la société : {curr['Nom']} (moins disant) pour {curr['Montant']} Dhs TTC.")
        else:
            prev = data.iloc[idx - 1]
            doc.add_paragraph(f"La commission constate que la société {prev['Nom']} n’a pas confirmé son offre.")
            if is_final:
                doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le BC à la société {curr['Nom']} pour {curr['Montant']} Dhs TTC ({amt_w}).").bold = True

    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # قسم التوقيعات
    doc.add_paragraph("\nSignatures des membres :").bold = True
    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.rows[0].cells[0].text = "Le Président"; sig_tab.rows[0].cells[1].text = "Le Directeur"; sig_tab.rows[0].cells[2].text = "Le Technicien"
    sig_tab.rows[1].cells[0].text, sig_tab.rows[1].cells[1].text, sig_tab.rows[1].cells[2].text = p_name, d_name, t_name
    for r in sig_tab.rows:
        for c in r.cells: c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    bio = BytesIO(); doc.save(bio)
    st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
