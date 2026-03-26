import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام أشغال المجلس الجماعي", layout="wide")

# --- دالة تنسيق ملف Word للعربية ---
def create_docx(title, content_list):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(14)

    # العنوان
    heading = doc.add_heading(title, 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for item in content_list:
        p = doc.add_paragraph(item)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.rtl = True
        
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- واجهة المستخدم ---
st.title("🏛️ نظام الإدارة الشاملة لأشغال المجلس")
st.info("هذا النظام مصمم وفق القانون التنظيمي 113.14")

# مدخلات عامة في القائمة الجانبية
with st.sidebar:
    st.header("📋 معلومات الدورة")
    council = st.text_input("الجماعة/المجلس", "جماعة الدار البيضاء")
    s_type = st.selectbox("نوع الدورة", ["دورة عادية", "دورة استثنائية"])
    s_date = st.date_input("تاريخ الانعقاد")
    s_time = st.time_input("ساعة الانعقاد")
    city = st.text_input("المدينة", "الدار البيضاء")

# التبويبات لتنظيم أشغال المجلس
tab1, tab2, tab3, tab4 = st.tabs(["✉️ الاستدعاءات", "👥 لائحة الحضور", "📝 المحاضر والمقررات", "⚖️ نصوص قانونية"])

# --- 1. الاستدعاءات ---
with tab1:
    st.subheader("توليد استدعاءات الأعضاء")
    members_raw = st.text_area("أدخل أسماء الأعضاء (اسم في كل سطر)", "السيد أحمد العلمي\nالسيدة فاطمة الزهراء")
    agenda = st.text_area("جدول أعمال الدورة")
    
    if st.button("تجهيز ملف الاستدعاءات (Word)"):
        members = [m.strip() for m in members_raw.split('\n') if m.strip()]
        full_text = []
        for m in members:
            txt = f"""
            المملكة المغربية - وزارة الداخلية
            جماعة: {council}
            
            إلى السيد(ة): {m}
            الموضوع: استدعاء لحضور {s_type}
            
            بناءً على القانون التنظيمي 113.14، يتشرف رئيس المجلس بدعوتكم لحضور أشغال الدورة 
            المقرر عقدها يوم {s_date} في تمام الساعة {s_time}.
            
            جدول الأعمال:
            {agenda}
            
            حرر بـ {city} بتاريخ {datetime.now().date()}
            """
            full_text.append(txt)
            full_text.append("-" * 30)
        
        docx_file = create_docx(f"استدعاءات {s_type}", full_text)
        st.download_button(
            label="تحميل الاستدعاءات الآن 📄",
            data=docx_file,
            file_name="invitations.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# --- 2. لائحة الحضور ---
with tab2:
    st.subheader("ضبط النصاب القانوني")
    total_m = st.number_input("عدد الأعضاء المزاولين", min_value=1, value=10)
    present_m = st.number_input("عدد الحاضرين", min_value=0, value=0)
    
    if present_m > (total_m / 2):
        st.success(f"النصاب قانوني: {present_m}/{total_m}")
    else:
        st.error(f"النصاب غير مكتمل (المادة 42): {present_m}/{total_m}")

# --- 3. المحاضر والمقررات ---
with tab3:
    st.subheader("تحرير محضر الجلسة")
    discussions = st.text_area("ملخص المناقشات")
    results = st.text_area("المقررات المتخذة (نتائج التصويت)")
    
    if st.button("توليد المحضر النهائي"):
        report = [
            f"محضر أشغال {s_type} - {council}",
            f"بتاريخ: {s_date}",
            "ملخص المناقشات:",
            discussions,
            "المقررات المتخذة:",
            results,
            f"حرر في {city} بتاريخ {datetime.now().date()}"
        ]
        report_docx = create_docx(f"محضر {s_type}", report)
        st.download_button("تحميل المحضر النهائي 📄", report_docx, file_name="session_report.docx")

# --- 4. نصوص قانونية ---
with tab4:
    st.write("**تذكير بالمادة 35:** ترسل الاستدعاءات بجدول الأعمال إلى أعضاء المجلس 7 أيام على الأقل قبل تاريخ الدورة العادية.")
    
