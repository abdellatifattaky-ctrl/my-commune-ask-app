import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime, date, timedelta

# --- إعدادات النظام المتقدمة ---
st.set_page_config(page_title="نظام جماعة أسكاون الرقمي - النسخة الاحترافية", layout="wide")

# دالة لتنسيق ملفات Word باللغة العربية
def create_docx_official(title, paragraphs_list):
    doc = Document()
    for p_text in paragraphs_list:
        p = doc.add_paragraph(p_text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.rtl = True
        run = p.runs[0] if p.runs else p.add_run()
        run.font.name = 'Arial'
        run.font.size = Pt(12)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- إدارة قاعدة بيانات الأعضاء (في الذاكرة) ---
if 'members_list' not in st.session_state:
    st.session_state.members_list = ["رئيس المجلس", "نائب الرئيس", "كاتب المجلس"] # أمثلة افتراضية

# --- الواجهة الجانبية: معلومات ثابتة للجماعة ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Coat_of_arms_of_Morocco.svg", width=80)
    st.header("🏢 إقليم تارودانت")
    st.info("جماعة أسكاون | دائرة تاليوين | قيادة أسكاون")
    
    st.subheader("👥 سجل الأعضاء")
    new_member = st.text_input("إضافة عضو:")
    if st.button("تسجيل"):
        if new_member.strip():
            st.session_state.members_list.append(new_member.strip())
            st.rerun()
    
    if st.session_state.members_list:
        st.write(f"عدد الأعضاء: {len(st.session_state.members_list)}")
        if st.button("🗑️ مسح الكل"):
            st.session_state.members_list = []
            st.rerun()

# --- قسم الجدول الزمني القانوني (الميزة الجديدة) ---
st.title("🏛️ منصة تدبير أشغال جماعة أسكاون")

# حساب المواعيد القانونية
today = date.today()
current_year = today.year
deadlines = {
    "دورة فبراير": date(current_year, 2, 1),
    "دورة ماي": date(current_year, 5, 1),
    "دورة أكتوبر": date(current_year, 10, 1)
}

st.subheader("📅 المواعيد القانونية للدورات العادية")
cols = st.columns(3)
for i, (name, d_date) in enumerate(deadlines.items()):
    with cols[i]:
        days_diff = (d_date - today).days
        if days_diff > 0:
            st.metric(label=name, value=f"{days_diff} يوم متبقي", delta="قادمة")
        elif -30 < days_diff <= 0:
            st.success(f"أنت الآن في فترة {name}")
        else:
            st.text(f"{name} انتهت")

# --- التبويبات ---
tabs = st.tabs(["✉️ الاستدعاءات", "📋 اللجان الدائمة", "📝 المحاضر", "📊 النصاب"])

with tabs[0]:
    st.subheader("توليد استدعاءات الأعضاء")
    col1, col2 = st.columns(2)
    with col1:
        s_type = st.selectbox("نوع الدورة", ["دورة فبراير العادية", "دورة ماي العادية", "دورة أكتوبر العادية", "دورة استثنائية"])
        s_date = st.date_input("تاريخ الاجتماع", value=today + timedelta(days=8))
    with col2:
        s_time = st.time_input("التوقيت")
        
    # تنبيه قانوني برمجياً
    notice_deadline = s_date - timedelta(days=7)
    if today > notice_deadline:
        st.error(f"⚠️ تنبيه: لقد تجاوزت الأجل القانوني للإرسال (المادة 35). كان يجب الإرسال قبل {notice_deadline}")
    else:
        st.warning(f"✅ متبقي {(notice_deadline - today).days} أيام على آخر أجل لإرسال الاستدعاءات.")

    s_agenda = st.text_area("جدول الأعمال")

    if st.button("توليد ملف الاستدعاءات (Word)"):
        if not st.session_state.members_list:
            st.error("السجل فارغ! أضف أعضاء من اليمين.")
        else:
            invites = []
            for m in st.session_state.members_list:
                text = f"""
المملكة المغربية - وزارة الداخلية
عمالة تارودانت | دائرة تاليوين
قيادة أسكاون | جماعة أسكاون

من رئيس مجلس جماعة أسكاون
إلى السيد(ة): {m}

الموضوع: استدعاء لحضور أشغال {s_type}.

بناءً على القانون التنظيمي 113.14 (المواد 33، 35، 36)، يتشرف رئيس المجلس بدعوتكم لحضور أشغال {s_type} يوم {s_date} على الساعة {s_time} بمقر الجماعة.

جدول الأعمال:
{s_agenda}

توقيع رئيس المجلس
                """
                invites.append(text)
                invites.append("-" * 50)
            
            doc_data = create_docx_official(f"استدعاءات {s_type}", invites)
            st.download_button("تحميل الملف النهائي 📄", doc_data, file_name="invitations_askaoun.docx")

# --- بقية التبويبات (اللجان والمحاضر) ---
with tabs[1]:
    st.subheader("اللجان الدائمة")
    comm_name = st.selectbox("اللجنة", ["الميزانية والشؤون المالية", "المرافق العامة", "التنمية البشرية"])
    st.write(f"تقرير {comm_name} قيد التحضير...")

with tabs[2]:
    st.subheader("المحضر الرسمي")
    discussions = st.text_area("ملخص المناقشات")
    if st.button("توليد المحضر"):
        report = [f"محضر {s_type} - جماعة أسكاون", f"تاريخ: {s_date}", discussions]
        doc_report = create_docx_official("المحضر الرسمي", report)
        st.download_button("تحميل المحضر 📄", doc_report, file_name="report.docx")

with tabs[3]:
    st.subheader("احتساب النصاب")
    present = st.number_input("الحاضرون", min_value=0)
    total = len(st.session_state.members_list)
    if present > (total / 2):
        st.success(f"النصاب قانوني ({present}/{total})")
    else:
        st.error(f"النصاب غير مكتمل ({present}/{total})")
