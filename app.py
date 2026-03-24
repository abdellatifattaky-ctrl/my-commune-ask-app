import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Gestion Administrative - Askaouen", layout="wide")

st.title("🏛️ منصة التدبير الإداري - جماعة أسكاون")
st.markdown("---")

# إعدادات اللجنة في الجانب
st.sidebar.header("اللجنة الإدارية")
president = st.sidebar.text_input("الرئيس", "MOHAMED ZILALI")
directeur = st.sidebar.text_input("مدير المصالح", "M BAREK BAK")
technicien = st.sidebar.text_input("التقني", "ATTAKY ABDELLATIF")

# اختيار نوع الوثيقة
option = st.selectbox("اختر نوع الوثيقة:", 
                     ["Avis d'achat sur Bons de Commande",
                      "1er PV : Ouverture et Classement",
                      "2ème/3ème PV : Écartement",
                      "4ème PV : Attribution finale"])

doc_download = None
file_name = ""

with st.form("global_form"):
    col1, col2 = st.columns(2)
    with col1:
        num_doc = st.text_input("رقم السند/الملف", "03/ASK/2025")
        objet = st.text_input("الموضوع (Objet)", "Location d’une Tractopelle")
    with col2:
        date_reunion = st.date_input("تاريخ اليوم/الاجتماع", date.today())
        heure = st.text_input("الساعة (Heure)", "12h00mn")

    # --- الجزء الخاص بالإعلان (Avis) ---
    if option == "Avis d'achat sur Bons de Commande":
        st.subheader("جدول المواد/الخدمات")
        df_init = pd.DataFrame([{"Désignation": "", "Unité": "", "Quantité": ""}])
        edited_df = st.data_editor(df_init, num_rows="dynamic", use_container_width=True)

    # --- الجزء الخاص بالمحاضر (PVs) ---
    else:
        if "1er PV" in option:
            st.subheader("ترتيب المتنافسين (Nom;Total TTC)")
            competitors = st.text_area("أدخل الشركات (شركة 1;60000)", help="شركة;مبلغ")
        elif "2ème/3ème" in option:
            societe_ecartee = st.text_input("الشركة المبعدة (N'a pas confirmé)")
            societe_suivante = st.text_input("الشركة الموالية (Invitée)")
            montant_suivant = st.text_input("المبلغ (TTC)")
        elif "4ème" in option:
            gagnant = st.text_input("الشركة الفائزة نهائياً")
            montant_final = st.text_input("المبلغ النهائي")

    submitted = st.form_submit_button("تجهيز الوثيقة للتحميل")

if submitted:
    doc = Document()
    
    # 1. حالة الإعلان (Avis)
    if option == "Avis d'achat sur Bons de Commande":
        doc.add_heading(f"AVIS D’ACHAT N° {num_doc}", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {objet}").bold = True
        table = doc.add_table(rows=1, cols=4); table.style = 'Table Grid'
        for i, row in edited_df.iterrows():
            if row["Désignation"]:
                r = table.add_row().cells
                r[0].text, r[1].text, r[2].text, r[3].text = str(i+1), str(row["Désignation"]), str(row["Unité"]), str(row["Quantité"])
    
    # 2. حالة المحاضر (بناءً على النماذج الفرنسية التي أرسلتها)
    else:
        doc.add_heading(f"{option.split(':')[0]}", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Commission d’ouverture des plis - Procédure BC").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le {date_reunion} à {heure}, la commission composée de :")
        doc.add_paragraph(f"- {president}\n- {directeur}\n- {technicien}")
        doc.add_paragraph(f"S'est réunie pour l'objet : {objet} (Avis n° {num_doc})")

        if "1er PV" in option:
            doc.add_paragraph("Les concurrents classés :")
            for line in competitors.split('\n'):
                if ';' in line: doc.add_paragraph(f"- {line.replace(';', ' : ')} MAD")
        elif "2ème/3ème" in option:
            doc.add_paragraph(f"La société {societe_ecartee} est écartée. La société {societe_suivante} est invitée pour {montant_suivant} DH.")
        elif "4ème" in option:
            doc.add_paragraph(f"L'attribution finale est faite à : {gagnant} pour un montant de {montant_final} DH.")

    # التوقيعات
    doc.add_paragraph(f"\nAskaouen, le {date_reunion}")
    doc.add_paragraph(f"{president}          {directeur}          {technicien}")

    bio = BytesIO(); doc.save(bio)
    doc_download = bio.getvalue()
    file_name = f"{option.replace(' ', '_')}_{num_doc.replace('/','_')}.docx"

if doc_download:
    st.success("✅ الوثيقة جاهزة!")
    st.download_button("📥 تحميل الآن", doc_download, file_name)
