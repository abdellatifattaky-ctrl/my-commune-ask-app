import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- وظيفة التنسيق والترويسة الموحدة ---
def setup_header(doc):
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- واجهة التطبيق ---
st.set_page_config(page_title="منصة جماعة أسكاون المتكاملة", layout="wide")

st.sidebar.title("🏛️ الإدارة الرقمية")
menu = st.sidebar.radio("اختر القسم:", ["الصفقات العمومية (BC/AO)", "أشغال المجلس (الدورات)", "الأوامر الخدمية (OS)"])

# --- القسم الأول: الصفقات وطلبات العروض ---
if menu == "الصفقات العمومية (BC/AO)":
    st.header("📋 إدارة الصفقات وطلبات العروض")
    type_p = st.selectbox("نوع المسطرة:", ["سند طلب (BC)", "طلب عروض مفتوح (AO Ouvert)", "طلب عروض محصور"])
    num_p = st.text_input("رقم الصفقة/السند", "01/ASK/2026")
    obj_p = st.text_area("موضوع الصفقة", "أدخل الموضوع هنا...")
    
    st.subheader("📊 جدول المتنافسين")
    df = pd.DataFrame([{"Concurrent": "STE EXAMPLE", "Montant TTC": "150000.00", "Statut": "Admis"}])
    data = st.data_editor(df, num_rows="dynamic")

    if st.button("توليد المحضر الرسمي"):
        doc = Document(); setup_header(doc)
        title = doc.add_paragraph(f"PROCÈS-VERBAL\n{type_p} N° {num_p}")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nObjet : {obj_p}").bold = True
        doc.add_paragraph(f"En application du décret n° 2-22-431 relatif aux marchés publics...")
        # (إضافة الجدول آلياً هنا)
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المستند", bio.getvalue(), f"PV_{num_p}.docx")

# --- القسم الثاني: الدورات والمجلس ---
elif menu == "أشغال المجلس (الدورات)":
    st.header("📝 محاضر دورات المجلس الجماعي")
    type_s = st.selectbox("نوع الدورة", ["دورة عادية", "دورة استثنائية"])
    date_s = st.date_input("تاريخ الدورة")
    points = st.text_area("نقاط جدول الأعمال (نقطة في كل سطر)")

    if st.button("توليد محضر الدورة"):
        doc = Document(); setup_header(doc)
        title = doc.add_paragraph(f"محضر اجتماع {type_s}\nبتاريخ {date_s}")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nبناءً على القانون التنظيمي 113.14 المتعلق بالجماعات...")
        doc.add_paragraph("جدول الأعمال :").bold = True
        for p in points.split('\n'): doc.add_paragraph(f"- {p}")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر", bio.getvalue(), "PV_Session.docx")

# --- القسم الثالث: الأوامر الخدمية ---
elif menu == "الأوامر الخدمية (OS)":
    st.header("⚙️ الأوامر الخدمية (OS)")
    os_type = st.selectbox("النوع", ["OS de Commencement", "OS d'Arrêt", "OS de Reprise"])
    company = st.text_input("اسم الشركة المعنية")
    os_date = st.date_input("تاريخ سريان الأمر")

    if st.button("توليد الأمر الخدمي"):
        doc = Document(); setup_header(doc)
        title = doc.add_paragraph(f"{os_type}\nORDRE DE SERVICE")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nIl est ordonné à l'entreprise : {company}")
        doc.add_paragraph(f"De procéder à l'exécution des travaux à compter du {os_date}.")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل OS", bio.getvalue(), f"{os_type}.docx")

st.divider()
st.info("💡 ملاحظة: النماذج مدمجة وتتبع التنسيق الرسمي المعتمد.")
