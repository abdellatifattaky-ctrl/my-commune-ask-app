import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from io import BytesIO
from datetime import date
from num2words import num2words

# إعداد الصفحة
st.set_page_config(page_title="Commune d'Askaouen - Gestion des 5 PV", layout="wide")

# دالة تحويل المبلغ إلى حروف بالفرنسية
def format_amount_fr(amount):
    try:
        val = float(str(amount).replace(',', ''))
        euros = int(val)
        cents = int(round((val - euros) * 100))
        text = num2words(euros, lang='fr').upper() + " DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " PILE"
        return text
    except:
        return "________________"

# --- القائمة الجانبية ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Coat_of_arms_of_Morocco.svg", width=100)
st.sidebar.header("اللجنة الإدارية")
pres = st.sidebar.text_input("Le Président", "MOHAMED ZILALI")
dir_serv = st.sidebar.text_input("Directeur des Services", "M BAREK BAK")
tech = st.sidebar.text_input("Le Technicien", "ATTAKY ABDELLATIF")

st.title("🏛️ نظام المحاضر الخمسة - جماعة أسكاون")

# --- إدخال البيانات ---
with st.container():
    col1, col2, col3 = st.columns([2,1,1])
    num_bc = col1.text_input("رقم سند الطلب (N° BC)", "01/ASK/2025")
    date_pub = col2.date_input("تاريخ النشر", date(2025, 3, 25))
    reunion_hour = col3.text_input("الساعة", "12h00mn")
    
    obj_bc = st.text_area("موضوع الطلب (Objet)", "Location d’une Tractopelle pour les travaux divers.")

# --- جدول المتنافسين الخمسة ---
st.subheader("📊 ترتيب المتنافسين الخمسة")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
edited_df = st.data_editor(df_init, num_rows="fixed", use_container_width=True)

# --- اختيار نوع المحضر والسيناريو ---
st.subheader("📄 توليد المحضر")
pv_type = st.selectbox("اختر المحضر المطلوب استخراجه الآن:", [
    "PV 1 : فتح الأظرفة والترتيب (الكل)",
    "PV 2 : إقصاء الأول واستدعاء الثاني",
    "PV 3 : إقصاء الثاني واستدعاء الثالث",
    "PV 4 : إقصاء الثالث واستدعاء الرابع",
    "PV 5 : إقصاء الرابع واستدعاء الخامس / أو الإسناد النهائي"
])

is_final = st.checkbox("هل هذا هو محضر الإسناد النهائي (Attribution)؟")
reunion_date = st.date_input("تاريخ اليوم (تاريخ المحضر)", date.today())
next_meeting = st.date_input("تاريخ الجلسة القادمة (في حالة الاستدعاء)")

if st.button("🚀 إنشاء ملف Word للمحضر"):
    doc = Document()
    
    # الترويسة الرسمية
    header = doc.sections[0].header
    htable = header.add_table(1, 2, Inches(6))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANTE\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_paragraph("\n")
    title = doc.add_heading(f"{pv_type.split(':')[0]}", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # النصوص الثابتة
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission composée de :")
    doc.add_paragraph(f"- {pres} : Président\n- {dir_serv} : Directeur\n- {tech} : Technicien")
    doc.add_paragraph(f"S'est réunie... concernant l’avis n° {num_bc} publié le {date_pub}...")

    # منطق المحاضر بناءً على البيانات
    if "PV 1" in pv_type:
        doc.add_paragraph("Classement des concurrents (Offres électroniques) :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in edited_df.iterrows():
            row_cells = tab.add_row().cells
            row_cells[0].text, row_cells[1].text, row_cells[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        first = edited_df.iloc[0]
        amt_txt = format_amount_fr(first['Montant'])
        doc.add_paragraph(f"\nLe président invite la société {first['Nom']} (Moins disant) pour {first['Montant']} DH ({amt_txt}) à confirmer son offre le {next_meeting}.")

    elif "PV 2" in pv_type or "PV 3" in pv_type or "PV 4" in pv_type or "PV 5" in pv_type:
        # تحديد من خرج ومن دخل بناءً على رقم المحضر
        idx = int(pv_type[3]) - 1 # مثلا PV 2 -> idx 1
        out_co = edited_df.iloc[idx-1]
        in_co = edited_df.iloc[idx]
        
        doc.add_paragraph(f"La commission constate que la société {out_co['Nom']} n'a pas confirmé son offre.")
        
        if is_final:
            amt_txt = format_amount_fr(in_co['Montant'])
            doc.add_paragraph(f"Le président valide la confirmation et ATTRIBUE le bon de commande à {in_co['Nom']} pour {in_co['Montant']} DH ({amt_txt}).").bold = True
        else:
            amt_txt = format_amount_fr(in_co['Montant'])
            doc.add_paragraph(f"Après écartement de {out_co['Nom']}, le président invite {in_co['Nom']} ({in_co['Rang']}ème) pour {in_co['Montant']} DH ({amt_txt}) à confirmer son offre le {next_meeting}.")

    # التوقيعات
    doc.add_paragraph(f"\nAskaouen le {reunion_date}\n" + "_"*40)
    p_sig = doc.add_paragraph(f"{pres}                {dir_serv}                {tech}")
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # التحميل
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل المحضر بصيغة Word", bio.getvalue(), f"PV_{num_bc.replace('/','-')}.docx")
