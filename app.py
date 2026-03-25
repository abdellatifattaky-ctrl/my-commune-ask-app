import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta # استيراد timedelta للحساب الزمني
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

st.title("🏛️ نظام صفقات جماعة أسكاون - أتمتة المواعيد")

with st.expander("📝 Détails Administratifs", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication", date(2026, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle.")

st.subheader("📊 Liste des concurrents")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"}
])
data = st.data_editor(df_init, use_container_width=True)

# --- ضبط التواريخ تلقائياً ---
st.divider()
col_date, col_hour, col_next = st.columns(3)

reunion_date = col_date.date_input("Date de la séance actuelle", date.today())
reunion_hour = col_hour.text_input("Heure", "10h00mn")

# حساب تاريخ اليوم الموالي تلقائياً
next_rdv_auto = reunion_date + timedelta(days=1)
col_next.info(f"📅 Prochain RDV (Auto): {next_rdv_auto.strftime('%d/%m/%Y')}")

pv_num = st.selectbox("Numéro du PV:", [1, 2, 3, 4, 5])
is_final = st.checkbox("✅ Est-ce le PV d'attribution finale ?")

if st.button("🚀 إنشاء المحضر (تاريخ آلي)"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée Comme suit :")
    doc.add_paragraph(f"- {p_name} : Président\n- {d_name} : D.S\n- {t_name} : Technicien")
    
    doc.add_paragraph(f"S’est réunie... en application des dispositions de l’article 91 du décret n° 2-22-431.")

    idx = pv_num - 1
    if pv_num == 1:
        curr = data.iloc[0]
        amt_w = format_to_words_fr(curr['Montant'])
        doc.add_paragraph("Après vérification du portail...")
        # استخدام التاريخ الموالي المحسوب آلياً هنا
        doc.add_paragraph(f"Le président invite la société : {curr['Nom']} (moins disant) à confirmer son offre، et suspend la séance et fixe un rendez-vous le {next_rdv_auto.strftime('%d/%m/%Y')} (soit le lendemain) ou sur invitation.")
    else:
        target_company = data.iloc[idx - 1]
        amt_w = format_to_words_fr(target_company['Montant'])
        if is_final:
            doc.add_paragraph(f"Après vérification... la société {target_company['Nom']} a confirmé son offre.")
            p_res = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le BC à {target_company['Nom']} pour {target_company['Montant']} Dhs TTC ({amt_w}).")
            p_res.bold = True
        else:
            doc.add_paragraph(f"Après vérification... la société {target_company['Nom']} n’a pas confirmé son offre.")
            next_company = data.iloc[idx]
            # استخدام التاريخ الموالي المحسوب آلياً هنا أيضاً
            doc.add_paragraph(f"Le président invite la société : {next_company['Nom']} ({idx+1}éme) à confirmer son offre le {next_rdv_auto.strftime('%d/%m/%Y')} أو بناءً على دعوة.")

    p_date = doc.add_paragraph(f"\nAskaouen le {reunion_date.strftime('%d/%m/%Y')}")
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    bio = BytesIO(); doc.save(bio)
    st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
