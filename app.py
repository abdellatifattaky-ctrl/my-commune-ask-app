import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

# =====================
# الإعدادات العامة
# =====================
st.set_page_config(page_title="نظام جماعة أسكاون - إدارة المجلس", layout="wide")
DB_FILE = "askaoun_council.db"
ARCHIVE_FOLDER = "archive_askaoun"
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول
c.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, role TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, type TEXT, date_s TEXT, time_s TEXT, agenda TEXT, chairman TEXT, secretary TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, session_id INTEGER, point TEXT, result TEXT, v_for INTEGER, v_against INTEGER, v_abst INTEGER)')
conn.commit()

# =====================
# محرك التوليد التلقائي (خاص بجماعة أسكاون)
# =====================

def generate_askaoun_docs(doc_type, s_info, attendance=None, decisions=None):
    doc = Document()
    
    # إعداد الخط الرسمي
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Simplified Arabic'
    font.size = Pt(14)
    
    # 1. الديباجة الرسمية الثابتة لأسكاون
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("المملكة المغربية\nوزارة الداخلية\nجهة سوس ماسة\nإقليم تارودانت\nدائرة تالوين\nقيادة أسكاون\nجماعة أسكاون\nمكتب المجلس").bold = True
    
    doc.add_paragraph("\n")

    if doc_type == "AGENDA":
        # --- توليد جدول الأعمال ---
        title = doc.add_heading(f"جدول أعمال الدورة {s_info['type']}", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nبناءً على مقتضيات القانون التنظيمي 113.14، ينهي رئيس مجلس جماعة أسكاون إلى علم السيدات والسادة الأعضاء أن الدورة {s_info['type']} ستنعقد بتاريخ {s_info['date_s']} على الساعة {s_info['time_s']} بمقر الجماعة، ويتضمن جدول أعمالها النقط التالية:").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        for p in s_info['agenda'].split('\n'):
            if p.strip(): doc.add_paragraph(p.strip(), style='List Number').alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
    elif doc_type == "PV":
        # --- توليد المحضر الرسمي ---
        title = doc.add_heading(f"محضر أشغال الدورة {s_info['type']}", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        intro = doc.add_paragraph()
        intro.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        intro.add_run(f"في يومه {s_info['date_s']}، وفي إطار مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات، اجتمع مجلس جماعة أسكاون في دورة {s_info['type']} برئاسة السيد {s_info['chairman']} وبمساعدة السيد {s_info['secretary']} كاتب المجلس، وبحضور السيد قائد قيادة أسكاون.")
        
        doc.add_heading("📌 النصاب القانوني والحضور:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph(f"حضر الاجتماع {len(attendance)} عضواً، وبعد التأكد من توفر النصاب القانوني، افتتح السيد الرئيس الجلسة مرحباً بالحضور.").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        doc.add_heading("⚖️ المداولات والقرارات:", level=2).alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for _, row in decisions.iterrows():
            dp = doc.add_paragraph()
            dp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            dp.add_run(f"النقطة: {row['point']}").bold = True
            doc.add_paragraph(f"القرار المتخذ: {row['result']} (بـ {row['v_for']} نعم، {row['v_against']} لا، {row['v_abst']} ممتنع)").alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # التوقيعات
    doc.add_paragraph("\n\n")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "توقيع كاتب المجلس"
    table.cell(0, 1).text = "توقيع رئيس مجلس جماعة أسكاون"

    name = f"{doc_type}_Askaoun_{datetime.now().strftime('%M%S')}.docx"
    path = os.path.join(ARCHIVE_FOLDER, name)
    doc.save(path)
    return path

# =====================
# الواجهة (Streamlit)
# =====================
st.sidebar.title("🏛️ بوابة جماعة أسكاون")
choice = st.sidebar.selectbox("القائمة", ["👥 الأعضاء", "📅 البرمجة والجدول", "📝 المداولات", "🚀 توليد المحضر"])

# (هنا تضع بقية الكود الخاص بالإدخال كما في الأمثلة السابقة)
# عند الضغط على أزرار التوليد، يتم استدعاء دالة generate_askaoun_docs
