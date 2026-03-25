import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date

# --- دالة الترويسة الرسمية ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- واجهة التطبيق ---
st.set_page_config(page_title="منصة جماعة أسكاون", layout="wide")
st.title("🏛️ نظام تدبير دورات المجلس - أسكاون")

# القائمة الجانبية
st.sidebar.header("⚙️ إعدادات الجلسة")
sess_type = st.sidebar.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
sess_date = st.sidebar.text_input("التاريخ بالكامل", "الأربعاء 25 مارس 2026")

# --- القسم الرئيسي: جدول الأعمال والمقررون ---
st.subheader("📍 جدول الأعمال وتعيين المقررين")
st.info("قم بتحديد النقاط واسم المقرر لكل نقطة بالترتيب:")

# إنشاء جدول تفاعلي للنقاط والمقررين
if 'agenda_data' not in st.session_state:
    st.session_state.agenda_data = pd.DataFrame([
        {"رقم النقطة": 1, "موضوع النقطة": "المصادقة على الميزانية", "اسم المقرر": "أدخل اسم المقرر الأول"},
        {"رقم النقطة": 2, "موضوع النقطة": "تحويل اعتمادات", "اسم المقرر": ""},
        {"رقم النقطة": 3, "موضوع النقطة": "اتفاقية شراكة", "اسم المقرر": ""}
    ])

edited_df = st.data_editor(st.session_state.agenda_data, num_rows="dynamic", use_container_width=True)

# --- قسم الحضور ---
st.divider()
st.subheader("👥 سجل الحضور والغياب")
col1, col2, col3 = st.columns(3)
presents = col1.text_area("الأعضاء الحاضرون (الاسم والصفة)")
abs_exc = col2.text_area("الغائبون بعذر")
abs_no = col3.text_area("الغائبون بدون عذر")

# --- توليد المحضر الحرفي ---
if st.button("📄 توليد المحضر الكامل بالترتيب"):
    doc = Document(); add_askaouen_header(doc)
    
    # الديباجة الرسمية (نموذجك)
    t = doc.add_paragraph(f"محضر اجتماع دورة المجلس {sess_type}")
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True
    
    doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات...")
    doc.add_paragraph(f"في يوم {sess_date}، عقد مجلس جماعة أسكاون دورته {sess_type}...")
    
    # أولا: الحضور
    doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
    table_h = doc.add_table(rows=1, cols=3); table_h.style = 'Table Grid'
    hdr = table_h.rows[0].cells
    hdr[0].text = 'الحاضرون'; hdr[1].text = 'غائبون بعذر'; hdr[2].text = 'غائبون بدون عذر'
    r = table_h.add_row().cells
    r[0].text = presents; r[1].text = abs_exc; r[2].text = abs_no

    # ثانيا: جدول الأعمال والمقررون
    doc.add_paragraph("\nثانياً: جدول الأعمال والمداولات").bold = True
    
    for index, row in edited_df.iterrows():
        point_title = row['موضوع النقطة']
        rapporteur = row['اسم المقرر']
        
        # تنسيق كل نقطة مع مقررها
        p = doc.add_paragraph()
        p.add_run(f"النقطة {row['رقم النقطة']}: {point_title}").bold = True
        
        doc.add_paragraph(f"العرض: قدم السيد(ة) {rapporteur}، بصفته مقرراً لهذه النقطة، عرضاً مفصلاً حول الموضوع...")
        doc.add_paragraph("المناقشة: بعد فتح باب التدخلات، أبدى الأعضاء ملاحظاتهم حول...")
        doc.add_paragraph("التصويت: صادق المجلس بالإجماع/الأغلبية على هذه النقطة.\n")

    # الخاتمة
    doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
    doc.add_paragraph("رفعت الجلسة بتلاوة برقية الولاء والإخلاص المرفوعة إلى السدة العالية بالله...")
    
    doc.add_paragraph(f"\nحُرر بأسكاون في: {date.today()}")
    
    bio = BytesIO(); doc.save(bio)
    st.download_button("📥 تحميل المحضر المنسق", bio.getvalue(), "PV_Askaouen_Final.docx")

st.sidebar.divider()
st.sidebar.info("تنسيق خاص بمدير مصالح جماعة أسكاون")
