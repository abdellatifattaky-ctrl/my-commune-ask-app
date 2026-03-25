import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- الإعدادات البصرية (Lacoste Style) ---
st.set_page_config(page_title="Askaouen Pro - Final Version", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    h1, h2, h3 { color: #004526 !important; font-family: 'Arial'; }
    .stButton>button {
        background-color: #004526;
        color: white;
        border-radius: 25px;
        font-weight: bold;
        border: 2px solid #004526;
    }
    .stButton>button:hover {
        background-color: white;
        color: #004526;
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

# --- الواجهة الرئيسية ---
st.title("🏛️ منظومة تدبير سندات الطلب الذكية")
st.subheader("جماعة أسكاون - إقليم تارودانت")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Coat_of_arms_of_Morocco.svg/1200px-Coat_of_arms_of_Morocco.svg.png", width=80)
    st.header("اللجنة الإدارية")
    p_name = st.text_input("الرئيس", "MOHAMED ZILALI")
    d_name = st.text_input("مدير المصالح", "M BAREK BAK")
    t_name = st.text_input("التقني", "ABDELLATIF ATTAKY")

# معطيات السند
with st.expander("📝 تفاصيل سند الطلب (Bon de Commande)", expanded=True):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("رقم السند", "01/ASK/2026")
    date_pub = c2.date_input("تاريخ النشر بالبوابة", date(2026, 3, 25))
    obj_bc = st.text_area("موضوع السند", "Achat de fournitures...")

# جدول المتنافسين
st.info("💡 أدخل الشركات حسب ترتيب مبالغها (من الأقل إلى الأكثر)")
data = st.data_editor(pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
]), use_container_width=True)

st.divider()

# --- منطق اختيار المحضر والنتيجة ---
col_v1, col_v2, col_v3 = st.columns(3)
pv_num = col_v1.selectbox("رقم المحضر الحالي:", [1, 2, 3, 4, 5, 6])
reunion_date = col_v2.date_input("تاريخ الجلسة", date.today())

is_final_attr = False
is_infructueux = False

if pv_num == 6:
    res_6 = st.radio("نتيجة المحضر السادس:", ["إسناد نهائي (Attribution)", "غير مثمر (Infructueux)"])
    is_final_attr = (res_6 == "إسناد نهائي (Attribution)")
    is_infructueux = not is_final_attr
else:
    # الميزة الجديدة: أي محضر يمكن أن يكون نهائياً
    is_final_attr = st.checkbox(f"✅ هل أكدت الشركة رقم {pv_num} عرضها؟ (إسناد نهائي)")
    if not is_final_attr:
        next_date = col_v3.date_input("موعد الجلسة القادمة", date.today() + timedelta(days=1))

if st.button("🚀 توليد المحضر المنسق"):
    doc = Document()
    # (إعدادات الهوامش والترويسة...)
    section = doc.sections[0]
    section.top_margin = Cm(1.5)
    
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_paragraph("\n")
    title = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à 10h00mn, la commission s'est réunie conformément à l'article 91 du décret n° 2-22-431.")

    idx = pv_num - 1 # ترتيب الشركة الحالية
    
    if pv_num == 1:
        doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires sont :")
        # (جدول المتنافسين...)
        curr = data.iloc[0]
        amt_w = format_to_words_fr(curr['Montant'])
        p = doc.add_paragraph(f"Le président invite la société : {curr['Nom']} (moins disant) pour {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre, ")
        p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True
    
    else:
        # المحاضر من 2 إلى 6
        prev_company = data.iloc[idx-1]['Nom']
        doc.add_paragraph(f"La commission constate que la société {prev_company} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_infructueux:
            doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :")
            res_p = doc.add_paragraph("INFRUCTUEUX")
            res_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            res_p.bold = True
        
        elif is_final_attr:
            # تطبيق نموذج الإسناد النهائي (نسخة المحضر 6)
            curr = data.iloc[idx]
            amt_w = format_to_words_fr(curr['Montant'])
            doc.add_paragraph(f"La commission constate que la société {curr['Nom']} a confirmé son offre par lettre de confirmation.")
            p_res = doc.add_paragraph(f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société {curr['Nom']} pour un montant de : {curr['Montant']} Dhs TTC ({amt_w}).")
            p_res.bold = True
        
        else:
            # استمرار المسطرة للمنافس الموالي
            curr = data.iloc[idx]
            amt_w = format_to_words_fr(curr['Montant'])
            p = doc.add_paragraph(f"Après écartement de la société {prev_company}, le président invite la société : {curr['Nom']} ({pv_num}éme rang) pour {curr['Montant']} Dhs TTC ({amt_w}) à confirmer son offre, ")
            p.add_run(f"et suspend la séance et fixe un rendez-vous le {next_date.strftime('%d/%m/%Y')} ou sur invitation.").bold = True

    # التوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sig_tab = doc.add_table(rows=2, cols=3)
    sig_tab.rows[0].cells[0].text = "Le Président"; sig_tab.rows[0].cells[1].text = "Le Directeur"; sig_tab.rows[0].cells[2].text = "Le Technicien"
    sig_tab.rows[1].cells[0].text, sig_tab.rows[1].cells[1].text, sig_tab.rows[1].cells[2].text = p_name, d_name, t_name

    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
