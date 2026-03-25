import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- الوظيفة القانونية لتحويل المبالغ ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        return f"{num2words(val, lang='fr').upper()} DIRHAMS"
    except: return "________________"

st.set_page_config(page_title="Système BC Askaouen", layout="wide")

# --- المدخلات الجانبية ---
with st.sidebar:
    st.header("👤 لجنة فتح الأظرفة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

# --- المراجع والتواريخ ---
with st.expander("📝 المعطيات الإدارية (النشر والتبليغ)", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° BC", "01/ASK/2026")
    date_pub = col2.date_input("Date de Publication (Portail)", date(2026, 3, 25))
    obj_bc = st.text_area("Objet (موضوع السند)", "Achat de fournitures...")

# --- جدول المتنافسين ---
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# --- اختيار نوع الوثيقة ---
doc_type = st.selectbox("إختر الوثيقة:", ["PV (المحاضر)", "Notification", "Ordre de Service", "Réception"])

if doc_type == "PV (المحاضر)":
    c_pv, c_dt, c_nxt = st.columns(3)
    pv_num = c_pv.selectbox("رقم المحضر", [1, 2, 3, 4, 5, 6])
    reunion_date = c_dt.date_input("تاريخ الجلسة", date.today())
    is_final = False
    if pv_num < 6:
        is_final = st.checkbox(f"✅ إسناد نهائي في هذا المحضر (PV {pv_num})")
        if not is_final:
            next_date = c_nxt.date_input("تاريخ الموعد القادم", date.today() + timedelta(days=1))
    else:
        res_6 = st.radio("نتيجة المحضر 6:", ["Attribution", "Infructueux"])
        is_final = (res_6 == "Attribution")

# --- زر التنفيذ ---
if st.button("🚀 استخراج الوثيقة الرسمية"):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    ht = header.add_table(1, 2, Inches(6.5))
    ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    if doc_type == "PV (المحاضر)":
        doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        
        # جملة الاجتماع الرسمية
        doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à 10h00mn, la commission composée de M. {p_name}, M. {d_name} et M. {t_name} s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

        idx = pv_num - 1
        if pv_num == 1:
            doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires sont :")
            # إدراج جدول المتنافسين
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Nom du concurrent', 'Montant TTC'
            for _, row in data.iterrows():
                row_cells = table.add_row().cells
                row_cells[0].text, row_cells[1].text, row_cells[2].text = str(row['Rang']), str(row['Nom']), str(row['Montant'])
            
            curr = data.iloc[0]
            p = doc.add_paragraph(f"\nLe président invite la société : {curr['Nom']} (moins disant) لتقديم تأكيد عرضها بمبلغ {curr['Montant']} Dhs TTC ({format_to_words_fr(curr['Montant'])}), ")
            p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True
        
        else:
            prev_name = data.iloc[idx-1]['Nom']
            curr = data.iloc[idx]
            doc.add_paragraph(f"La commission constate que la société {prev_name} n'a pas confirmé son offre.")
            if is_final:
                doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le BC à la société {curr['Nom']} لكونها صاحبة العرض الموالي المقبول بمبلغ {curr['Montant']} Dhs TTC ({format_to_words_fr(curr['Montant'])}).").bold = True
            else:
                p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} ({pv_num}éme rang) لتقديم تأكيد عرضها، ")
                p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True

    elif doc_type == "Notification":
        doc.add_heading("LETTRE DE NOTIFICATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nObjet: Notification du BC n° {num_bc} (Publié le {date_pub.strftime('%d/%m/%Y')})")
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer...")

    elif doc_type == "Réception":
        doc.add_heading("PV DE RECEPTION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le {date.today().strftime('%d/%m/%Y')}, la commission a procédé à la réception...")

    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل المستند النهائي", bio.getvalue(), f"Document_Askaouen_{doc_type}.docx")
