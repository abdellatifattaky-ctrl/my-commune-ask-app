import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime

# دالة برمجية لتنسيق فقرات Word للعربية
def format_arabic_paragraph(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in paragraph.runs:
        run.font.rtl = True
        run.font.name = 'Arial'
        run.font.size = Pt(14)

def create_docx(title, content):
    doc = Document()
    # إضافة العنوان
    heading = doc.add_heading(title, 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # إضافة المحتوى
    paragraph = doc.add_paragraph(content)
    format_arabic_paragraph(paragraph)
    
    # حفظ الملف في ذاكرة مؤقتة لإرساله للمتصفح
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- واجهة Streamlit ---
st.title("🏛️ مولد المحاضر الرسمية (Word)")

with st.sidebar:
    st.header("إعدادات القالب")
    council_name = st.text_input("اسم الجماعة/المجلس", "جماعة الدار البيضاء")
    session_name = st.text_input("اسم الدورة", "دورة أكتوبر العادية")

tab1, tab2 = st.tabs(["✉️ الاستدعاءات", "📝 محضر الجلسة"])

with tab1:
    st.subheader("توليد استدعاءات الأعضاء")
    members = st.text_area("أدخل أسماء الأعضاء (اسم في كل سطر)")
    agenda = st.text_area("جدول الأعمال")
    
    if st.button("توليد ملف Word للاستدعاءات"):
        if members:
            member_list = members.split('\n')
            all_content = f"المملكة المغربية\nوزارة الداخلية\n{council_name}\n\n"
            for m in member_list:
                all_content += f"إلى السيد(ة): {m.strip()}\nالموضوع: استدعاء لحضور {session_name}\n\nجدول الأعمال:\n{agenda}\n"
                all_content += "-"*30 + "\n"
            
            docx_file = create_docx(f"استدعاءات {session_name}", all_content)
            st.download_button(
                label="تحميل ملف Word 📄",
                data=docx_file,
                file_name="invitations.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

with tab2:
    st.subheader("تحرير محضر الدورة الرسمي")
    decisions = st.text_area("المقررات والتوصيات")
    
    if st.button("توليد محضر Word"):
        report_text = f"""
        محضر {session_name}
        المجلس: {council_name}
        تاريخ التحرير: {datetime.now().strftime('%Y-%m-%d')}
        
        بناءً على القانون التنظيمي 113.14، تم اتخاذ المقررات التالية:
        {decisions}
        """
        docx_report = create_docx(f"محضر {session_name}", report_text)
        st.download_button(
            label="تحميل المحضر النهائي 📄",
            data=docx_report,
            file_name="minutes_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
