import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date, timedelta

# --- دالة تحويل المبالغ (نسخة آمنة) ---
def dcm_to_words_fr(n):
    units = ["", "UN", "DEUX", "TROIS", "QUATRE", "CINQ", "SIX", "SEPT", "HUIT", "NEUF"]
    teens = ["DIX", "ONZE", "DOUZE", "TREIZE", "QUATORZE", "QUINZE", "SEIZE", "DIX-SEPT", "DIX-HUIT", "DIX-NEUF"]
    tens = ["", "", "VINGT", "TRENTE", "QUARANTE", "CINQUANTE", "SOIXANTE", "SOIXANTE-DIX", "QUATRE-VINGT", "QUATRE-VINGT-DIX"]
    def convert(n):
        if n < 10: return units[n]
        elif n < 20: return teens[n-10]
        elif n < 100: return tens[n//10] + ("-" + convert(n%10) if n%10 != 0 else "")
        elif n < 1000: return (units[n//100] if n//100 > 1 else "") + " CENT" + (" " + convert(n%100) if n%100 != 0 else "")
        elif n < 1000000: return (convert(n//1000) if n//1000 > 1 else "") + " MILLE" + (" " + convert(n%1000) if n%1000 != 0 else "")
        return str(n)
    try:
        val = int(float(str(n).replace(' ', '').replace(',', '')))
        return f"{convert(val)} DIRHAMS"
    except: return "________________"

st.set_page_config(page_title="Askaouen Pro", layout="wide")
st.title("🏛️ منظومة جماعة أسكاون - نسخة مصححة")

# --- اللجنة ---
with st.sidebar:
    st.header("👥 اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

# --- البيانات ---
with st.expander("📅 مراجع السند", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° BC", "01/ASK/2026")
    obj_bc = st.text_area("Objet", "Achat de fournitures...")

# --- الجدول ---
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# --- خيارات المحضر ---
pv_num = st.selectbox("رقم المحضر:", [1, 2, 3, 4, 5, 6])
reunion_date = st.date_input("تاريخ الجلسة", date.today())
is_final = st.checkbox("✅ إسناد نهائي")
if not is_final:
    next_date = st.date_input("الموعد القادم", date.today() + timedelta(days=1))

if st.button("🚀 إنشاء الملف"):
    if (pv_num - 1) >= len(data):
        st.error("خطأ: لا توجد شركة بهذا الترتيب في الجدول!")
    else:
        doc = Document()
        # الترويسة
        section = doc.sections[0]
        ht = section.header.add_table(1, 2, Inches(6.5))
        ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
        ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
        ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')}, la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

        idx = pv_num - 1
        curr = data.iloc[idx]
        amt_words = dcm_to_words_fr(curr['Montant'])

        if pv_num == 1:
            doc.add_paragraph("Après vérification du portail، soumissionnaires :")
            table = doc.add_table(rows=1, cols=3); table.style = 'Table Grid'
            for i, h in enumerate(['Rang', 'Nom', 'Montant']): table.rows[0].cells[i].text = h
            for _, r in data.iterrows():
                c = table.add_row().cells
                c[0].text, c[1].text, c[2].text = str(r['Rang']), str(r['Nom']), str(r['Montant'])
            
            p = doc.add_paragraph(f"\nLe président invite : {curr['Nom']} pour {curr['Montant']} Dhs ({amt_words}), ")
            p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True
        else:
            prev_name = data.iloc[idx-1]['Nom']
            doc.add_paragraph(f"La commission constate que la société {prev_name} n'a pas confirmé.")
            if is_final:
                doc.add_paragraph(f"Le président VALIDE et ATTRIBUE le BC à {curr['Nom']} بمبلغ {curr['Montant']} Dhs ({amt_words}).").bold = True
            else:
                p = doc.add_paragraph(f"Le président invite : {curr['Nom']} لتقديم تأكيدها، ")
                p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')}.").bold = True

        doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر", bio.getvalue(), f"PV_{pv_num}.docx")

st.info("البرنامج جاهز الآن.")
