import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

# =====================
# 1. إعدادات النظام والأرشفة
# =====================
st.set_page_config(page_title="نظام جماعة أسكاون - التدبير الرقمي للمجلس", layout="wide")
DB_FILE = "askaoun_council_final.db"
ARCHIVE_FOLDER = "archive_askaoun_official"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول المتكاملة (أعضاء، دورات، حضور، قرارات)
c.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, role TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, type TEXT, date_s TEXT, time_s TEXT, agenda TEXT, chairman TEXT, secretary TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS attendance (session_id INTEGER, member_id INTEGER, status TEXT, excuse TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, session_id INTEGER, point TEXT, result TEXT, v_for INTEGER, v_against INTEGER, v_abst INTEGER)')
conn.commit()

# =====================
# 2. محرك التنسيق الإداري (Mise en Page)
# =====================
def apply_askaoun_style(doc):
    """ضبط الهوامش والخطوط وفق المعايير الإدارية المغربية"""
    for section in doc.sections:
        section.top_margin, section.bottom_margin = Cm(2.5), Cm(2.5)
        section.left_margin, section.right_margin = Cm(2.5), Cm(2.5)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Simplified Arabic'
    font.size = Pt(14)

def add_official_header(doc, title_text):
    """إضافة الرأسية الرسمية الثابتة لجماعة أسكاون"""
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
# 3. محرك توليد المحضر الراقي (برقية الولاء)
# =====================
def generate_royal_pv(s_info, attendance_df, decisions_df):
    doc = Document()
    apply_askaoun_style(doc)
    add_official_header(doc, f"محضر أشغال الدورة {s_info['type']}")

    # الافتتاحية
    p_intro = doc.add_paragraph()
    p_intro.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_intro.add_run(f"في يومه {s_info['date_s']}، وعلى الساعة {s_info['time_s']}، وبمقر جماعة أسكاون، اجتمع مجلس الجماعة في إطار دورته {s_info['type']}، برئاسة السيد {s_info['chairman']} وبحضور السيد قائد قيادة أسكاون ممثلاً للسلطة المحلية، والسيد {s_info['secretary']} كاتب المجلس.")

    # النصاب والغياب
    doc.add_heading("📌 النصاب القانوني والوضعية القانونية:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    present = attendance_df[attendance_df['status'] == "حاضر"]
    excused = attendance_df[attendance_df['status'] == "غائب بعذر"]
    unexcused = attendance_df[attendance_df['status'] == "غائب بدون عذر"]
    
    q_p = doc.add_paragraph()
    q_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    q_p.add_run(f"بناءً على المادة 42 من القانون التنظيمي 113.14، وبعد المناداة على الأعضاء، تبين حضور {len(present)} عضواً، مما يجعل النصاب القانوني مكتملاً.")
    
    if not excused.empty:
        doc.add_paragraph(f"✔️ الغياب المبرر: {', '.join(excused['name'].tolist())}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if not unexcused.empty:
        doc.add_paragraph(f"❌ الغياب غير المبرر: {', '.join(unexcused['name'].tolist())}").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # المداولات
    doc.add_heading("📑 المداولات والمصادقة:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for _, row in decisions_df.iterrows():
        dp = doc.add_paragraph()
        dp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        dp.add_run(f"النقطة: {row['point']}").bold = True
        doc.add_paragraph(f"القرار: {row['result']}. (الموافقون: {row['v_for']} | المعارضون: {row['v_against']})").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # برقية الولاء (صفحة جديدة)
    doc.add_page_break()
    add_official_header(doc, "📜 برقية ولاء وإخلاص")
    loyalty = (
        "مرفوعة إلى مقام حضرة صاحب الجلالة الملك محمد السادس نصره الله وأيده.\n\n"
        "نعم سيدي القائد الأعلى، بمناسبة اختتام أشغال الدورة " + s_info['type'] + 
        " لمجلس جماعة أسكاون، يتشرف خديم جنابكم الشريف، رئيس المجلس، أصالة عن نفسه ونيابة عن كافة أعضاء المجلس وساكنة الجماعة، "
        "بأن يرفع إلى مقامكم العالي بالله أزكى آيات الولاء والإخلاص، مشفوعة بصادق التعلق بالعرش العلوي المجيد.\n\n"
        "حفظكم الله يا مولاي بما حفظ به الذكر الحكيم، وأبقاكم ذخراً وملاذاً لهذه الأمة. إنه سميع مجيب."
    )
    p_l = doc.add_paragraph(loyalty)
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER

    path = os.path.join(ARCHIVE_FOLDER, f"Final_PV_Askaoun_{s_info['id']}.docx")
    doc.save(path)
    return path

# =====================
# 4. واجهة الاستخدام (Streamlit)
# =====================
st.sidebar.title("🏛️ بوابة جماعة أسكاون")
menu = ["👥 الأعضاء", "📅 برمجة الدورة", "📊 ضبط الحضور", "📝 تسجيل المداولات", "🚀 توليد المحضر النهائي"]
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

elif choice == "📊 ضبط الحضور":
    st.subheader("تتبع حضور الأعضاء (المادة 67)")
    s_df = pd.read_sql("SELECT id, type FROM sessions", conn)
    if not s_df.empty:
        s_id = st.selectbox("اختر الدورة", s_df['id'])
        m_df = pd.read_sql("SELECT * FROM members", conn)
        for _, m in m_df.iterrows():
            col1, col2 = st.columns(2)
            stat = col1.radio(f"{m['name']}", ["حاضر", "غائب بعذر", "غائب بدون عذر"], key=f"m_{m['id']}")
            exc = col2.text_input("العذر", key=f"e_{m['id']}")
            if st.button(f"تحديث {m['name']}", key=f"b_{m['id']}"):
                c.execute("REPLACE INTO attendance (session_id, member_id, status, excuse) VALUES (?,?,?,?)", (s_id, m['id'], stat, exc))
                conn.commit()

elif choice == "📝 تسجيل المداولات":
    st.subheader("تسجيل قرارات الدورة")
    s_df = pd.read_sql("SELECT id, type FROM sessions", conn)
    if not s_df.empty:
        s_id = st.selectbox("الدورة", s_df['id'])
        with st.form("d"):
            pt = st.text_input("النقطة")
            res = st.selectbox("القرار", ["مصادقة بالإجماع", "مصادقة بالأغلبية", "رفض"])
            v_f = st.number_input("نعم", 0)
            v_a = st.number_input("لا", 0)
            if st.form_submit_button("حفظ القرار"):
                c.execute("INSERT INTO decisions (session_id, point, result, v_for, v_against) VALUES (?,?,?,?,?)", (s_id, pt, res, v_f, v_a))
                conn.commit()

elif choice == "🚀 توليد المحضر النهائي":
    st.subheader("إصدار المحضر الرسمي الراقي")
    s_df = pd.read_sql("SELECT * FROM sessions", conn)
    if not s_df.empty:
        s_id = st.selectbox("اختر الدورة للتوليد", s_df['id'])
        if st.button("🚀 توليد المحضر وبرقية الولاء"):
            s_data = s_df[s_df['id'] == s_id].iloc[0]
            att_df = pd.read_sql(f"SELECT m.name, a.status FROM attendance a JOIN members m ON a.member_id = m.id WHERE a.session_id={s_id}", conn)
            dec_df = pd.read_sql(f"SELECT * FROM decisions WHERE session_id={s_id}", conn)
            path = generate_royal_pv(s_data, att_df, dec_df)
            with open(path, "rb") as f:
                st.download_button("📥 تحميل المحضر الرسمي", f, file_name=os.path.basename(path))
