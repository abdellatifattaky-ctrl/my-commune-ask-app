import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta # لإضافة الـ 24 ساعة
from num2words import num2words

def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else: text += " ,00 CTS"
        return text
    except: return "________________"

st.set_page_config(page_title="Gestion des BC - Askaouen", layout="wide")

# القائمة الجانبية للجنة
st.sidebar.header("⚖️ Commission d'Ouverture")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ نظام تدبير سندات الطلب - جماعة أسكاون")

with st.expander("📝 المعطيات الإدارية (Détails Administratifs)", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication", date(2026, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle.")

# جدول المتنافسين
st.subheader("📊 Liste des concurrents")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"}
])
data = st.data_editor(df_init, num_rows="dynamic", use_container_width=True)

# إعدادات المحضر والوقت
st.divider()
c3, c4, c5 = st.columns(3)
pv_num = c3.selectbox("Numéro du PV:", [1, 2, 3, 4, 5])
reunion_date = c4.date_input("Date de la séance actuelle", date.today())
is_final = c5.checkbox("✅ Est-ce le PV d'attribution finale ?")

# احتساب أجل 24 ساعة تلقائياً للجلسة القادمة
suggested_next = reunion_date + timedelta(days=1)
next_rdv = st.date_input("Date de la prochaine séance (Min +24h)", suggested_next)

if st.button("🚀 إنشاء المحضر المنسق"):
    doc = Document()
    section = doc.sections[0]
    
    # الترويسة
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_paragraph("\n")
    title = doc.add_paragraph(f"{pv_num}ème PROCES VERBAL")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True; title.runs[0].font.size = Pt(14)

    doc.add_paragraph(f"OBJET : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')}, la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

    idx = pv_num - 1
    if idx < len(data):
        curr = data.iloc[idx]
        amt_w = format_to_words_fr(curr['Montant'])

        if pv_num == 1:
            # محضر فتح الأظرفة الأول
            doc.add_paragraph("Après examen des offres électroniques، les soumissionnaires sont classés comme suit :")
            tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
            for i, h in enumerate(['Rang', 'Concurrent', 'Montant']): tab.rows[0].cells[i].text = h
            for _, r in data.iterrows():
                row = tab.add_row().cells
                row[0].text, row[1].text, row[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
            
            doc.add_paragraph(f"\nLe président invite la société {curr['Nom']} à confirmer son offre. La séance est suspendue et reprendra le {next_rdv.strftime('%d/%m/%Y')} (respectant le délai de 24h).")
        
        else:
            # محاضر الاستمرار أو الإسناد
            prev = data.iloc[idx - 1]
            doc.add_paragraph(f"La commission constate le défaut de confirmation par la société {prev['Nom']}.")
            
            if is_final:
                # جملة الإسناد النهائي (لا تتكرر في المحاضر الأخرى)
                p_attr = doc.add_paragraph()
                p_attr.add_run(f"Considérant la confirmation reçue، la commission VALIDE l'offre et ATTRIBUE définitivement le bon de commande à la société {curr['Nom']} pour un montant de {curr['Montant']} DHS TTC ({amt_w}).").bold = True
            else:
                doc.add_paragraph(f"En conséquence، le président invite le concurrent suivant {curr['Nom']} à confirmer son offre sous 24h، soit le {next_rdv.strftime('%d/%m/%Y')}.")

    # التواقيع
    doc.add_paragraph(f"\nAskaouen، le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.rows[0].cells[0].text = "Le Président"; sig_tab.rows[0].cells[1].text = "Le Directeur"; sig_tab.rows[0].cells[2].text = "Le Technicien"
    sig_tab.rows[1].cells[0].text, sig_tab.rows[1].cells[1].text, sig_tab.rows[1].cells[2].text = p_name, d_name, t_name

    bio = BytesIO(); doc.save(bio)
    st.download_button("📥 تحميل المحضر المطور", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
