import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta
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

# القائمة الجانبية (لإدخال الأسماء)
st.sidebar.header("Membres de la Commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ Système de Gestion des PV - Commune Askaouen")

with st.expander("📝 Détails de la Procédure", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° Bon de commande", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication (Portail)", date(2026, 3, 25))
    obj_bc = st.text_area("Objet du BC", "Location d’une Tractopelle pour les travaux divers.")

st.subheader("📊 Liste des Soumissionnaires")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"}
])
data = st.data_editor(df_init, num_rows="dynamic", use_container_width=True)

st.divider()
c_date, c_hour, c_pv = st.columns(3)
reunion_date = c_date.date_input("Date de la séance actuelle", date.today())
reunion_hour = c_hour.text_input("Heure de la séance", "10h00mn")
pv_num = c_pv.selectbox("Numéro du PV:", [1, 2, 3, 4, 5])

# الأتمتة الزمنية: اليوم الموالي تلقائياً
next_rdv_auto = reunion_date + timedelta(days=1)
is_final = st.checkbox("✅ Marquer comme PV d'attribution finale")

if st.button("🚀 Générer le PV (Version Française)"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2)

    # Header en Français uniquement
    header = section.header
    htable = header.add_table(1, 1, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"

    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée Comme suit :")
    doc.add_paragraph(f"- {p_name} : Président de la commission\n- {d_name} : Directeur du service\n- {t_name} : Technicien de la commune")
    
    doc.add_paragraph(f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')} sur le portail des marchés publics, en application des dispositions de l’article 91 du décret n° 2-22-431 ( 8 mars 2023 ) relatif aux marchés publics, ayant pour objet : {obj_bc}").alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    idx = pv_num - 1
    
    if pv_num == 1:
        curr = data.iloc[0]
        amt_w = format_to_words_fr(curr['Montant'])
        doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires qui ont déposés leurs offres de prix électroniquement sont :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            row = tab.add_row().cells
            row[0].text, row[1].text, row[2].text = str(r['Rang']), str(r['Nom']), f"{r['Montant']} MAD"
        
        doc.add_paragraph("\nFormat papier : Néant.")
        doc.add_paragraph(f"Le président de la commission d’ouverture des plis invite la société : {curr['Nom']} est le moins disant pour un montant de {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre، et suspend la séance et fixe un rendez-vous le {next_rdv_auto.strftime('%d/%m/%Y')} ou sur invitation.")
    
    else:
        target_company = data.iloc[idx - 1]
        amt_w = format_to_words_fr(target_company['Montant'])

        if is_final:
            doc.add_paragraph(f"Après vérification du portail des marchés publics، la commission d’ouverture des plis constate que la société {target_company['Nom']} a confirmé son offre par lettre de confirmation.")
            p_res = doc.add_paragraph(f"Le président de la commission VALIDE la confirmation et ATTRIBUE le bon de commande à la société {target_company['Nom']} pour un montant de : {target_company['Montant']} Dhs TTC ({amt_w}).")
            p_res.bold = True
        else:
            doc.add_paragraph(f"Après vérification du portail des marchés publics، la commission d’ouverture des plis constate que la société {target_company['Nom']} n’a pas confirmé son offre par lettre de confirmation.")
            next_company = data.iloc[idx]
            doc.add_paragraph(f"Après écartement de la société {target_company['Nom']} le président invite la société : {next_company['Nom']} qui est classé le {idx+1}éme pour un montant de {next_company['Montant']} Dhs TTC ({format_to_words_fr(next_company['Montant'])}) à confirmer son offre le {next_rdv_auto.strftime('%d/%m/%Y')} ou sur invitation.")

    doc.add_paragraph(f"\nFait à Askaouen le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.rows[0].cells[0].text = "Le Président"; sig_tab.rows[0].cells[1].text = "Le Directeur"; sig_tab.rows[0].cells[2].text = "Le Technicien"
    sig_tab.rows[1].cells[0].text, sig_tab.rows[1].cells[1].text, sig_tab.rows[1].cells[2].text = p_name, d_name, t_name

    bio = BytesIO(); doc.save(bio)
    st.download_button(f"📥 Télécharger le PV {pv_num} (DOCX)", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
