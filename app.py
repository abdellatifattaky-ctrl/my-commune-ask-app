import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# Fonction de conversion des montants
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " PILE"
        return text
    except: return "________________"

st.set_page_config(page_title="Commune Askaouen - PV Officiel", layout="wide")

# Sidebar
st.sidebar.header("Membres de la commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ Générateur de PV - Commune d'Askaouen")

# Saisie des informations
with st.expander("📝 Informations du Dossier"):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2025")
    date_pub = c2.date_input("Date de publication", date(2025, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle pour les travaux divers.")

# Tableau
st.subheader("📊 Classement des Concurrents")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

# Options
pv_num = st.selectbox("Numéro du PV:", [1, 2, 3, 4, 5])
is_final = st.checkbox("✅ PV d'attribution finale ?")
reunion_date = st.date_input("Date de la séance", date.today())
reunion_hour = st.text_input("Heure", "10h00mn")
next_date = st.date_input("Prochain rendez-vous")

if st.button("🚀 Générer le PV avec Mise en Page"):
    doc = Document()
    
    # --- MISE EN PAGE (Margins & Paper Size) ---
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2)

    # En-tête
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c0 = htable.rows[0].cells[0].paragraphs[0]
    c0.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    c0.style.font.size = Pt(9)
    
    c1 = htable.rows[0].cells[1].paragraphs[0]
    c1.text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    c1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c1.style.font.size = Pt(10)

    # Titre
    doc.add_paragraph("\n")
    titre = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
    titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    st_titre = doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande")
    st_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st_titre.bold = True

    # Corps du texte
    obj_p = doc.add_paragraph(f"Objet : {obj_bc}")
    obj_p.paragraph_format.space_before = Pt(12)
    obj_p.runs[0].bold = True

    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission d’ouverture des plis composée Comme suit :")
    
    membres = doc.add_paragraph()
    membres.add_run(f"- {p_name}").bold = True
    membres.add_run(" : Président de la commission\n")
    membres.add_run(f"- {d_name}").bold = True
    membres.add_run(" : Directeur du service\n")
    membres.add_run(f"- {t_name}").bold = True
    membres.add_run(" : Technicien de la commune")

    p_intro = doc.add_paragraph(f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub} sur le portail des marchés publics, en application des dispositions de l’article 91 du décret n° 2-22-431 ( 8 mars 2023 ) relatif aux marchés publics, ayant pour objet : {obj_bc}")
    p_intro.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_intro.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    idx = pv_num - 1
    curr = data.iloc[idx]
    amt_w = format_to_words_fr(curr['Montant'])

    if pv_num == 1:
        doc.add_paragraph("Les soumissionnaires ayant déposé leurs offres électroniquement :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            rc = tab.add_row().cells
            rc[0].text, rc[1].text, rc[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        doc.add_paragraph(f"\nLe président invite la société : {curr['Nom']} (moins disant) pour {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre le {next_date}.")
    else:
        prev = data.iloc[idx - 1]
        doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission constate que la société {prev['Nom']} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_final:
            doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission constate que la société : {curr['Nom']} a confirmé son offre par lettre de confirmation.")
            res = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_w}).")
            res.runs[0].bold = True
        else:
            doc.add_paragraph(f"Après écartement de {prev['Nom']}, le président invite {curr['Nom']} ({pv_num}éme) pour {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre le {next_date}.")

    # --- SIGNATURES TABLE ---
    doc.add_paragraph(f"\nAskaouen le {date.today()}\n")
    sig_table = doc.add_table(rows=2, cols=3)
    sig_table.width = Inches(6.5)
    
    cells = sig_table.rows[0].cells
    cells[0].text = "Le Président"; cells[1].text = "Le Directeur"; cells[2].text = "Le Technicien"
    for cell in cells: cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    names = sig_table.rows[1].cells
    names[0].text = p_name; names[1].text = d_name; names[2].text = t_name
    for cell in names: 
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].bold = True

    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 Télécharger le PV avec Mise en Page", bio.getvalue(), f"PV_{pv_num}.docx")
