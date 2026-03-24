import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from io import BytesIO
from datetime import date

# إعداد الصفحة
st.set_page_config(page_title="Commune d'Askaouen - App", layout="wide")

# --- القائمة الجانبية (أعضاء اللجنة) ---
st.sidebar.header("اللجنة الإدارية")
president = st.sidebar.text_input("Le Président", "MOHAMED ZILALI")
directeur = st.sidebar.text_input("Le Directeur des Services", "M BAREK BAK")
technicien = st.sidebar.text_input("Le Technicien", "ATTAKY ABDELLATIF")

# اختيار نوع الوثيقة
option = st.selectbox("نوع الوثيقة:", 
                     ["Avis d'achat sur Bons de Commande",
                      "1er PV : Ouverture et Classement",
                      "PV de Validation (Confirmation d'offre)"])

doc_download = None
file_name = ""

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        num_doc = st.text_input("رقم السند/الإعلان", "03/ASK/2025")
        objet = st.text_input("الموضوع (Objet)", "Station de pompage et relevage")
    with col2:
        date_doc = st.date_input("التاريخ", date.today())
        heure_doc = st.text_input("الساعة", "10:00")

    # جدول المتنافسين الخمسة
    st.subheader("جدول الترتيب والمنافسين")
    df_init = pd.DataFrame([
        {"Rang": "1er", "Nom": "", "Montant": ""},
        {"Rang": "2ème", "Nom": "", "Montant": ""},
        {"Rang": "3ème", "Nom": "", "Montant": ""},
        {"Rang": "4ème", "Nom": "", "Montant": ""},
        {"Rang": "5ème", "Nom": "", "Montant": ""}
    ])
    edited_rank = st.data_editor(df_init, use_container_width=True)

    selected_rank = "1er"
    if option == "PV de Validation (Confirmation d'offre)":
        selected_rank = st.selectbox("المتنافس المعني بالتأكيد:", ["1er", "2ème", "3ème", "4ème", "5ème"])

    submitted = st.form_submit_button("توليد الوثيقة الرسمية")

if submitted:
    doc = Document()
    
    # --- إضافة الترويسة (Header) بنظام الجدول المخفي ---
    header_section = doc.sections[0]
    header = header_section.header
    htable = header.add_table(1, 2, Inches(6))
    
    # الجانب الأيسر (Français)
    c_left = htable.rows[0].cells[0]
    p_fr = c_left.add_paragraph("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANTE\nCOMMUNE D'ASKAOUN")
    p_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # الجانب الأيمن (العربية)
    c_right = htable.rows[0].cells[1]
    p_ar = c_right.add_paragraph("المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nدائرة تالوين\nجماعة أسكاون")
    p_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # --- العنوان الرئيسي ---
    doc.add_paragraph("\n")
    title_text = f"COMMUNE ASKAOUN - {option}"
    title = doc.add_heading(title_text, level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f"Objet : {objet}").bold = True
    doc.add_paragraph(f"Réf : {num_doc} | Date : {date_doc} à {heure_doc}")

    # محتوى المحضر الأول
    if option == "1er PV : Ouverture et Classement":
        doc.add_paragraph("\nTableau de classement des concurrents :")
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text = 'Rang', 'Nom du Concurrent', 'Montant TTC'
        for _, row in edited_rank.iterrows():
            if row["Nom"]:
                r = table.add_row().cells
                r[0].text, r[1].text, r[2].text = str(row["Rang"]), str(row["Nom"]), f"{row['Montant']} DH"

    # التوقيعات (كما في صورتك الأخيرة)
    doc.add_paragraph("\n" + "_"*40)
    sig_text = f"Signatures: {president} | {directeur} | {technicien}"
    p_sig = doc.add_paragraph(sig_text)
    
    # تحويل الملف للتحميل
    bio = BytesIO()
    doc.save(bio)
    doc_download = bio.getvalue()
    file_name = f"{option.replace(' ', '_')}_{num_doc.replace('/', '-')}.docx"

# زر التحميل خارج الاستمارة لتفدي الأخطاء
if doc_download:
    st.success("✅ تم دمج الشعار والبيانات بنجاح!")
    st.download_button("📥 تحميل المستند الرسمي (.docx)", doc_download, file_name)
