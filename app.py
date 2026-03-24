import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# دالة تحويل المبالغ إلى حروف بالفرنسية
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

st.set_page_config(page_title="Commune Askaouen - PV App", layout="wide")

# إعدادات اللجنة من القائمة الجانبية
st.sidebar.header("Membres de la commission")
p_name = st.sidebar.text_input("Président", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("Directeur du service", "M BAREK BAK")
t_name = st.sidebar.text_input("Technicien", "ABDELLATIF ATTAKY")

st.title("🏛️ نظام توليد المحاضر الرسمي - جماعة أسكاون")

# إدخال البيانات
with st.expander("📝 معلومات الملف"):
    c1, c2 = st.columns(2)
    num_bc = c1.text_input("N° BC", "01/ASK/2025")
    date_pub = c2.date_input("Date de publication", date(2025, 3, 25))
    obj_bc = st.text_area("Objet", "Location d’une Tractopelle pour les travaux divers.")

# جدول المتنافسين
st.subheader("📊 قائمة المتنافسين الخمسة")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

# خيارات المحضر
pv_num = st.selectbox("رقم المحضر:", [1, 2, 3, 4, 5])
is_final = st.checkbox("✅ هل هذا هو محضر الإسناد النهائي (Attribution)؟")
reunion_date = st.date_input("تاريخ اجتماع اليوم", date.today())
reunion_hour = st.text_input("الساعة", "12h00mn")
next_date = st.date_input("تاريخ الموعد القادم")

if st.button("🚀 إنشاء المحضر بالنص الأصلي الكامل"):
    doc = Document()
    
    # الترويسة
    header = doc.sections[0].header
    htable = header.add_table(1, 2, Inches(6))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # المتن الأصلي (النص الذي قدمته لي حرفياً)
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission d’ouverture des plis composée Comme suit :")
    doc.add_paragraph(f"- {p_name} : Président de la commission\n- {d_name} : Directeur du service\n- {t_name} : Technicien de la commune")
    
    p2 = doc.add_paragraph(f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub} sur le portail des marchés publics, en تطبيق أحكام المادة 91 من المرسوم رقم 2-22-431 (8 مارس 2023) المتعلق بالصفقات العمومية، موضوعه: {obj_bc}")

    idx = pv_num - 1
    current_co = data.iloc[idx]
    amt_w = format_to_words_fr(current_co['Montant'])

    if pv_num == 1:
        # نص المحضر الأول بالكامل
        doc.add_paragraph("Les soumissionnaires qui ont déposés leurs offres de prix électroniquement sont :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            row_cells = tab.add_row().cells
            row_cells[0].text, row_cells[1].text, row_cells[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        doc.add_paragraph(f"\nLe président de la commission d’ouverture des plis invite la société : {current_co['Nom']} est le moins disant pour un montant de {current_co['Montant']} Dhs TTC ({amt_w}) à confirmer son offre، ويتم تعليق الجلسة وتحديد موعد في {next_date} أو على إثر استدعاء.")

    else:
        prev_co = data.iloc[idx - 1]
        # جملة الإقصاء الحرفية
        doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société {prev_co['Nom']} n’a pas confirmé son offre par lettre de confirmation.")
        
        if is_final:
            # جملة التأكيد والإسناد الحرفية كما طلبت
            doc.add_paragraph(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société : {current_co['Nom']} a confirmé son offre par lettre de confirmation.")
            doc.add_paragraph(f"Le président de la commission valide la confirmation et attribue le bon de commande à la société {current_co['Nom']} pour un montant de : {current_co['Montant']} Dhs TTC ({amt_w}).").bold = True
        else:
            # جملة الاستدعاء للمحاضر الوسطى
            doc.add_paragraph(f"Après écartement de la société {prev_co['Nom']} le président de la commission invite la société : {current_co['Nom']} qui est classé le {pv_num}éme pour un montant de {current_co['Montant']} Dhs TTC ({amt_w}) à confirmer son offre، ويتم تعليق الجلسة وتحديد موعد في {next_date} أو على إثر استدعاء.")

    # الخاتمة والتوقيعات
    doc.add_paragraph(f"\nAskaouen le {date.today()}\n")
    sig = doc.add_paragraph(f"{p_name}             {d_name}             {t_name}")
    sig.alignment = WD_ALIGN_PARAGRAPH.CENTER

    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل المحضر النهائي", bio.getvalue(), f"PV_{pv_num}.docx")
