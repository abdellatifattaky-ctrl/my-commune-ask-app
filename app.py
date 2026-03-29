import sqlite3
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from num2words import num2words

st.set_page_config(
    page_title="نظام تدبير مصالح الجماعة",
    page_icon="🏛️",
    layout="wide",
)

st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: "Arial", sans-serif;
}
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
.main-title {
    background: linear-gradient(135deg, #0f766e, #115e59);
    color: white;
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.main-title h1 { margin: 0; font-size: 32px; }
.main-title p { margin: 6px 0 0 0; opacity: 0.95; }
.small-card {
    background: #f8fafc;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    text-align: center;
}
.small-card h3 { margin: 0; color: #0f766e; font-size: 28px; }
.small-card p { margin: 6px 0 0 0; color: #475569; }
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    margin: 8px 0 10px 0;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    background-color: #f1f5f9;
    padding: 8px 14px;
}
.stTabs [aria-selected="true"] {
    background-color: #0f766e !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

def get_conn():
    return sqlite3.connect("commune.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS correspondences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT, subject TEXT, ctype TEXT, department TEXT, status TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_name TEXT, license_type TEXT, status TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT, department TEXT, position TEXT, status TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT, progress INTEGER, budget TEXT, status TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS procurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT, subject TEXT, owner TEXT, procedure_type TEXT, estimated_cost REAL,
        fiscal_year INTEGER, department TEXT, market_type TEXT, status TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS cps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, cps_subject TEXT, execution_delay TEXT, temporary_guarantee TEXT,
        final_guarantee TEXT, payment_terms TEXT, penalties TEXT, reception_terms TEXT,
        notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS procurement_launches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, launch_date TEXT, publication_date TEXT, opening_date TEXT,
        publication_number TEXT, publication_media TEXT, visit_required TEXT, place TEXT,
        notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS procurement_openings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, session_date TEXT, session_time TEXT, chair_name TEXT,
        members TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS procurement_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, company_name TEXT, administrative_result TEXT, technical_score REAL,
        financial_offer REAL, ranking INTEGER, result TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS procurement_attributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, awarded_company TEXT, provisional_date TEXT, final_date TEXT,
        attributed_amount REAL, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS os_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, os_type TEXT, company_name TEXT, os_date TEXT,
        execution_delay TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        procurement_ref TEXT, pv_type TEXT, notes TEXT, content TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, fiscal_year INTEGER, subject TEXT, department TEXT, expense_type TEXT,
        budget_line TEXT, estimated_amount REAL, manager_name TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, consultation_date TEXT, deadline_date TEXT, consultation_mode TEXT,
        suppliers TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, supplier_name TEXT, offer_ref TEXT, offer_date TEXT, offer_amount REAL,
        offer_status TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_awards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, awarded_supplier TEXT, awarded_amount REAL, award_date TEXT,
        execution_deadline TEXT, bc_issue_date TEXT, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, notification_date TEXT, start_date TEXT, expected_delivery TEXT,
        execution_status TEXT, execution_progress INTEGER, notes TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bc_receptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bc_ref TEXT, reception_date TEXT, reception_type TEXT, conformity TEXT,
        invoice_number TEXT, invoice_date TEXT, invoice_amount REAL, payment_date TEXT,
        notes TEXT, created_at TEXT)""")
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

def count_rows(table_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    conn.close()
    return count

init_db()

with st.sidebar:
    st.markdown("## 🏛️ نظام الجماعة")
    st.markdown("إدارة يومية للمصالح والصفقات وBC")
    menu = st.selectbox("اختر الوحدة", [
        "لوحة القيادة", "المراسلات", "الرخص", "الموظفون",
        "المشاريع", "الصفقات العمومية", "سندات الطلب BC",
    ])
    st.markdown("---")
    st.write(f"**التاريخ:** {date.today()}")
    st.write("**المستخدم:** مدير المصالح")
    st.info("البيانات تحفظ محليًا في قاعدة SQLite: commune.db")

st.markdown("""
<div class="main-title">
    <h1>نظام تدبير مصالح الجماعة</h1>
    <p>نسخة احترافية جاهزة لـ GitHub و Streamlit Community Cloud</p>
</div>
""", unsafe_allow_html=True)

if menu == "لوحة القيادة":
    st.markdown('<div class="section-title">لوحة القيادة</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    tables = [("correspondences","المراسلات"),("licenses","الرخص"),("employees","الموظفون"),
              ("projects","المشاريع"),("procurements","الصفقات"),("bc_records","BC")]
    for col,(table,label) in zip(cols,tables):
        with col:
            st.markdown(f'<div class="small-card"><h3>{count_rows(table)}</h3><p>{label}</p></div>', unsafe_allow_html=True)
    st.subheader("ملخص الوضعية")
    st.dataframe([{"الوحدة": lbl, "عدد السجلات": count_rows(tbl)} for tbl,lbl in tables], use_container_width=True, hide_index=True)

elif menu == "المراسلات":
    st.markdown('<div class="section-title">تدبير المراسلات</div>', unsafe_allow_html=True)
    with st.form("correspondence_form"):
        c1, c2 = st.columns(2)
        with c1:
            reference = st.text_input("رقم المراسلة")
            ctype = st.selectbox("النوع", ["واردة", "صادرة"])
            department = st.text_input("المصلحة المعنية")
        with c2:
            subject = st.text_input("الموضوع")
            status = st.selectbox("الحالة", ["قيد المعالجة", "محالة", "منتهية"])
        if st.form_submit_button("حفظ المراسلة"):
            insert_record("INSERT INTO correspondences (reference, subject, ctype, department, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                          (reference, subject, ctype, department, status, str(date.today())))
            st.success("تم حفظ المراسلة بنجاح.")
    st.dataframe(fetch_all("SELECT * FROM correspondences ORDER BY id DESC"), use_container_width=True, hide_index=True)

elif menu == "الرخص":
    st.markdown('<div class="section-title">تدبير الرخص</div>', unsafe_allow_html=True)
    with st.form("license_form"):
        c1, c2 = st.columns(2)
        with c1:
            applicant_name = st.text_input("اسم صاحب الطلب")
            license_type = st.selectbox("نوع الرخصة", ["رخصة بناء", "رخصة سكن", "رخصة استغلال"])
        with c2:
            status = st.selectbox("الحالة", ["قيد الدراسة", "مقبولة", "مرفوضة"])
            notes = st.text_area("ملاحظات")
        if st.form_submit_button("حفظ الطلب"):
            insert_record("INSERT INTO licenses (applicant_name, license_type, status, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                          (applicant_name, license_type, status, notes, str(date.today())))
            st.success("تم حفظ الطلب.")
    st.dataframe(fetch_all("SELECT * FROM licenses ORDER BY id DESC"), use_container_width=True, hide_index=True)

elif menu == "الموظفون":
    st.markdown('<div class="section-title">تدبير الموظفين</div>', unsafe_allow_html=True)
    with st.form("employee_form"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("الاسم الكامل")
            department = st.text_input("المصلحة")
        with c2:
            position = st.text_input("الوظيفة")
            status = st.selectbox("الحالة", ["حاضر", "غائب", "في رخصة"])
        if st.form_submit_button("حفظ الموظف"):
            insert_record("INSERT INTO employees (full_name, department, position, status, created_at) VALUES (?, ?, ?, ?, ?)",
                          (full_name, department, position, status, str(date.today())))
            st.success("تم حفظ الموظف.")
    st.dataframe(fetch_all("SELECT * FROM employees ORDER BY id DESC"), use_container_width=True, hide_index=True)

elif menu == "المشاريع":
    st.markdown('<div class="section-title">تتبع المشاريع</div>', unsafe_allow_html=True)
    with st.form("project_form"):
        c1, c2 = st.columns(2)
        with c1:
            project_name = st.text_input("اسم المشروع")
            progress = st.slider("نسبة التقدم", 0, 100, 0)
        with c2:
            budget = st.text_input("الميزانية")
            status = st.selectbox("الحالة", ["متقدم", "متوسط", "متأخر"])
        if st.form_submit_button("حفظ المشروع"):
            insert_record("INSERT INTO projects (project_name, progress, budget, status, created_at) VALUES (?, ?, ?, ?, ?)",
                          (project_name, progress, budget, status, str(date.today())))
            st.success("تم حفظ المشروع.")
    rows = fetch_all("SELECT * FROM projects ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)
    for row in rows[:10]:
        st.write(f"**{row['project_name']}**")
        st.progress(int(row["progress"]))

elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية</div>', unsafe_allow_html=True)
    tabs = st.tabs(["البيانات الأساسية","CPS","Lancement","Ouverture des plis","Évaluation","Attribution","OS","PVs","سجل الصفقات"])
    with tabs[0]:
        with st.form("procurement_form"):
            c1, c2 = st.columns(2)
            with c1:
                reference = st.text_input("مرجع الصفقة")
                subject = st.text_input("موضوع الصفقة")
                owner = st.text_input("صاحب المشروع", value="الجماعة الترابية")
                procedure_type = st.selectbox("طريقة الإبرام", ["طلب عروض مفتوح","طلب عروض محدود","سند طلب","مباراة معمارية"])
                estimated_cost = st.number_input("الكلفة التقديرية", min_value=0.0, step=1000.0)
            with c2:
                fiscal_year = st.number_input("السنة المالية", min_value=2024, max_value=2100, value=2026)
                department = st.text_input("المصلحة المعنية")
                market_type = st.selectbox("نوع الصفقة", ["أشغال","توريدات","خدمات"])
                status = st.selectbox("المرحلة الحالية", ["إعداد","إطلاق","فتح الأظرفة","التقييم","الإسناد","التنفيذ"])
            if st.form_submit_button("حفظ الصفقة"):
                insert_record("""INSERT INTO procurements (reference, subject, owner, procedure_type, estimated_cost, fiscal_year, department, market_type, status, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (reference, subject, owner, procedure_type, estimated_cost, fiscal_year, department, market_type, status, str(date.today())))
                st.success("تم حفظ بيانات الصفقة.")
    with tabs[1]:
        with st.form("cps_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="cps_ref")
            cps_subject = st.text_input("موضوع CPS")
            execution_delay = st.text_input("أجل الإنجاز")
            temporary_guarantee = st.text_input("الضمان المؤقت")
            final_guarantee = st.text_input("الضمان النهائي")
            payment_terms = st.text_area("شروط الأداء")
            penalties = st.text_area("الغرامات")
            reception_terms = st.text_area("شروط الاستلام")
            notes = st.text_area("ملاحظات CPS")
            if st.form_submit_button("حفظ CPS"):
                insert_record("""INSERT INTO cps (procurement_ref, cps_subject, execution_delay, temporary_guarantee, final_guarantee, payment_terms, penalties, reception_terms, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, cps_subject, execution_delay, temporary_guarantee, final_guarantee, payment_terms, penalties, reception_terms, notes, str(date.today())))
                st.success("تم حفظ CPS.")
        st.dataframe(fetch_all("SELECT * FROM cps ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[2]:
        with st.form("launch_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="launch_ref")
            launch_date = st.date_input("تاريخ الإطلاق")
            publication_date = st.date_input("تاريخ النشر")
            opening_date = st.date_input("تاريخ فتح الأظرفة")
            publication_number = st.text_input("رقم الإعلان")
            publication_media = st.multiselect("وسائل النشر", ["بوابة الصفقات العمومية","جرائد وطنية","لوحة الإعلانات"])
            visit_required = st.selectbox("زيارة ميدانية", ["نعم","لا"])
            place = st.text_input("مكان الجلسة", value="مقر الجماعة")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ lancement"):
                insert_record("""INSERT INTO procurement_launches (procurement_ref, launch_date, publication_date, opening_date, publication_number, publication_media, visit_required, place, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, str(launch_date), str(publication_date), str(opening_date), publication_number, ", ".join(publication_media), visit_required, place, notes, str(date.today())))
                st.success("تم حفظ معطيات الإطلاق.")
        st.dataframe(fetch_all("SELECT * FROM procurement_launches ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[3]:
        with st.form("opening_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="opening_ref")
            session_date = st.date_input("تاريخ الجلسة")
            session_time = st.time_input("ساعة الجلسة")
            chair_name = st.text_input("رئيس اللجنة")
            members = st.text_area("أعضاء اللجنة")
            notes = st.text_area("ملاحظات الجلسة")
            if st.form_submit_button("حفظ جلسة الفتح"):
                insert_record("""INSERT INTO procurement_openings (procurement_ref, session_date, session_time, chair_name, members, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, str(session_date), str(session_time), chair_name, members, notes, str(date.today())))
                st.success("تم حفظ جلسة فتح الأظرفة.")
        st.dataframe(fetch_all("SELECT * FROM procurement_openings ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[4]:
        with st.form("evaluation_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="eval_ref")
            company_name = st.text_input("اسم المتنافس")
            administrative_result = st.selectbox("الملف الإداري", ["مقبول","مرفوض"])
            technical_score = st.number_input("التنقيط التقني", min_value=0.0, max_value=100.0, step=1.0)
            financial_offer = st.number_input("العرض المالي", min_value=0.0, step=1000.0)
            ranking = st.number_input("الترتيب", min_value=1, step=1)
            result = st.selectbox("النتيجة", ["مقبول","مقصى"])
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ التقييم"):
                insert_record("""INSERT INTO procurement_evaluations (procurement_ref, company_name, administrative_result, technical_score, financial_offer, ranking, result, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, company_name, administrative_result, technical_score, financial_offer, ranking, result, notes, str(date.today())))
                st.success("تم حفظ التقييم.")
        st.dataframe(fetch_all("SELECT * FROM procurement_evaluations ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[5]:
        with st.form("attribution_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="attr_ref")
            awarded_company = st.text_input("نائل الصفقة")
            provisional_date = st.date_input("تاريخ الإسناد المؤقت")
            final_date = st.date_input("تاريخ الإسناد النهائي")
            attributed_amount = st.number_input("مبلغ الإسناد", min_value=0.0, step=1000.0)
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ الإسناد"):
                insert_record("""INSERT INTO procurement_attributions (procurement_ref, awarded_company, provisional_date, final_date, attributed_amount, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, awarded_company, str(provisional_date), str(final_date), attributed_amount, notes, str(date.today())))
                st.success("تم حفظ الإسناد.")
        st.dataframe(fetch_all("SELECT * FROM procurement_attributions ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[6]:
        with st.form("os_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="os_ref")
            os_type = st.selectbox("نوع الأمر بالخدمة", ["OS Notification","OS Commencement"])
            company_name = st.text_input("اسم المقاولة")
            os_date = st.date_input("تاريخ OS")
            execution_delay = st.text_input("أجل التنفيذ")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ OS"):
                insert_record("""INSERT INTO os_orders (procurement_ref, os_type, company_name, os_date, execution_delay, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                              (procurement_ref, os_type, company_name, str(os_date), execution_delay, notes, str(date.today())))
                st.success("تم حفظ OS.")
        st.dataframe(fetch_all("SELECT * FROM os_orders ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[7]:
        procurement_ref = st.text_input("مرجع الصفقة", key="pv_ref")
        pv_type = st.selectbox("نوع المحضر", ["PV ouverture des plis","PV évaluation technique","PV évaluation financière","PV attribution provisoire","PV attribution définitive","PV réception provisoire","PV réception définitive"])
        pv_notes = st.text_area("ملاحظات المحضر")
        pv_content = st.text_area("محتوى المحضر", height=260)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("حفظ PV"):
                insert_record("INSERT INTO pvs (procurement_ref, pv_type, notes, content, created_at) VALUES (?, ?, ?, ?, ?)",
                              (procurement_ref, pv_type, pv_notes, pv_content, str(date.today())))
                st.success("تم حفظ المحضر.")
        with c2:
            st.download_button("تحميل المحضر", data=pv_content if pv_content else "لا يوجد محتوى",
                               file_name=f"{pv_type.replace(' ', '_')}.txt", mime="text/plain")
        st.dataframe(fetch_all("SELECT * FROM pvs ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with tabs[8]:
        st.dataframe(fetch_all("SELECT * FROM procurements ORDER BY id DESC"), use_container_width=True, hide_index=True)

elif menu == "سندات الطلب BC":
    st.markdown('<div class="section-title">تدبير سندات الطلب BC</div>', unsafe_allow_html=True)
    bc_tabs = st.tabs(["المعطيات الأساسية","الاستشارة","العروض","Comparatif","المحاضر","الإسناد","التنفيذ","الاستلام والأداء","رسالة الاستشارة","إشعار الإسناد","سجل BC"])

    with bc_tabs[0]:
        with st.form("bc_basic_form"):
            bc_ref = st.text_input("رقم سند الطلب")
            fiscal_year = st.number_input("السنة", min_value=2024, max_value=2100, value=2026)
            subject = st.text_input("موضوع سند الطلب")
            department = st.text_input("المصلحة المعنية")
            expense_type = st.selectbox("نوع النفقة", ["توريدات","خدمات","أشغال"])
            budget_line = st.text_input("السطر الميزانياتي")
            estimated_amount = st.number_input("الكلفة التقديرية", min_value=0.0, step=100.0)
            manager_name = st.text_input("المسؤول عن الملف")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ BC"):
                insert_record("""INSERT INTO bc_records (bc_ref, fiscal_year, subject, department, expense_type, budget_line, estimated_amount, manager_name, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, fiscal_year, subject, department, expense_type, budget_line, estimated_amount, manager_name, notes, str(date.today())))
                st.success("تم حفظ سند الطلب.")
    with bc_tabs[1]:
        with st.form("bc_consultation_form"):
            bc_ref = st.text_input("رقم BC", key="bc_cons_ref")
            consultation_date = st.date_input("تاريخ الاستشارة")
            deadline_date = st.date_input("آخر أجل للتوصل بالعروض")
            consultation_mode = st.selectbox("طريقة الاستشارة", ["يدوي","بريد إلكتروني","مراسلة","هاتف مع تأكيد"])
            suppliers = st.text_area("الموردون أو المقاولات المستشارة")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ الاستشارة"):
                insert_record("""INSERT INTO bc_consultations (bc_ref, consultation_date, deadline_date, consultation_mode, suppliers, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, str(consultation_date), str(deadline_date), consultation_mode, suppliers, notes, str(date.today())))
                st.success("تم حفظ الاستشارة.")
        st.dataframe(fetch_all("SELECT * FROM bc_consultations ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with bc_tabs[2]:
        with st.form("bc_offer_form"):
            bc_ref = st.text_input("رقم BC", key="bc_offer_ref")
            supplier_name = st.text_input("اسم المورد أو المقاولة")
            offer_ref = st.text_input("رقم العرض")
            offer_date = st.date_input("تاريخ التوصل")
            offer_amount = st.number_input("مبلغ العرض", min_value=0.0, step=100.0)
            offer_status = st.selectbox("وضعية العرض", ["مقبول","مرفوض","قيد الدراسة"])
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ العرض"):
                insert_record("""INSERT INTO bc_offers (bc_ref, supplier_name, offer_ref, offer_date, offer_amount, offer_status, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, supplier_name, offer_ref, str(offer_date), offer_amount, offer_status, notes, str(date.today())))
                st.success("تم حفظ العرض.")
        st.dataframe(fetch_all("SELECT * FROM bc_offers ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with bc_tabs[3]:
        st.subheader("📊 جدول مقارنة الأثمان")
        bc_refs = [r["bc_ref"] for r in fetch_all("SELECT bc_ref FROM bc_records WHERE bc_ref IS NOT NULL AND bc_ref != '' ORDER BY id DESC")]
        if bc_refs:
            selected_bc = st.selectbox("اختر BC", bc_refs, key="comp_bc")
            offers = fetch_all("""SELECT supplier_name, offer_amount, offer_status, notes FROM bc_offers WHERE bc_ref = ? ORDER BY offer_amount ASC""", (selected_bc,))
            if offers:
                df = pd.DataFrame([{"المورد": r["supplier_name"], "المبلغ": r["offer_amount"], "الحالة": r["offer_status"], "ملاحظات": r["notes"]} for r in offers])
                st.dataframe(df, use_container_width=True, hide_index=True)
                best = min(offers, key=lambda x: x["offer_amount"])
                st.success(f"أقل عرض: {best['supplier_name']} - {best['offer_amount']} درهم")
            else:
                st.warning("لا توجد عروض لهذا BC.")
        else:
            st.warning("لا توجد سندات طلب محفوظة.")
    with bc_tabs[4]:
        def format_to_words_fr(amount_str):
            try:
                val = float(str(amount_str).replace(' ', '').replace(',', ''))
                words = num2words(val, lang='fr').upper()
                cents = int(round((val - int(val)) * 100))
                text = f"{words} DIRHAMS"
                if cents > 0:
                    text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
                else:
                    text += " ,00CTS"
                return text
            except:
                return "________________"

        st.subheader("🏛️ نظام استخراج محاضر BC")

        with st.expander("📝 Détails Administratifs", expanded=True):
            c1, c2 = st.columns(2)
            num_bc = c1.text_input("N° BC", "01/ASK/2026")
            date_pub = c2.date_input("Date de publication", date.today())
            obj_bc = st.text_area("Objet", "Achat de matériel...")

        st.markdown("### 👥 Membres de la Commission")
        m1, m2, m3 = st.columns(3)
        p_name = m1.text_input("Président", "MOHAMED ZILALI")
        d_name = m2.text_input("Directeur du service", "M BAREK BAK")
        t_name = m3.text_input("Technicien", "ABDELLATIF ATTAKY")

        st.subheader("📊 Liste des concurrents")
        df_init = pd.DataFrame([
            {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
            {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
            {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
            {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
            {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
        ])
        data = st.data_editor(df_init, use_container_width=True)

        st.divider()
        c_pv1, c_pv2, c_pv3 = st.columns(3)
        pv_num = c_pv1.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
        reunion_date = c_pv3.date_input("Date de la séance", date.today())
        reunion_hour = c_pv2.text_input("Heure", "10h00mn")

        is_infructueux = False
        is_final_attr = False
        if pv_num == 6:
            res_6 = st.radio("Résultat du 6éme PV:", ["Attribution (إسناد الشركة 5)", "B.C Infructueux (غير مثمر)"])
            is_infructueux = (res_6 == "B.C Infructueux (غير مثمر)")
            is_final_attr = (res_6 == "Attribution (إسناد الشركة 5)")
        else:
            is_final_attr = st.checkbox("✅ Est-ce le PV d'attribution finale ?")

        if st.button("🚀 إنشاء المحضر"):
            doc = Document()
            section = doc.sections[0]
            section.top_margin, section.bottom_margin = Cm(2), Cm(2)
            section.left_margin, section.right_margin = Cm(2.5), Cm(2)

            header = section.header
            htable = header.add_table(1, 2, Inches(6.5))
            htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
            htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
            htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            doc.add_paragraph("\n")
            doc.add_heading(f"{pv_num}éme Procès verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

            p_obj = doc.add_paragraph()
            p_obj.add_run(f"Objet : {obj_bc}").bold = True

            doc.add_paragraph(f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée comme suit :")
            doc.add_paragraph(
                f"- M. {p_name} : Président de la commission\n"
                f"- M. {d_name} : Directeur du service\n"
                f"- M. {t_name} : Technicien de la commune"
            )

            doc.add_paragraph(
                f"S’est réunie dans la salle de réunion de la commune sur invitation du président concernant "
                f"l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')} "
                f"sur le portail des marchés publics, en application des dispositions de l’article 91 du décret "
                f"n° 2-22-431 (8 mars 2023) relatif aux marchés publics."
            )

            if pv_num == 1:
                doc.add_paragraph("Après vérification du portail des marchés publics, les soumissionnaires qui ont déposé leurs offres de prix électroniquement sont :")
                tab = doc.add_table(rows=1, cols=3)
                tab.style = 'Table Grid'
                hdr = tab.rows[0].cells
                hdr[0].text = 'Rang'
                hdr[1].text = 'Concurrent'
                hdr[2].text = 'Montant TTC'

                for _, r in data.iterrows():
                    row = tab.add_row().cells
                    row[0].text = str(r['Rang'])
                    row[1].text = str(r['Nom'])
                    row[2].text = f"{r['Montant']} MAD"

                curr_company = data.iloc[0]['Nom']
                curr_amount = data.iloc[0]['Montant']
                amt_w = format_to_words_fr(curr_amount)

                doc.add_paragraph(
                    f"\nAprès examen des offres, le président de la commission invite la société : "
                    f"{curr_company} qui est le moins disant pour un montant de {curr_amount} Dhs TTC "
                    f"({amt_w}) à confirmer son offre par lettre de confirmation."
                )
            else:
                idx = pv_num - 1 if pv_num <= 5 else 4
                prev_idx = idx - 1
                prev_company = data.iloc[prev_idx]['Nom'] if prev_idx >= 0 else ""
                curr_company = data.iloc[idx]['Nom']
                curr_amount = data.iloc[idx]['Montant']
                amt_w = format_to_words_fr(curr_amount)

                if is_infructueux:
                    doc.add_paragraph(
                        f"Après vérification du portail des marchés publics, la commission constate que "
                        f"la société {curr_company} n’a pas confirmé son offre par lettre de confirmation."
                    )
                    p_inf = doc.add_paragraph("\nPAR CONSEQUENT, LA COMMISSION DECLARE QUE CE BON DE COMMANDE EST :")
                    p_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    res_inf = doc.add_paragraph("INFRUCTUEUX")
                    res_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    res_inf.runs[0].bold = True
                    res_inf.runs[0].font.size = Pt(16)
                elif is_final_attr:
                    doc.add_paragraph(
                        f"Après vérification du portail des marchés publics, la commission constate que "
                        f"la société {curr_company} a confirmé son offre par lettre de confirmation."
                    )
                    p_res = doc.add_paragraph(
                        f"Le président VALIDE la confirmation et ATTRIBUE le bon de commande à la société "
                        f"{curr_company} pour un montant de : {curr_amount} Dhs TTC ({amt_w})."
                    )
                    p_res.runs[0].bold = True
                else:
                    doc.add_paragraph(
                        f"Après vérification du portail des marchés publics, la commission constate que "
                        f"la société {prev_company} n’a pas confirmé son offre par lettre de confirmation."
                    )
                    doc.add_paragraph(
                        f"Après écartement de la société {prev_company}, le président de la commission invite "
                        f"la société : {curr_company} qui est classé le {pv_num}éme pour un montant de "
                        f"{curr_amount} Dhs TTC ({amt_w}) à confirmer son offre par lettre de confirmation."
                    )

            doc.add_paragraph(f"\nFait à Askaouen, le {reunion_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            sig_tab = doc.add_table(rows=2, cols=3)
            sig_tab.rows[0].cells[0].text = "Le Président"
            sig_tab.rows[0].cells[1].text = "Le Directeur"
            sig_tab.rows[0].cells[2].text = "Le Technicien"
            sig_tab.rows[1].cells[0].text = p_name
            sig_tab.rows[1].cells[1].text = d_name
            sig_tab.rows[1].cells[2].text = t_name
            for r in sig_tab.rows:
                for c in r.cells:
                    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            bio = BytesIO()
            doc.save(bio)

            st.download_button(f"📥 تحميل المحضر رقم {pv_num}", bio.getvalue(), f"PV_{pv_num}_Askaouen.docx")
    with bc_tabs[5]:
        with st.form("bc_award_form"):
            bc_ref = st.text_input("رقم BC", key="bc_award_ref")
            awarded_supplier = st.text_input("نائل سند الطلب")
            awarded_amount = st.number_input("مبلغ الإسناد", min_value=0.0, step=100.0)
            award_date = st.date_input("تاريخ الإسناد")
            execution_deadline = st.text_input("أجل التنفيذ")
            bc_issue_date = st.date_input("تاريخ إصدار BC")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ الإسناد"):
                insert_record("""INSERT INTO bc_awards (bc_ref, awarded_supplier, awarded_amount, award_date, execution_deadline, bc_issue_date, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, awarded_supplier, awarded_amount, str(award_date), execution_deadline, str(bc_issue_date), notes, str(date.today())))
                st.success("تم حفظ الإسناد.")
        st.dataframe(fetch_all("SELECT * FROM bc_awards ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with bc_tabs[6]:
        with st.form("bc_execution_form"):
            bc_ref = st.text_input("رقم BC", key="bc_exec_ref")
            notification_date = st.date_input("تاريخ التبليغ")
            start_date = st.date_input("تاريخ بدء التنفيذ")
            expected_delivery = st.date_input("تاريخ التسليم المتوقع")
            execution_status = st.selectbox("حالة التنفيذ", ["لم يبدأ","جاري","تم"])
            execution_progress = st.slider("نسبة الإنجاز", 0, 100, 0)
            notes = st.text_area("ملاحظات التتبع")
            if st.form_submit_button("حفظ التنفيذ"):
                insert_record("""INSERT INTO bc_executions (bc_ref, notification_date, start_date, expected_delivery, execution_status, execution_progress, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, str(notification_date), str(start_date), str(expected_delivery), execution_status, execution_progress, notes, str(date.today())))
                st.success("تم حفظ وضعية التنفيذ.")
        st.dataframe(fetch_all("SELECT * FROM bc_executions ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with bc_tabs[7]:
        with st.form("bc_reception_form"):
            bc_ref = st.text_input("رقم BC", key="bc_reception_ref")
            reception_date = st.date_input("تاريخ الاستلام")
            reception_type = st.selectbox("نوع الاستلام", ["مؤقت","نهائي"])
            conformity = st.selectbox("المطابقة", ["مطابق","غير مطابق"])
            invoice_number = st.text_input("رقم الفاتورة")
            invoice_date = st.date_input("تاريخ الفاتورة")
            invoice_amount = st.number_input("مبلغ الفاتورة", min_value=0.0, step=100.0)
            payment_date = st.date_input("تاريخ الأداء")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ الاستلام والأداء"):
                insert_record("""INSERT INTO bc_receptions (bc_ref, reception_date, reception_type, conformity, invoice_number, invoice_date, invoice_amount, payment_date, notes, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (bc_ref, str(reception_date), reception_type, conformity, invoice_number, str(invoice_date), invoice_amount, str(payment_date), notes, str(date.today())))
                st.success("تم حفظ بيانات الاستلام والأداء.")
        st.dataframe(fetch_all("SELECT * FROM bc_receptions ORDER BY id DESC"), use_container_width=True, hide_index=True)
    with bc_tabs[8]:
        st.subheader("📨 رسالة طلب الأثمنة")
        bc_ref = st.text_input("رقم BC", key="consult_doc")
        subject = st.text_input("موضوع الطلب")
        suppliers = st.text_area("الموردون")
        if st.button("توليد رسالة الاستشارة"):
            text = f"""
المملكة المغربية
الجماعة الترابية

الموضوع: طلب أثمنة

يشرفنا أن نطلب منكم تقديم عرض أثمنة بخصوص:
{subject}

يرجى إرسال العرض في أقرب الآجال.

الموردون:
{suppliers}

رقم BC:
{bc_ref}
"""
            st.text_area("المعاينة", text, height=250)
            st.download_button("تحميل رسالة الاستشارة", data=text,
                               file_name=f"Lettre_consultation_{bc_ref if bc_ref else 'BC'}.txt", mime="text/plain")
    with bc_tabs[9]:
        st.subheader("📄 إشعار الإسناد")
        bc_ref = st.text_input("BC", key="attr_doc")
        company = st.text_input("الشركة")
        amount = st.number_input("المبلغ", min_value=0.0, step=100.0, key="attr_amount")
        if st.button("توليد إشعار الإسناد"):
            text = f"""
المملكة المغربية
الجماعة الترابية

إشعار بالإسناد

نخبركم أنه تم إسناد سند الطلب رقم {bc_ref}
لفائدتكم بمبلغ {amount} درهم.

يرجى الاتصال بالمصلحة المختصة.
"""
            st.text_area("المعاينة", text, height=220)
            st.download_button("تحميل إشعار الإسناد", data=text,
                               file_name=f"Notification_attribution_{bc_ref if bc_ref else 'BC'}.txt", mime="text/plain")
    with bc_tabs[10]:
        st.dataframe(fetch_all("SELECT * FROM bc_records ORDER BY id DESC"), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("نظام تدبير مصالح الجماعة — نسخة احترافية جاهزة للنشر")
