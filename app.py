import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Commune d'Askaouen", layout="wide")

st.sidebar.header("اللجنة الإدارية")
president = st.sidebar.text_input("Le Président", "MOHAMED ZILALI")
directeur = st.sidebar.text_input("Le Directeur des Services", "M BAREK BAK")
technicien = st.sidebar.text_input("Le Technicien", "ATTAKY ABDELLATIF")

option = st.selectbox("نوع الوثيقة:", 
                     ["Avis d'achat sur Bons de Commande",
                      "1er PV : Ouverture et Classement",
                      "PV de Validation (Confirmation d'offre)"])

# متغيرات لتخزين البيانات خارج الفورم
doc_download = None
file_name = ""

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        num_doc = st.text_input("رقم السند/الإعلان", "03/ASK/2025")
        objet = st.text_input("الموضوع (Objet)", "Location d’une Tractopelle")
    with col2:
        date_doc = st.date_input("التاريخ", date.today())
        heure_doc = st.text_input("الساعة", "10:00")

    # جدول المتنافسين (تم توحيد اسم العمود ليكون 'Rang')
    st.subheader("جدول ترتيب المتنافسين")
    df_init = pd.DataFrame([
        {"Rang": "1er", "Nom": "", "Montant": ""},
        {"Rang": "2ème", "Nom": "", "Montant": ""},
        {"Rang": "3ème", "Nom": "", "Montant": ""},
        {"Rang": "4ème", "Nom": "", "Montant": ""},
        {"Rang": "5ème", "Nom": "", "Montant": ""}
    ])
    edited_rank = st.data_editor(df_init, use_container_width=True)

    selected_rank = "1er"
    statut = ""
    if option == "PV de Validation (Confirmation d'offre)":
        selected_rank = st.selectbox("اختر ترتيب المتنافس المعني:", ["1er", "2ème", "3ème", "4ème", "5ème"])
        statut = st.radio("حالة التأكيد:", ["A confirmé", "N'a pas confirmé"])

    submitted = st.form_submit_button("تجهيز الوثيقة")

# معالجة البيانات خارج الفورم لحل مشكلة الصورة رقم 5
if submitted:
    doc = Document()
    doc.add_heading(f"COMMUNE ASKAOUN - {option}", 0)
    
    # حل مشكلة الصورة رقم 6: الوصول للبيانات بشكل آمن
    try:
        target_row = edited_rank[edited_rank['Rang'] == selected_rank].iloc[0]
        
        if option == "PV de Validation (Confirmation d'offre)":
            doc.add_paragraph(f"Société: {target_row['Nom']}")
            doc.add_paragraph(f"Statut: {statut}")
            doc.add_paragraph(f"Montant: {target_row['Montant']} DH")
        
        # إضافة التوقيعات
        doc.add_paragraph(f"\nSignatures: {president} | {directeur} | {technicien}")
        
        bio = BytesIO()
        doc.save(bio)
        doc_download = bio.getvalue()
        file_name = f"PV_{num_doc.replace('/', '_')}.docx"
    except Exception as e:
        st.error(f"خطأ في البيانات: {e}")

# زر التحميل خارج الفورم (حل نهائي)
if doc_download:
    st.success("✅ الوثيقة جاهزة")
    st.download_button("📥 تحميل ملف الوورد", doc_download, file_name)
