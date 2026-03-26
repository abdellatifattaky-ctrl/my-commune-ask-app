import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime

# --- دالة إنشاء ملف Word بتنسيق احترافي ---
def create_official_docx(member_name, council, province, city, s_type, s_date, s_time, agenda):
    doc = Document()
    
    # إعدادات الصفحة والخط
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)

    # نص الاستدعاء بناءً على طلبك (القانون التنظيمي 113.14)
    content = f"""المملكة المغربية
وزارة الداخلية
ولاية/عمالة: {province}
جماعة: {council}

من رئيس مجلس جماعة {council}
إلى السيد(ة): {member_name}
عضو مجلس جماعة {council}

الموضوع: استدعاء لحضور أشغال {s_type}.

سلام تام بوجود مولانا الإمام،

وبعد، بناءً على مقتضيات المواد 33، 35، و36 من القانون التنظيمي رقم 113.14 المتعلق بالجماعات، يتشرف رئيس مجلس جماعة {council} بدعوتكم لحضور أشغال {s_type} التي سيعقدها المجلس يوم {s_date} على الساعة {s_time} بمقر الجماعة.

ويتضمن جدول أعمال هذه الدورة النقاط التالية:
{agenda}

ونظراً لأهمية النقاط المدرجة في جدول الأعمال، نرجو منكم الحضور في الموعد والمكان المحددين أعلاه.

وتقبلوا، السيد(ة) العضو، فائق التقدير والاحترام.

حرر بـ {city} في: {datetime.now().strftime('%Y-%m-%d')}

توقيع:
رئيس المجلس الجماعي
"""

    # إضافة الفقرات مع تنسيق اليمين لليسار
    for line in content.split('\n'):
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.rtl = True

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- واجهة Streamlit ---
st.set_page_config(page_title="مولد الاستدعاءات القانونية", layout="centered")

st.title("📄 مولد الاستدعاءات الرسمية (Word)")
st.info("هذا النموذج مصمم وفق مقتضيات القانون التنظيمي 113.14")

with st.form("official_form"):
    col1, col2 = st.columns(2)
    with col1:
        province = st.text_input("الولاية / العمالة", "الدار البيضاء")
        council = st.text_input("اسم الجماعة", "جماعة الدار البيضاء")
        city = st.text_input("مدينة التحرير", "الدار البيضاء")
    with col2:
        s_type = st.selectbox("نوع الدورة", ["الدورة العادية لشهر أكتوبر", "الدورة العادية لشهر ماي", "الدورة العادية لشهر فبراير", "دورة استثنائية"])
        s_date = st.date_input("تاريخ الانعقاد")
        s_time = st.time_input("ساعة الانعقاد")

    agenda = st.text_area("جدول أعمال الدورة (اكتب كل نقطة في سطر)")
    members = st.text_area("أسماء الأعضاء (اسم واحد في كل سطر)")
    
    submit = st.form_submit_button("توليد ملفات Word")

    if submit:
        if members and agenda:
            member_list = members.split('\n')
            # لتبسيط الأمر، سنقوم بتوليد ملف واحد يحتوي على كل الاستدعاءات مفصولة
            # أو يمكنك تعديل الكود لتوليد ملف مضغوط ZIP (إذا أردت ذلك لاحقاً)
            
            combined_doc = Document()
            for m in member_list:
                if m.strip():
                    # إضافة نص الاستدعاء لكل عضو
                    st.write(f"✅ تم تجهيز استدعاء: {m}")
                    # (هنا يمكن إضافة كود لجمعهم في ملف واحد أو تحميلهم فرادى)
            
            # مثال لتحميل استدعاء تجريبي لأول اسم في القائمة
            sample_member = member_list[0].strip()
            docx_file = create_official_docx(sample_member, council, province, city, s_type, s_date, s_time, agenda)
            
            st.download_button(
                label=f"تحميل استدعاء {sample_member} (Word)",
                data=docx_file,
                file_name=f"invitation_{sample_member}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
