import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import date

# ... (الكود السابق يبقى كما هو، فقط نضيف خيار "Avis d'achat" في القائمة)

option = st.selectbox("Sélectionner le type de document :", 
                     ["1er PV : Ouverture et Classement", 
                      "2ème/3ème PV : Écartement et Invitation du suivant", 
                      "4ème PV : Validation et Attribution finale",
                      "Avis d'achat sur Bons de Commande"])

if option == "Avis d'achat sur Bons de Commande":
    st.subheader("Configuration de l'Avis d'achat")
    with st.form("avis_form"):
        num_avis = st.text_input("N° Avis d'achat", "03/ASK/2025")
        objet_avis = st.text_input("Objet de la prestation", "Station de pompage et relevage")
        delai = st.text_input("Délai d'exécution (jours)", "10")
        date_limite = st.date_input("Date limite de réception des devis")
        
        st.write("Détails des prestations (Tableau) :")
        items_data = st.text_area("Entrez les articles (Désignation;Unité;Quantité)", 
                                  help="Exemple: Pompe solaire;U;1\nConduite PN 16;ML;50")
        
        submitted_avis = st.form_submit_button("Générer l'Avis d'achat")

        if submitted_avis:
            doc = Document()
            
            # الترويسة الرسمية (Header مزدوج)
            header = doc.add_table(rows=1, cols=2)
            header.allow_autofit = True
            
            # جهة اليمين (العربية)
            right_cell = header.rows[0].cells[1]
            p_ar = right_cell.add_paragraph("المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nدائرة تالوين\nجماعة أسكاون")
            p_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            # جهة اليسار (الفرنسية)
            left_cell = header.rows[0].cells[0]
            p_fr = left_cell.add_paragraph("ROYAUME DU MAROC\nMINISTERE DE L’INTERIEUR\nPROVINCE DE TAROUDANTE\nCERCLE DE TALIOUINE\nCOMMUNE D’ASKAOUN")
            p_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT

            # العنوان الرئيسي
            doc.add_paragraph("\n")
            title = doc.add_heading(f"AVIS D’ACHAT SUR BONS DE COMMANDE N° {num_avis}", 1)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph(f"Objet de la prestation : {objet_avis}").bold = True
            
            # الجدول التقني
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'N°'
            hdr_cells[1].text = 'Désignation des prestations'
            hdr_cells[2].text = 'Unité'
            hdr_cells[3].text = 'Quantité'

            i = 1
            for line in items_data.split('\n'):
                if ';' in line:
                    desc, unit, qty = line.split(';')
                    row = table.add_row().cells
                    row[0].text = str(i)
                    row[1].text = desc
                    row[2].text = unit
                    row[3].text = qty
                    i += 1

            doc.add_paragraph(f"\n- Lieu d'exécution : la commune d'Askaoun.")
            doc.add_paragraph(f"- Délai d'exécution : {delai} jours.")
            doc.add_paragraph(f"- Date limite de réception : {date_limite}.")
            doc.add_paragraph(f"- Les plis sont déposés électroniquement sur : www.marchespublics.gov.ma")

            doc.add_paragraph(f"\nASKAOUN LE : {date.today()}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_paragraph("Le Président de la commune").alignment = WD_ALIGN_PARAGRAPH.RIGHT

            bio = BytesIO()
            doc.save(bio)
            st.success("✅ Avis d'achat généré !")
            st.download_button("📥 Télécharger l'Avis (.docx)", bio.getvalue(), f"Avis_{num_avis.replace('/','_')}.docx")
