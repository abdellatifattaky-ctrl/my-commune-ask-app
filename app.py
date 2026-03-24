import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة تحويل المبالغ إلى حروف فرنسية ---
def format_amount_to_words(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        # تحويل الرقم إلى كلمات بالفرنسية كعملة
        words = num2words(val, lang='fr', to='currency', currency='MAD').upper()
        # تصحيح المصطلحات لتناسب المحاضر المغربية
        words = words.replace('EUROS', 'DIRHAMS').replace('EURO', 'DIRHAM')
        words = words.replace('CENTS', 'CENTIMES').replace('CENT', 'CENTIME')
        return words
    except:
        return "________________"

# --- إعدادات الواجهة ---
st.set_page_config(page_title="Commune Askaouen - Multi-PV Generator", layout="wide")

# القائمة الجانبية للجنة
st.sidebar.header("اللجنة الإدارية")
p_name = st.sidebar.text_input("الرئيس", "MOHAMED ZILALI")
d_name = st.sidebar.text_input("المدير", "M BAREK BAK")
t_name = st.sidebar.text_input("التقني", "ATTAKY ABDELLATIF")

st.title("🏛️ مولد المحاضر الخمسة - جماعة أسكاون")

# --- الخطوة 1: إدخال البيانات العامة ---
with st.expander("1️⃣ معلومات السند والإعلان", expanded=True):
    c1, c2, c3 = st.columns(3)
    num_bc = c1.text_input("رقم سند الطلب", "01/ASK/2025")
    date_pub = c2.date_input("تاريخ النشر", date(2025, 3, 25))
    obj_bc = st.text_area("الموضوع", "Location d’une Tractopelle pour les travaux divers.")

# --- الخطوة 2: جدول المتنافسين الخمسة ---
with st.expander("2️⃣ ترتيب المتنافسين (Top 5)", expanded=True):
    df_init = pd.DataFrame([
        {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
        {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
        {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
        {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
        {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
    ])
    data = st.data_editor(df_init, use_container_width=True)

# --- الخطوة 3: اختيار المحضر والسيناريو ---
st.divider()
pv_choice = st.selectbox("اختر رقم المحضر المطلوب:", [1, 2, 3, 4, 5])
is_final_attribution = st.checkbox("هل هذا هو محضر الإسناد النهائي (Attribution)؟")
reunion_date = st.date_input("تاريخ اجتماع اللجنة", date.today())
reunion_hour = st.text_input("ساعة الاجتماع", "12h00mn")
next_rdv = st.date_input("موعد الجلسة القادمة (في حالة الاستدعاء)")

if st.button(f"🚀 توليد المحضر رقم {pv_choice} بصيغة Word"):
    doc = Document()
    
    # الترويسة الرسمية (Header)
    header = doc.sections[0].header
    htable = header.add_table(1, 2, Inches(6))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANTE\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان
    doc.add_paragraph("\n")
    doc.add_heading(f"{pv_choice}éme Procès verbal", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

    # المتن الأساسي
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    doc.add_paragraph(f"Le {reunion_date} à {reunion_hour}, la commission composée de :")
    doc.add_paragraph(f"- {p_name} : Président\n- {d_name} : Directeur\n- {t_name} : Technicien")
    doc.add_paragraph(f"S'est réunie... concernant l’avis n° {num_bc} publié le {date_pub}...")

    # منطق المحاضر بناءً على الاختيار
    idx = pv_choice - 1
    current_co = data.iloc[idx]
    
    if pv_choice == 1:
        # المحضر الأول: عرض الجدول والترتيب
        doc.add_paragraph("Les soumissionnaires qui ont déposés leurs offres :")
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells; hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Concurrent', 'Montant TTC'
        for _, r in data.iterrows():
            row_cells = tab.add_row().cells
            row_cells[0].text, row_cells[1].text, row_cells[2].text = str(r['Rang']), r['Nom'], f"{r['Montant']} MAD"
        
        doc.add_paragraph(f"\nLe président invite la société {current_co['Nom']} (Moins disant) pour {current_co['Montant']} DH ({format_amount_to_words(current_co['Montant'])}) à confirmer son offre le {next_rdv}.")

    else:
        # المحاضر من 2 إلى 5: إقصاء السابق واستدعاء الحالي
        prev_co = data.iloc[idx - 1]
        doc.add_paragraph(f"La commission constate que la société {prev_co['Nom']} n'a pas confirmé son offre.")
        
        if is_final_attribution:
            doc.add_paragraph(f"Le président valide la confirmation et ATTRIBUE le bon de commande à la société {current_co['Nom']} pour un montant de : {current_co['Montant']} DH ({format_amount_to_words(current_co['Montant'])}).").bold = True
        else:
            doc.add_paragraph(f"Après écartement de {prev_co['Nom']}, le président invite la société {current_co['Nom']} ({current_co['Rang']}éme) pour {current_co['Montant']} DH ({format_amount_to_words(current_co['Montant'])}) à confirmer son offre le {next_rdv}.")

    # التوقيعات
    doc.add_paragraph(f"\nAskaouen le {reunion_date}\n" + "_"*40)
    sig_tab = doc.add_table(rows=1, cols=3); sig_tab.width = Inches(6)
    sig_tab.rows[0].cells[0].text = p_name
    sig_tab.rows[0].cells[1].text = d_name
    sig_tab.rows[0].cells[2].text = t_name

    # التحميل
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل المحضر رقم {pv_choice}", bio.getvalue(), f"PV_{pv_choice}_{num_bc.replace('/','-')}.docx")
