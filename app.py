import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from io import BytesIO
from datetime import datetime

# --- إعدادات النظام ---
st.set_page_config(page_title="نظام جماعة أسكاون - الإصدار الكامل", layout="wide")

# دالة توليد ملفات Word مع ميزة فاصل الصفحات
def create_invitations_docx(members_list, session_info):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(13)

    for i, m in enumerate(members_list):
        # إضافة نص الاستدعاء
        p1 = doc.add_paragraph("المملكة المغربية\nوزارة الداخلية\nعمالة تارودانت | دائرة تاليوين\nقيادة أسكاون | جماعة أسكاون")
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.rtl = True

        p2 = doc.add_paragraph(f"\nإلى السيد(ة): {m['name']}\nالصفة: {m['role']} بمجلس جماعة أسكاون")
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.rtl = True
        p2.runs[0].bold = True

        p3 = doc.add_paragraph(f"\nالموضوع: استدعاء لحضور أشغال {session_info['type']}.")
        p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p3.paragraph_format.rtl = True
        p3.runs[0].underline = True

        content = f"""
سلام تام بوجود مولانا الإمام،

وبعد، بناءً على مقتضيات المواد 33، 35، و36 من القانون التنظيمي رقم 113.14 المتعلق بالجماعات، يتشرف رئيس مجلس جماعة أسكاون بدعوتكم لحضور أشغال {session_info['type']} التي سيعقدها المجلس يوم {session_info['date']} على الساعة {session_info['time']} بمقر الجماعة.

جدول الأعمال:
{session_info['agenda']}

نرجو منكم الحضور في الموعد والمكان المحددين أعلاه.
وتقبلوا فائق التقدير والاحترام.

حرر بأسكاون في: {datetime.now().strftime('%Y-%m-%d')}
توقيع رئيس المجلس
        """
        p4 = doc.add_paragraph(content)
        p4.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p4.paragraph_format.rtl = True

        # --- السر البرمجي: إضافة فاصل صفحات إلا بعد العضو الأخير ---
        if i < len(members_list) - 1:
            doc.add_page_break()
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# دالة عامة للمحاضر العادية
def create_general_docx(title, content_list):
    doc = Document()
    doc.add_heading(title, 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    for text in content_list:
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.rtl = True
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- إدارة قاعدة البيانات في الذاكرة ---
if 'members' not in st.session_state: st.session_state.members = []
if 'staff' not in st.session_state: st.session_state.staff = [{"name": "ممثل السلطة المحلية", "role": "قائد قيادة أسكاون"}, {"name": "مدير المصالح", "role": "مدير مصالح الجماعة"}]

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("👤 سجل أعضاء أسكاون")
    m_name = st.text_input("الاسم الكامل:")
    m_role = st.selectbox("الصفة:", ["عضو", "رئيس المجلس", "نائب الرئيس", "كاتب المجلس", "نائب الكاتب", "رئيس لجنة", "مقرر لجنة"])
    if st.button("تسجيل العضو"):
        if m_name: 
            st.session_state.members.append({"name": m_name, "role": m_role})
            st.rerun()
    
    if st.button("🗑️ مسح الكل"):
        st.session_state.members = []; st.rerun()

# --- الواجهة الرئيسية ---
st.title("🏛️ منصة تدبير أشغال جماعة أسكاون")
tabs = st.tabs(["✉️ استدعاءات (ورقة لكل عضو)", "👥 لجان دائمة", "📝 محضر الدورة والتصويت"])

# --- تبويب الاستدعاءات ---
with tabs[0]:
    st.subheader("توليد استدعاءات فردية بفاصل صفحات")
    s_type = st.selectbox("نوع الدورة", ["دورة فبراير العادية", "دورة ماي العادية", "دورة أكتوبر العادية", "دورة استثنائية"])
    col1, col2 = st.columns(2)
    with col1: s_date = st.date_input("تاريخ الاجتماع")
    with col2: s_time = st.time_input("التوقيت")
    s_agenda = st.text_area("جدول الأعمال")

    if st.button("توليد ملف Word (ورقة لكل عضو)"):
        if st.session_state.members:
            info = {'type': s_type, 'date': s_date, 'time': s_time, 'agenda': s_agenda}
            docx_inv = create_invitations_docx(st.session_state.members, info)
            st.download_button("تحميل الاستدعاءات 📄", docx_inv, file_name="invitations_askaoun.docx")
        else:
            st.error("سجل الأعضاء فارغ!")

# --- تبويب اللجان ---
with tabs[1]:
    st.subheader("محضر اللجنة الدائمة")
    c_name = st.selectbox("اللجنة:", ["لجنة الميزانية", "لجنة المرافق", "لجنة التنمية"])
    c_present = [f"{m['name']} ({m['role']})" for m in st.session_state.members + st.session_state.staff if st.checkbox(f"حاضر: {m['name']}", key=f"c_{m['name']}")]
    c_recommend = st.text_area("توصيات اللجنة")
    if st.button("توليد محضر اللجنة"):
        st.download_button("تحميل 📄", create_general_docx(f"محضر {c_name}", ["الحضور:\n" + "\n".join(c_present), f"التوصيات: {c_recommend}"]), file_name="comm.docx")

# --- تبويب المحضر والتصويت ---
with tabs[2]:
    st.subheader("نتائج التصويت والمقررات")
    s_present = [f"{m['name']} ({m['role']})" for m in st.session_state.members + st.session_state.staff if st.checkbox(f"حاضر في الدورة: {m['name']}", key=f"s_{m['name']}")]
    
    st.write("### 🗳️ التصويت على النقاط")
    num_p = st.number_input("عدد النقاط:", min_value=1, value=1)
    votes = []
    for i in range(int(num_p)):
        with st.expander(f"النقطة {i+1}"):
            title = st.text_input(f"عنوان النقطة {i+1}", key=f"t_{i}")
            y = st.number_input("موافق", key=f"y_{i}")
            n = st.number_input("معارض", key=f"n_{i}")
            votes.append(f"النقطة: {title}\nالنتيجة: {y} موافق، {n} معارض.")

    if st.button("توليد المحضر النهائي"):
        st.download_button("تحميل المحضر 📄", create_general_docx("محضر الدورة", ["الحضور:\n" + "\n".join(s_present), "التصويت:\n" + "\n".join(votes)]), file_name="final.docx")
