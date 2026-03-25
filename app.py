import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة تحويل المبالغ ---
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

# --- إعدادات الصفحة وحفظ الأسماء ---
st.set_page_config(page_title="Commune Askaouen - Système PV", layout="wide")

if 'p_name' not in st.session_state: st.session_state.p_name = "MOHAMED ZILALI"
if 'd_name' not in st.session_state: st.session_state.d_name = "M BAREK BAK"
if 't_name' not in st.session_state: st.session_state.t_name = "ABDELLATIF ATTAKY"

st.sidebar.header("Membres de la Commission")
st.session_state.p_name = st.sidebar.text_input("Président", st.session_state.p_name)
st.session_state.d_name = st.sidebar.text_input("Directeur du service", st.session_state.d_name)
st.session_state.t_name = st.sidebar.text_input("Technicien", st.session_state.t_name)

st.title("🏛️ نظام استخراج المحاضر - جماعة أسكاون")

with st.expander("📝 Détails Administratifs", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2026")
    date_pub = c2.date_input("Date de publication", date(2025, 3, 25))
    obj_bc = st.text_area("Objet", "Achat de matériel...")

# جدول الشركات الخمس
st.subheader("📊 Liste des concurrents")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True, num_rows="dynamic")

st.divider()
c_pv1, c_pv2, c_pv3 = st.columns(3)
pv_num = c_pv1.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
reunion_date = c_pv3.date_input("Date de la séance", date.today())
reunion_hour = st.text_input("Heure", "10h00mn")

is_infructueux = False
is_final_attr = False
if pv_num == 6:
    res_6 = st.radio("Résultat du 6éme PV:", ["Attribution (إسناد)", "B.C Infructueux (غير مثمر)"])
    is_infructueux = (res_6 == "B.C Infructueux (غير مثمر)")
    is_final_attr = (res_6 == "Attribution (إسناد)")
else:
    is_final_attr = c_pv2.checkbox("✅ Est-ce le PV d'attribution finale ?")

# --- التنفيذ الرئيسي ---
if st.button("🚀 إنشاء المحضر رقم " + str(pv_num)):
    doc = Document()
    section = doc.sections[0]
    
    # Header
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العناوين
    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # بيانات اللجنة
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée comme suit :")
    doc.add_paragraph(f"- M. {st.session_state.p_name} : Président de la commission\n- M. {st.session_state.d_name} : Directeur du service\n- M. {st.session_state.t_name} : Technicien de la commune")
    
    doc.add_paragraph(f"S’est réunie... BC n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')}...")

    # --- المنطق الحرفي للنصوص ---
    if pv_num == 1:
        doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires... sont :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            row = tab.add_row().cells
            row[0].text, row[1].text, row[2].text = str(r['Rang']), str(r['Nom']), f"{r['Montant']} MAD"
        
        curr_company = data.iloc[0]['Nom']
        curr_amount = data.iloc[0]['Montant']
        amt_w = format_to_words_fr(curr_amount)
        doc.add_paragraph(f"\nAprès examen des offres... invite la société : {curr_company} (moins disant) pour {curr_amount} Dhs TTC ({amt_w}).")

    else:
        # حساب الفهارس بدقة
        idx = min(pv_num - 1, len(data) - 1)
        prev_idx = idx - 1
        prev_co = data.iloc[prev_idx]['Nom']
        curr_co = data.iloc[idx]['Nom']
        curr_amt = data.iloc[idx]['Montant']
        amt_w = format_to_words_fr(curr_amt)

        if is_infructueux:
            doc.add_paragraph(f"Après vérification... la commission constate que la société {curr_co} n’a pas confirmé...")
            doc.add_paragraph("INFRUCTUEUX").bold = True
        elif is_final_attr:
            doc.add_paragraph(f"Après vérification... la commission constate que la société {curr_co} a confirmé...")
            doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr_co} pour : {curr_amt} Dhs TTC ({amt_w}).").bold = True
        else:
            # نص الاستبعاد الحرفي للمحاضر الوسطى
            doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission constate que la société {prev_co} n’a pas confirmé son offre par lettre de confirmation.")
            doc.add_paragraph(f"Après écartement de la société {prev_co}, le président de la commission invite la société : {curr_co} qui est classé le {pv_num}éme pour un montant de {curr_amt} Dhs TTC ({amt_w}) à confirmer son offre par lettre de confirmation.")

    # التوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sig_tab = doc.add_table(rows=1, cols=3)
    sig_tab.rows[0].cells[0].text = st.session_state.p_name
    sig_tab.rows[0].cells[1].text = st.session_state.d_name
    sig_tab.rows[0].cells[2].text = st.session_state.t_name

    bio = BytesIO(); doc.save(bio)
    st.download_button(f"📥 تحميل المحضر {pv_num}", bio.getvalue(), f"PV_{pv_num}.docx")
    st.success("جاهز للتحميل!")
