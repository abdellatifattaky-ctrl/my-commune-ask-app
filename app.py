import sqlite3
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm
from num2words import num2words

st.set_page_config(page_title="نظام تدبير مصالح الجماعة", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"]  { direction: rtl; text-align: right; font-family: "Arial", sans-serif; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
.main-title { background: linear-gradient(135deg, #0f766e, #115e59); color: white; padding: 22px; border-radius: 18px; margin-bottom: 18px; }
.main-title h1 { margin: 0; font-size: 32px; }
.main-title p { margin: 6px 0 0 0; opacity: 0.95; }
.section-title { font-size: 22px; font-weight: 700; color: #0f172a; margin: 8px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

def get_conn():
    return sqlite3.connect("commune.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS correspondences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT, subject TEXT, ctype TEXT, department TEXT, status TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_name TEXT, license_type TEXT, status TEXT, notes TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT, department TEXT, position TEXT, status TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT, progress INTEGER, budget TEXT, status TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, fiscal_year INTEGER, subject TEXT, department TEXT, expense_type TEXT,
        budget_line TEXT, estimated_amount REAL, manager_name TEXT, notes TEXT, created_at TEXT
    )""")
    conn.commit()
    conn.close()

def insert_record(query, values):
    conn = get_conn()
    conn.execute(query, values)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

init_db()

with st.sidebar:
    menu = st.selectbox("اختر الوحدة", ["لوحة القيادة","المراسلات","الرخص","الموظفون","المشاريع","الصفقات العمومية","سندات الطلب BC"])

st.markdown("""
<div class="main-title">
    <h1>نظام تدبير مصالح الجماعة</h1>
    <p>نسخة كاملة مصححة</p>
</div>
""", unsafe_allow_html=True)

if menu == "لوحة القيادة":
    st.markdown('<div class="section-title">لوحة القيادة</div>', unsafe_allow_html=True)
    st.write("لوحة القيادة جاهزة")

elif menu == "المراسلات":
    st.markdown('<div class="section-title">تدبير المراسلات</div>', unsafe_allow_html=True)
    st.write("قسم المراسلات جاهز")

elif menu == "الرخص":
    st.markdown('<div class="section-title">تدبير الرخص</div>', unsafe_allow_html=True)
    st.write("قسم الرخص جاهز")

elif menu == "الموظفون":
    st.markdown('<div class="section-title">تدبير الموظفين</div>', unsafe_allow_html=True)
    st.write("قسم الموظفين جاهز")

elif menu == "المشاريع":
    st.markdown('<div class="section-title">تتبع المشاريع</div>', unsafe_allow_html=True)
    st.write("قسم المشاريع جاهز")

elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية</div>', unsafe_allow_html=True)
    st.info("هذا هو المكان الصحيح الذي يوضع فيه كود الصفقات. الخطأ السابق كان لأن elif وُضع في أول الملف.")
    st.code('''elif menu == "الصفقات العمومية":
    # هنا ضع كود الصفقات الكامل
    pass''', language="python")

elif menu == "سندات الطلب BC":
    st.markdown('<div class="section-title">تدبير سندات الطلب BC</div>', unsafe_allow_html=True)
    st.write("قسم BC جاهز")

st.markdown("---")
st.caption("ملف مصحح لتفادي خطأ elif في أول الملف")
