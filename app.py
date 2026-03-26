import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

# =====================
# 1. الإعدادات العامة والأرشفة
# =====================
st.set_page_config(page_title="نظام جماعة أسكاون الرقمي الشامل", layout="wide")
DB_FILE = "askaoun_integrated_system.db"
ARCHIVE_FOLDER = "archive_askaoun_official"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# الجداول: أعضاء، دورات، حضور، قرارات، وتقارير اللجن
c.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, role TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, type TEXT, date_s TEXT, time_s TEXT, agenda TEXT, chairman TEXT, secretary TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS attendance (session_id INTEGER, member_id INTEGER, status TEXT, excuse TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, session_id INTEGER, point TEXT, result TEXT, v_for INTEGER, v_against INTEGER, v_abst INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS committee_reports (id INTEGER PRIMARY KEY, session_id INTEGER, comm_name TEXT, comm_date TEXT, comm_content TEXT, comm_recommendations TEXT)')
conn.commit()

# =====================
# 2. محرك التنسيق الإداري (Mise en Page)
# =====================
def apply_askaoun_style(doc):
    for section in doc.sections:
        section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.5)
        section.left_margin, section.right_margin = Cm(2.5), Cm(2.5)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Simplified Arabic'
    font.size = Pt(14)

def add_official_header(doc, title_text):
    header_table = doc.add_table(rows=1, cols=2)
    header_table.width = Cm(16)
    r_cell = header_table.cell(0, 1).paragraphs[0]
    r_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_cell.add_run("المملكة المغربية\nوزارة الداخلية\nجهة سوس ماسة\nإقليم تارودانت\nدائرة تالوين\nقيادة أسكاون\nجماعة أسكاون\nمكتب المجلس").bold = True
    l_cell = header_table.cell(0, 0).paragraphs[0]
    l_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
    l_cell.add_run(f"أسكاون في: {date.today()}\nالرقم: ......./م.م/{date.today().year}")
    doc.add_paragraph("\n")
    t = doc.add_heading(title_text, level=1)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

# =====================
# 3. محركات توليد الوثائق (اللجن والمحضر الختامي)
# =====================
def generate_committee_doc(session_id, comm_name, comm_date, content, recommendations):
    doc = Document()
    apply_askaoun_style(doc)
    add_official_header(doc, f"محضر اجتماع {comm_name}")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"بناءً على مقتضيات القانون التنظيمي 113.14، اجتمعت {comm_name} بتاريخ {comm_date} بمقر الجماعة لدراسة النقط المحالة عليها من طرف مكتب المجلس.\n").bold = False
    
    doc.add_heading("📌 مداولات اللجنة:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_paragraph(content).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    doc.add_heading("💡 توصيات اللجنة:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_paragraph(recommendations).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    path = os.path.join(ARCHIVE_FOLDER, f"تقرير_{comm_name}_{session_id}.docx")
    doc.save(path)
    return path

# (دالة generate_royal_pv تبقى كما هي في الرد السابق مع برقية الولاء)

# =====================
# 4. واجهة المستخدم (Streamlit)
# =====================
st.sidebar.title("🏛️ بوابة جماعة أسكاون")
menu = ["👥 الأعضاء", "📅 برمجة الدورة", "📜 تقارير اللجان", "📊 ضبط الحضور", "📝 تسجيل المداولات", "🚀 المحضر النهائي"]
choice = st.sidebar.selectbox("القائمة الإدارية", menu)

if choice == "👥 الأعضاء":
    st.subheader("إدارة الأعضاء")
    with st.form("m"):
        n = st.text_input("الاسم الكامل")
        r = st.selectbox("الصفة", ["رئيس المجلس", "نائب الرئيس", "كاتب المجلس", "مستشار"])
        if st.form_submit_button("حفظ"):
            c.execute("INSERT INTO members (name, role) VALUES (?,?)", (n, r))
            conn.commit()
    st.table(pd.read_sql("SELECT * FROM members", conn))

elif choice == "📅 برمجة الدورة":
    st.subheader("برمجة دورة جديدة")
    with st.form("s"):
        t = st.selectbox("الدورة", ["عادية فبراير", "عادية ماي", "عادية أكتوبر", "استثنائية"])
        d = st.date_input("التاريخ")
        tm = st.time_input("التوقيت")
        chair = st.text_input("الرئيس", "رئيس المجلس")
        sec = st.text_input("الكاتب")
        ag = st.text_area("جدول الأعمال")
        if st.form_submit_button("حفظ الدورة"):
            c.execute("INSERT INTO sessions (type, date_s, time_s, agenda, chairman, secretary) VALUES (?,?,?,?,?,?)", (t, str(d), str(tm), ag, chair, sec))
            conn.commit()

elif choice == "📜 تقارير اللجان":
    st.subheader("📝 صياغة محاضر اللجان الدائمة")
    s_df = pd.read_sql("SELECT id, type FROM sessions", conn)
    if not s_df.empty:
        s_id = st.selectbox("الدورة المرتبطة", s_df['id'])
        with st.form("comm"):
            c_name = st.selectbox("اسم اللجنة", ["لجنة الميزانية والشؤون المالية", "لجنة المرافق العمومية والخدمات", "لجنة التنمية البشرية والشؤون الاجتماعية"])
            c_date = st.date_input("تاريخ اجتماع اللجنة")
            c_content = st.text_area("خلاصة المداولات (المناقشة)")
            c_recom = st.text_area("التوصيات النهائية للجنة")
            if st.form_submit_button("توليد محضر اللجنة بصيغة Word"):
                path = generate_committee_doc(s_id, c_name, str(c_date), c_content, c_recom)
                with open(path, "rb") as f:
                    st.download_button(f"📥 تحميل محضر {c_name}", f, file_name=os.path.basename(path))

# (أقسام ضبط الحضور وتسجيل المداولات والمحضر النهائي تبقى كما في النسخة السابقة لضمان التكامل)
