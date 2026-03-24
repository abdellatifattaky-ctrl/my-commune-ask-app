import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Commune d'Askaouen - Gestion BC", layout="wide")

st.title("🏛️ منصة تدبير سندات الطلب - جماعة أسكاون")
st.info("نظام إعداد المحاضر مع خاصية اختيار المتنافس المؤكد (Confirmation de l'offre)")

# --- الإعدادات الإدارية ---
st.sidebar.header("اللجنة الإدارية")
president = st.sidebar.text_input("Le Président", "MOHAMED ZILALI")
directeur = st.sidebar.text_input("Le Directeur des Services", "M BAREK BAK")
technicien = st.sidebar.text_input("Le Technicien", "ATTAKY ABDELLATIF")

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
        objet = st.text_input("الموضوع (Objet)", "Location d’une Tractopelle")
    with col2:
        date_doc = st.date_input("التاريخ", date.today())
        heure_doc = st.text_input("الساعة", "10:00")

    # 1. إدخال جدول المتنافسين الخمسة (أساسي لجميع المحاضر)
    st.subheader("جدول ترتيب المتنافسين الخمسة (Les 5 concurrents)")
    df_rank = pd.DataFrame([
        {"Rang": "1er", "Nom": "", "Montant": ""},
        {"Rang": "2ème", "Nom": "", "Montant": ""},
        {"Rang": "3ème", "Nom": "", "Montant": ""},
        {"Rang": "4ème", "Nom": "", "Montant": ""},
        {"Rang": "5ème", "Nom": "", "Montant": ""}
    ])
    edited_rank = st.data_editor(df_rank, use_container_width=True)

    # 2. خاصية اختيار المتنافس الذي أكد أو لم يؤكد العرض
    if option == "PV de Validation (Confirmation d'offre)":
        st.write("---")
        st.subheader("تحديد المتنافس المعني بالتأكيد")
        selected_rank = st.selectbox("اختر ترتيب المتنافس الذي سيتم البت في عرضه:", ["1er", "2ème", "3ème", "4ème", "5ème"])
        statut = st.radio("حالة التأكيد:", ["A confirmé son offre (تم التأكيد)", "N'a pas confirmé (لم يؤكد - إقصاء)"])
        date_prochaine = st.date_input("موعد الجلسة الموالية (في حالة الإقصاء)")

    submitted = st.form_submit_button("توليد الوثيقة الرسمية")

if submitted:
    doc = Document()
    # الترويسة الرسمية
    table_h = doc.add_table(rows=1, cols=2)
    table_h.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE ASKAOUN"
    table_h.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    table_h.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # البحث عن بيانات المتنافس المختار
    target_row = edited_rank[edited_rank['Rang'] == selected_rank if 'selected_rank' in locals() else '1er'].iloc[0]
    
    if option == "1er PV : Ouverture et Classement":
        doc.add_heading("PROCES-VERBAL N° 01", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le {date_doc} à {heure_doc}, la commission s'est réunie...")
        # إنشاء الجدول
        table = doc.add_table(rows=1, cols=3); table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text = 'Classement', 'Nom du Concurrent', 'Montant TTC'
        for _, row in edited_rank.iterrows():
            if row["Nom"]:
                r = table.add_row().cells
                r[0].text, r[1].text, r[2].text = str(row["Rang"]), str(row["Nom"]), f"{row['Montant']} DH"

    elif option == "PV de Validation (Confirmation d'offre)":
        doc.add_heading("PROCES-VERBAL DE VALIDATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        if "N'a pas confirmé" in statut:
            doc.add_paragraph(f"La commission constate que la société {target_row['Nom']} ({target_row['Rang']}) n’a pas confirmé son offre.")
            doc.add_paragraph(f"En conséquence, la commission décide d'écarter ladite société et d'inviter le concurrent suivant.")
        else:
            doc.add_paragraph(f"La commission constate que la société {target_row['Nom']} ({target_row['Rang']}) a confirmé son offre.")
            doc.add_paragraph(f"Le président valide la confirmation et attribue le bon de commande à ladite société pour {target_row['Montant']} DH TTC.").bold = True

    # التوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {date_doc}")
    doc.add_paragraph(f"Signatures :\n{president}          {directeur}          {technicien}")

    bio = BytesIO(); doc.save(bio)
    doc_download = bio.getvalue()
    file_name = f"PV_{selected_rank if 'selected_rank' in locals() else '01'}_{num_doc.replace('/','_')}.docx"

if doc_download:
    st.success("✅ تم توليد المحضر بناءً على اختيار المتنافس")
    st.download_button("📥 تحميل المحضر (.docx)", doc_download, file_name)
