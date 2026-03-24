import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة تحويل المبالغ إلى حروف فرنسية بدقة ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ,00CTS"
        return text
    except: return "________________"

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Commune Askaouen - Système de Gestion", layout="wide")

# --- القائمة الجانبية (الأعضاء والخيارات) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Coat_of_arms_of_Morocco.svg/1200px-Coat_of_arms_of_Morocco.svg.png", width=100)
st.sidebar.header("Membres de la Commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.sidebar.divider()
st.sidebar.info("Générateur Officiel - Commune d'Askaouen")

# --- واجهة التطبيق الرئيسية ---
st.title("🏛️ نظام التدبير الإداري - جماعة أسكاون")
st.subheader("إدارة سندات الطلب (Bons de Commande)")

with st.expander("📝 معلومات سند الطلب", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° Bon de commande", "01/ASK/2025")
    date_pub = col2.date_input("Date de publication sur le portail", date(2025, 3, 25))
    obj_bc = st.text_area("Objet de la prestation", "Location d’une Tractopelle pour les travaux divers.")

# --- جدول المتنافسين ---
st.subheader("📊 قائمة المتنافسين")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True, num_rows="fixed")

# --- خيارات الاستخراج ---
st.divider()
c1, c2, c3 = st.columns(3)
pv_num = c1.selectbox("رقم المحضر المطلوب:", [1, 2, 3, 4, 5])
is_final = c2.checkbox("✅ محضر الإسناد النهائي (Attribution)")
reunion_date = c3.date_input("تاريخ الاجتماع", date.today())
reunion_hour = st.text_input("الساعة", "10h00mn")
next_rdv = st.date_input("موعد الجلسة القادمة")

if st.button("🚀 توليد المستند المنسق (Word)"):
    doc = Document()
    
    # --- Mise en page (Margins) ---
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.5)
    section.left_margin, section.right_margin = Cm(2.5), Cm(2)

    # --- الترويسة المقلوبة (Header) ---
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    # اليسار (فرنسي)
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    c_fr.style.font.size = Pt(9)
    # اليمين (عربي)
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_ar.style.font.size = Pt(10)

    # --- العنوان ---
    doc.add_paragraph("\n")
    title = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- المتن ---
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    
    # الجملة الأولى المطلوبة
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée Comme suit :")
    doc.add_paragraph(f"- {p_name} : Président de la commission\n- {d_name} : Directeur du service\n- {t_name} : Technicien de la commune")
    
    p_loi = doc.add_paragraph(f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')} sur le portail des marchés publics, en application des dispositions de l’article 91 du décret n° 2-22-431 ( 8 mars 2023 ) relatif aux marchés publics, ayant pour objet : {obj_bc}")
    p_loi.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    idx = pv_num - 1
    curr = data.iloc[idx]
    amt_words = format_to_words_fr(curr['Montant'])

    if pv_num == 1:
        doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires qui ont déposés leurs offres de prix électroniquement sont :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            row = tab.add_row().cells
            row[0].text, row[1].text, row[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        # الجملة الختامية الحرفية للمحضر الأول
        doc.add_paragraph("\nFormat papier : Néant.")
        doc.add_paragraph(f"Le président de la commission d’ouverture des plis invite la société : {curr['Nom']} est le moins disant pour un montant de {curr['Montant']} Dhs TTC ({amt_words}) à confirmer son offre, et suspend la séance et fixe un rendez-vous le {next_rdv.strftime('%d/%m/%Y')} ou sur invitation.")
    
    else:
        prev = data.iloc[idx - 1]
        doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société {prev['Nom']} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_final:
            doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission constate que la société : {curr['Nom']} a confirmé son offre par lettre de confirmation.")
            p_res = doc.add_paragraph(f"Le président de la commission VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_words}).")
            p_res.bold = True
        else:
            doc.add_paragraph(f"Après écartement de la société {prev['Nom']} le président invite la société : {curr['Nom']} qui est classé le {pv_num}éme pour un montant de {curr['Montant']} Dhs TTC ({amt_words}) à confirmer son offre le {next_rdv.strftime('%d/%m/%Y')} أو على إثر استدعاء.")

    # --- التاريخ يميناً والتوقيعات ---
    p_date = doc.add_paragraph(f"\nAskaouen le {reunion_date.strftime('%d/%m/%Y')}")
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("Signatures des membres de la commission :").bold = True
    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.width = Inches(6.5)
    sig_tab.rows[0].cells[0].text = "Le Président"; sig_tab.rows[0].cells[1].text = "Le Directeur"; sig_tab.rows[0].cells[2].text = "Le Technicien"
    sig_tab.rows[1].cells[0].text = p_name; sig_tab.rows[1].cells[1].text = d_name; sig_tab.rows[1].cells[2].text = t_name
    for row in sig_tab.rows:
        for cell in row.cells: cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- حفظ وتحميل ---
    bio = BytesIO()
    doc.save(bio)
    st.download_button(label="📥 تحميل المحضر بصيغة Word", data=bio.getvalue(), file_name=f"PV_{pv_num}_Askaouen.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.success("✅ الكود جاهز للتجربة. قم بملء البيانات ثم اضغط على زر التوليد.")
