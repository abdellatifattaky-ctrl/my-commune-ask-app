import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- وظيفة تحويل المبالغ (تفادياً للأخطاء السابقة) ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        return f"{words} DIRHAMS"
    except: return "________________"

st.set_page_config(page_title="Commune Askaouen - Système Invariable", layout="wide")

# --- 1. مدخلات الإدارة ---
with st.sidebar:
    st.header("👥 أعضاء اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📅 المراجع والتواريخ الإدارية", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de Publication (بوابة الصفقات)", date(2026, 3, 25))
    obj_bc = st.text_area("Objet (موضوع السند)", "Achat de fournitures...")

# --- 2. جدول الشركات ---
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# --- 3. اختيار نوع الوثيقة ---
doc_type = st.selectbox("إختر الوثيقة:", ["PV (المحاضر)", "Notification (التبليغ)", "Réception (الاستلام)"])

if doc_type == "PV (المحاضر)":
    col_pv, col_dt, col_nxt = st.columns(3)
    pv_num = col_pv.selectbox("رقم المحضر", [1, 2, 3, 4, 5, 6])
    reunion_date = col_dt.date_input("تاريخ الجلسة", date.today())
    
    is_final = False
    if pv_num < 6:
        is_final = st.checkbox(f"✅ إسناد نهائي للشركة رقم {pv_num}")
        if not is_final:
            next_date = col_nxt.date_input("تاريخ الموعد القادم", date.today() + timedelta(days=1))
    else:
        res_6 = st.radio("نتيجة المحضر 6:", ["Attribution", "Infructueux"])
        is_final = (res_6 == "Attribution")

# --- 4. توليد الوثائق بنصوصك الحرفية ---
if st.button("🚀 إنشاء الوثيقة الرسمية"):
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
        doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')}, la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

        idx = pv_num - 1
        curr = data.iloc[idx]
        amt_w = format_to_words_fr(curr['Montant'])

        if pv_num == 1:
            # نصك الحرفي للمحضر الأول
            p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} (moins disant) pour un montant de {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre, ")
            p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True
        else:
            prev_name = data.iloc[idx-1]['Nom']
            doc.add_paragraph(f"La commission constate que la société {prev_name} n’a pas confirmé son offre par lettre de confirmation.")
            
            if is_final:
                # نصك الحرفي للإسناد النهائي
                doc.add_paragraph(f"La commission constate que la société {curr['Nom']} a confirmé son offre.")
                p_res = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_w}).")
                p_res.bold = True
            else:
                # نصك الحرفي للاستدعاء والتعليق
                p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} ({pv_num}éme rang) لتقديم تأكيدها، ")
                p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True

    elif doc_type == "Notification (التبليغ)":
        doc.add_heading("LETTRE DE NOTIFICATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nAskaouen, le {date.today().strftime('%d/%m/%Y')}")
        doc.add_paragraph(f"Objet: Notification du BC n° {num_bc} (Publié le {date_pub.strftime('%d/%m/%Y')})")
        doc.add_paragraph(f"\nJ'ai l'honneur de vous informer que votre offre a été retenue...")

    elif doc_type == "Réception (الاستلام)":
        doc.add_heading("PROCÈS VERBAL DE RÉCEPTION DÉFINITIVE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le {date.today().strftime('%d/%m/%Y')}, la commission a procédé à la réception des prestations...")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل الوثيقة الرسمية", bio.getvalue(), "Document_Askaouen.docx")
