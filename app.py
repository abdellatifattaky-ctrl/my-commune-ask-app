import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

# =====================
# 1. الإعدادات
# =====================
st.set_page_config(page_title="نظام جماعة أسكاون v2.0", layout="wide")
DB_FILE = "askaoun_pro.db"
ARCHIVE_FOLDER = "docs_askaoun"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# الجداول
c.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, role TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, type TEXT, date_s TEXT, time_s TEXT, agenda TEXT, chairman TEXT, secretary TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, session_id INTEGER, point TEXT, result TEXT, v_for INTEGER, v_against INTEGER, v_abst INTEGER)')
conn.commit()

# =====================
# 2. وظائف التوليد التلقائي
# =====================

def add_askaoun_header(doc):
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run("المملكة المغربية\nوزارة الداخلية\nجهة سوس ماسة\nإقليم تارودانت\nدائرة تالوين\nقيادة أسكاون\nجماعة أسكاون\nمكتب المجلس")
    run.bold = True
    doc.add_paragraph("\n")

def create_attendance_sheet(s_info, members_list):
    """توليد ورقة الحضور والتوقيع"""
    doc = Document()
    add_askaoun_header(doc)
    
    title = doc.add_heading(f"ورقة الحضور وتوقيع الأعضاء\nالدورة {s_info['type']}", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"بتاريخ: {s_info['date_s']} على الساعة: {s_info['time_s']}\n").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # إنشاء جدول الحضور
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'التوقيع'
    hdr_cells[1].text = 'الصفة'
    hdr_cells[2].text = 'الاسم الكامل للعضو'
    
    for member in members_list:
        row_cells = table.add_row().cells
        row_cells[1].text = member['role']
        row_cells[2].text = member['name']
        
    f_name = f"Attendance_Sheet_{s_info['id']}.docx"
    f_path = os.path.join(ARCHIVE_FOLDER, f_name)
    doc.save(f_path)
    return f_path

def generate_official_pv(s_info, attendance, decisions):
    """توليد المحضر الرسمي النهائي"""
    doc = Document()
    add_askaoun_header(doc)
    
    title = doc.add_heading(f"محضر أشغال الدورة {s_info['type']}", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run(f"بناءً على القانون التنظيمي 113.14، اجتمع يومه {s_info['date_s']} مجلس جماعة أسكاون في دورة {s_info['type']} برئاسة السيد {s_info['chairman']} وبحضور السيد قائد قيادة أسكاون ومشاركة {len(attendance)} عضواً.").bold = False

    doc.add_heading("📌 جدول الأعمال والمداولات:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for _, row in decisions.iterrows():
        doc.add_paragraph(f"النقطة: {row['point']}", style='List Bullet').alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph(f"القرار: {row['result']} (نعم: {row['v_for']} | لا: {row['v_against']})").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    f_path = os.path.join(ARCHIVE_FOLDER, f"PV_Final_{s_info['id']}.docx")
    doc.save(f_path)
    return f_path

# =====================
# 3. الواجهة الرسومية
# =====================
st.sidebar.title("🏛️ جماعة أسكاون الرقمية")
choice = st.sidebar.selectbox("القائمة", ["👥 الأعضاء", "📅 البرمجة واللوائح", "📝 تسجيل المداولات", "🚀 المحضر النهائي"])

if choice == "👥 الأعضاء":
    st.subheader("إدارة المجلس")
    with st.form("m_form"):
        n = st.text_input("الاسم")
        r = st.selectbox("الصفة", ["رئيس", "نائب", "كاتب", "عضو"])
        if st.form_submit_button("إضافة"):
            c.execute("INSERT INTO members (name, role) VALUES (?,?)", (n, r))
            conn.commit()
    st.table(pd.read_sql("SELECT * FROM members", conn))

elif choice == "📅 البرمجة واللوائح":
    st.subheader("إعداد الدورة واللوائح")
    with st.form("s_form"):
        t = st.selectbox("الدورة", ["عادية فبراير", "عادية ماي", "عادية أكتوبر", "استثنائية"])
        d = st.date_input("التاريخ")
        ag = st.text_area("جدول الأعمال")
        if st.form_submit_button("برمجة الدورة"):
            c.execute("INSERT INTO sessions (type, date_s, agenda) VALUES (?,?,?)", (t, str(d), ag))
            conn.commit()
    
    st.write("---")
    st.write("### 📥 تحميل لوائح الدورة")
    sessions = pd.read_sql("SELECT * FROM sessions", conn)
    if not sessions.empty:
        s_id = st.selectbox("اختر الدورة", sessions['id'])
        if st.button("📄 توليد ورقة التوقيع (قائمة الحضور)"):
            s_data = sessions[sessions['id']==s_id].iloc[0]
            members = pd.read_sql("SELECT name, role FROM members", conn).to_dict('records')
            path = create_attendance_sheet(s_data, members)
            with open(path, "rb") as f:
                st.download_button("📥 تحميل ورقة التوقيع", f, file_name=os.path.basename(path))

elif choice == "📝 تسجيل المداولات":
    st.subheader("تسجيل القرارات")
    sessions = pd.read_sql("SELECT id, type FROM sessions", conn)
    if not sessions.empty:
        s_id = st.selectbox("الدورة", sessions['id'])
        with st.form("d_form"):
            pt = st.text_input("النقطة")
            res = st.selectbox("القرار", ["مصادقة", "رفض", "تأجيل"])
            v_f = st.number_input("نعم", 0)
            v_a = st.number_input("لا", 0)
            if st.form_submit_button("حفظ"):
                c.execute("INSERT INTO decisions (session_id, point, result, v_for, v_against) VALUES (?,?,?,?,?)", (s_id, pt, res, v_f, v_a))
                conn.commit()

elif choice == "🚀 المحضر النهائي":
    st.subheader("توليد المحضر الختامي")
    sessions = pd.read_sql("SELECT * FROM sessions", conn)
    if not sessions.empty:
        s_id = st.selectbox("اختر الدورة", sessions['id'])
        attendance = st.multiselect("الأعضاء الحاضرون", pd.read_sql("SELECT name FROM members", conn)['name'].tolist())
        if st.button("🚀 توليد المحضر النهائي"):
            s_data = sessions[sessions['id']==s_id].iloc[0]
            decisions = pd.read_sql(f"SELECT * FROM decisions WHERE session_id={s_id}", conn)
            path = generate_official_pv(s_data, attendance, decisions)
            with open(path, "rb") as f:
                st.download_button("📥 تحميل المحضر", f, file_name=os.path.basename(path))
