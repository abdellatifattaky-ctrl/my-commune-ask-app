import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# --- 1. التنسيق الجمالي (Lacoste Style) ---
st.set_page_config(page_title="Commune Askaouen - Système Expert", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #004526 !important; }
    .stButton>button {
        background-color: #004526;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

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
st.title("🏛️ المنظومة الإدارية لأسكاون: سندات الطلب")

with st.sidebar:
    st.header("👥 لجنة فتح الأظرفة")
    p_name = st.text_input("Président de la commission", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur du service", "M BAREK BAK")
    t_name = st.text_input("Technicien de la commune", "ABDELLATIF ATTAKY")

with st.expander("📝 المعطيات التقنية والقانونية", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° Bon de Commande", "01/ASK/2026")
    date_pub = col2.date_input("Date de publication sur le portail", date(2026, 3, 25))
    obj_bc = st.text_area("Objet (Tel qu'il figure sur l'avis)")

st.subheader("📊 عروض المتنافسين")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

st.divider()

# اختيار نوع المستند
doc_type = st.radio("إختر نوع الوثيقة الرسمية:", 
    ["Procès-verbaux d'ouverture (1 à 6)", "Notification (التبليغ)", "Réception (الاستلام)"], horizontal=True)

if doc_type == "Procès-verbaux d'ouverture (1 à 6)":
    c1, c2, c3 = st.columns(3)
    pv_num = c1.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
    reunion_date = c2.date_input("Date de la séance", date.today())
    reunion_hour = c3.text_input("Heure de la séance", "10h00mn")
    
    is_infructueux = False
    is_final_attr = False
    if pv_num == 6:
        res_6 = st.radio("Résultat du 6éme PV:", ["Attribution (إسناد)", "Infructueux (غير مثمر)"])
        is_infructueux = (res_6 == "Infructueux (غير مثمر)")
        is_final_attr = not is_infructueux
    else:
        is_final_attr = st.checkbox("✅ Marquer comme PV d'Attribution Finale")

# --- 3. محرك توليد المستندات (DOCX Engine) ---
if st.button("✨ استخراج الوثيقة الرسمية"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2)

    # الترويسة الموحدة
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    if doc_type == "Procès-verbaux d'ouverture (1 à 6)":
        doc.add_paragraph("\n")
        doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée comme suit :")
        doc.add_paragraph(f"- M. {p_name} : Président de la commission\n- M. {d_name} : Directeur du service\n- M. {t_name} : Technicien de la commune")
        
        doc.add_paragraph(f"S’est réunie dans la salle de réunion de la commune sur invitation du président concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')} sur le portail des marchés publics, en application des dispositions de l’article 91 du décret n° 2-22-431 (8 mars 2023) relatif aux marchés publics, ayant pour objet : {obj_bc}")

        if pv_num == 1:
            doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires qui ont déposé leurs offres de prix électroniquement sont :")
            tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
            hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
            for _, r in data.iterrows():
                row = tab.add_row().cells
                row[0].text, row[1].text, row[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
            curr = data.iloc[0]
            amt_w = format_to_words_fr(curr['Montant'])
            doc.add_paragraph(f"\nLe président de la commission invite la société : {curr['Nom']} est le moins disant pour un montant de {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre, وsuspend la séance.")
        
        else:
            idx = pv_num - 1 if pv_num <= 5 else 4
            prev_company = data.iloc[idx-1]['Nom']
            doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission constate que la société {prev_company} n’a pas confirmé son offre par lettre de confirmation.")
            
            if is_infructueux:
                p_inf = doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :")
                p_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                res_inf = doc.add_paragraph("INFRUCTUEUX")
                res_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                res_inf.bold = True; res_inf.runs[0].font.size = Pt(16)
            
            elif is_final_attr:
                curr = data.iloc[idx]
                amt_w = format_to_words_fr(curr['Montant'])
                doc.add_paragraph(f"La commission constate que la société : {curr['Nom']} a confirmé son offre par lettre de confirmation.")
                p_res = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_w}).")
                p_res.bold = True
            
            else:
                curr = data.iloc[idx]
                amt_w = format_to_words_fr(curr['Montant'])
                doc.add_paragraph(f"Après écartement de la société {prev_company}, le président invite la société : {curr['Nom']} qui est classé le {pv_num}éme pour un montant de {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre.")

    elif doc_type == "Notification (التبليغ)":
        winner = data.iloc[0] # افتراضياً الأول، يمكن تعديله
        doc.add_heading("LETTRE DE NOTIFICATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nObjet : Notification de l'attribution du BC n° {num_bc}")
        doc.add_paragraph(f"À Monsieur le Gérant de la société {winner['Nom']}")
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer que votre offre pour {obj_bc} a été retenue pour un montant de {winner['Montant']} MAD TTC.")

    elif doc_type == "Réception (الاستلام)":
        doc.add_heading("PROCÈS VERBAL DE RÉCEPTION DÉFINITIVE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nLe {date.today().strftime('%d/%m/%Y')}, la commission a procédé à la réception des prestations du BC n° {num_bc} exécuté par la société retenue.")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO(); doc.save(bio)
    st.download_button(f"📥 تحميل {doc_type}", bio.getvalue(), f"{doc_type}.docx")
