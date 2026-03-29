import sqlite3
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from num2words import num2words


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="نظام تدبير مصالح الجماعة",
    page_icon="🏛️",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: "Arial", sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .main-title {
        background: linear-gradient(135deg, #0f766e, #115e59);
        color: white;
        padding: 22px;
        border-radius: 18px;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }
    .main-title h1 {
        margin: 0;
        font-size: 32px;
    }
    .main-title p {
        margin: 6px 0 0 0;
        opacity: 0.95;
    }
    .small-card {
        background: #f8fafc;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .small-card h3 {
        margin: 0;
        color: #0f766e;
        font-size: 28px;
    }
    .small-card p {
        margin: 6px 0 0 0;
        color: #475569;
    }
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        margin: 8px 0 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
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
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATABASE
# =========================================================
def get_conn():
    return sqlite3.connect("commune.db", check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS correspondences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT,
            subject TEXT,
            ctype TEXT,
            department TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT,
            license_type TEXT,
            status TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            department TEXT,
            position TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            progress INTEGER,
            budget TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS procurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT,
            subject TEXT,
            owner TEXT,
            procedure_type TEXT,
            estimated_cost REAL,
            fiscal_year INTEGER,
            department TEXT,
            market_type TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS cps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            cps_subject TEXT,
            execution_delay TEXT,
            temporary_guarantee TEXT,
            final_guarantee TEXT,
            payment_terms TEXT,
            penalties TEXT,
            reception_terms TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS procurement_launches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            launch_date TEXT,
            publication_date TEXT,
            opening_date TEXT,
            publication_number TEXT,
            publication_media TEXT,
            visit_required TEXT,
            place TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS procurement_openings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            session_date TEXT,
            session_time TEXT,
            chair_name TEXT,
            members TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS procurement_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            company_name TEXT,
            administrative_result TEXT,
            technical_score REAL,
            financial_offer REAL,
            ranking INTEGER,
            result TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS procurement_attributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            awarded_company TEXT,
            provisional_date TEXT,
            final_date TEXT,
            attributed_amount REAL,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS os_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            os_type TEXT,
            company_name TEXT,
            os_date TEXT,
            execution_delay TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS pvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            pv_type TEXT,
            notes TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            fiscal_year INTEGER,
            subject TEXT,
            department TEXT,
            expense_type TEXT,
            budget_line TEXT,
            estimated_amount REAL,
            manager_name TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            consultation_date TEXT,
            deadline_date TEXT,
            consultation_mode TEXT,
            suppliers TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            supplier_name TEXT,
            offer_ref TEXT,
            offer_date TEXT,
            offer_amount REAL,
            offer_status TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            awarded_supplier TEXT,
            awarded_amount REAL,
            award_date TEXT,
            execution_deadline TEXT,
            bc_issue_date TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            notification_date TEXT,
            start_date TEXT,
            expected_delivery TEXT,
            execution_status TEXT,
            execution_progress INTEGER,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_receptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            reception_date TEXT,
            reception_type TEXT,
            conformity TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            invoice_amount REAL,
            payment_date TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS bc_opening_pvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bc_ref TEXT,
            bc_subject TEXT,
            session_date TEXT,
            session_time TEXT,
            session_place TEXT,
            chair_name TEXT,
            members TEXT,
            offers_text TEXT,
            conclusion_text TEXT,
            pv_content TEXT,
            created_at TEXT
        )
        """
    )

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


def fetch_bc_refs():
    rows = fetch_all("SELECT bc_ref FROM bc_records WHERE bc_ref IS NOT NULL AND bc_ref != '' ORDER BY id DESC")
    return [r["bc_ref"] for r in rows]


def fetch_bc_record(bc_ref):
    rows = fetch_all("SELECT * FROM bc_records WHERE bc_ref = ? ORDER BY id DESC LIMIT 1", (bc_ref,))
    return rows[0] if rows else None


def fetch_bc_offers_sorted(bc_ref):
    return fetch_all(
        """
        SELECT supplier_name, offer_ref, offer_date, offer_amount, offer_status, notes
        FROM bc_offers
        WHERE bc_ref = ?
        ORDER BY offer_amount ASC
        """,
        (bc_ref,),
    )


def format_to_words_fr(amount_value):
    try:
        val = float(amount_value)
        words = num2words(val, lang="fr").upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ,00 CTS"
        return text
    except Exception:
        return "________________"


init_db()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🏛️ نظام الجماعة")
    st.markdown("إدارة يومية للمصالح والصفقات وBC")

    menu = st.selectbox(
        "اختر الوحدة",
        [
            "لوحة القيادة",
            "المراسلات",
            "الرخص",
            "الموظفون",
            "المشاريع",
            "الصفقات العمومية",
            "سندات الطلب BC",
        ],
    )

    st.markdown("---")
    st.write(f"**التاريخ:** {date.today()}")
    st.write("**المستخدم:** مدير المصالح")
    st.info("البيانات تحفظ محليًا في قاعدة SQLite: commune.db")


# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="main-title">
        <h1>نظام تدبير مصالح الجماعة</h1>
        <p>نسخة احترافية جاهزة لـ GitHub و Streamlit Community Cloud</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DASHBOARD
# =========================================================
if menu == "لوحة القيادة":
    st.markdown('<div class="section-title">لوحة القيادة</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("correspondences")}</h3><p>المراسلات</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("licenses")}</h3><p>الرخص</p></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("employees")}</h3><p>الموظفون</p></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("projects")}</h3><p>المشاريع</p></div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("procurements")}</h3><p>الصفقات</p></div>',
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f'<div class="small-card"><h3>{count_rows("bc_records")}</h3><p>BC</p></div>',
            unsafe_allow_html=True,
        )

    st.subheader("ملخص الوضعية")
    st.dataframe(
        [
            {"الوحدة": "المراسلات", "عدد السجلات": count_rows("correspondences"), "الوضعية": "نشطة"},
            {"الوحدة": "الرخص", "عدد السجلات": count_rows("licenses"), "الوضعية": "قيد المعالجة"},
            {"الوحدة": "الموظفون", "عدد السجلات": count_rows("employees"), "الوضعية": "مستقرة"},
            {"الوحدة": "المشاريع", "عدد السجلات": count_rows("projects"), "الوضعية": "تتبع مستمر"},
            {"الوحدة": "الصفقات العمومية", "عدد السجلات": count_rows("procurements"), "الوضعية": "جارية"},
            {"الوحدة": "سندات الطلب BC", "عدد السجلات": count_rows("bc_records"), "الوضعية": "جارية"},
        ],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# CORRESPONDENCES
# =========================================================
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

        submitted = st.form_submit_button("حفظ المراسلة")
        if submitted:
            insert_record(
                "INSERT INTO correspondences (reference, subject, ctype, department, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (reference, subject, ctype, department, status, str(date.today())),
            )
            st.success("تم حفظ المراسلة بنجاح.")

    rows = fetch_all("SELECT * FROM correspondences ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)


# =========================================================
# LICENSES
# =========================================================
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

        submitted = st.form_submit_button("حفظ الطلب")
        if submitted:
            insert_record(
                "INSERT INTO licenses (applicant_name, license_type, status, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (applicant_name, license_type, status, notes, str(date.today())),
            )
            st.success("تم حفظ الطلب.")

    rows = fetch_all("SELECT * FROM licenses ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)


# =========================================================
# EMPLOYEES
# =========================================================
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

        submitted = st.form_submit_button("حفظ الموظف")
        if submitted:
            insert_record(
                "INSERT INTO employees (full_name, department, position, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (full_name, department, position, status, str(date.today())),
            )
            st.success("تم حفظ الموظف.")

    rows = fetch_all("SELECT * FROM employees ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)


# =========================================================
# PROJECTS
# =========================================================
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

        submitted = st.form_submit_button("حفظ المشروع")
        if submitted:
            insert_record(
                "INSERT INTO projects (project_name, progress, budget, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (project_name, progress, budget, status, str(date.today())),
            )
            st.success("تم حفظ المشروع.")

    rows = fetch_all("SELECT * FROM projects ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("نسب التقدم")
    for row in rows[:10]:
        st.write(f"**{row['project_name']}**")
        st.progress(int(row["progress"]))


# =========================================================
# PROCUREMENTS
# =========================================================
elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية</div>', unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "البيانات الأساسية",
            "CPS",
            "Lancement",
            "Ouverture des plis",
            "Évaluation",
            "Attribution",
            "OS",
            "PVs",
            "سجل الصفقات",
        ]
    )

    with tabs[0]:
        with st.form("procurement_form"):
            c1, c2 = st.columns(2)
            with c1:
                reference = st.text_input("مرجع الصفقة")
                subject = st.text_input("موضوع الصفقة")
                owner = st.text_input("صاحب المشروع", value="الجماعة الترابية")
                procedure_type = st.selectbox(
                    "طريقة الإبرام",
                    ["طلب عروض مفتوح", "طلب عروض محدود", "سند طلب", "مباراة معمارية"],
                )
                estimated_cost = st.number_input("الكلفة التقديرية", min_value=0.0, step=1000.0)
            with c2:
                fiscal_year = st.number_input("السنة المالية", min_value=2024, max_value=2100, value=2026)
                department = st.text_input("المصلحة المعنية")
                market_type = st.selectbox("نوع الصفقة", ["أشغال", "توريدات", "خدمات"])
                status = st.selectbox("المرحلة الحالية", ["إعداد", "إطلاق", "فتح الأظرفة", "التقييم", "الإسناد", "التنفيذ"])

            submitted = st.form_submit_button("حفظ الصفقة")
            if submitted:
                insert_record(
                    """
                    INSERT INTO procurements
                    (reference, subject, owner, procedure_type, estimated_cost, fiscal_year, department, market_type, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference,
                        subject,
                        owner,
                        procedure_type,
                        estimated_cost,
                        fiscal_year,
                        department,
                        market_type,
                        status,
                        str(date.today()),
                    ),
                )
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

            submitted = st.form_submit_button("حفظ CPS")
            if submitted:
                insert_record(
                    """
                    INSERT INTO cps
                    (procurement_ref, cps_subject, execution_delay, temporary_guarantee, final_guarantee, payment_terms, penalties, reception_terms, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        cps_subject,
                        execution_delay,
                        temporary_guarantee,
                        final_guarantee,
                        payment_terms,
                        penalties,
                        reception_terms,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ CPS.")

        st.dataframe(fetch_all("SELECT * FROM cps ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[2]:
        with st.form("launch_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="launch_ref")
            launch_date = st.date_input("تاريخ الإطلاق")
            publication_date = st.date_input("تاريخ النشر")
            opening_date = st.date_input("تاريخ فتح الأظرفة")
            publication_number = st.text_input("رقم الإعلان")
            publication_media = st.multiselect("وسائل النشر", ["بوابة الصفقات العمومية", "جرائد وطنية", "لوحة الإعلانات"])
            visit_required = st.selectbox("زيارة ميدانية", ["نعم", "لا"])
            place = st.text_input("مكان الجلسة", value="مقر الجماعة")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ lancement")
            if submitted:
                insert_record(
                    """
                    INSERT INTO procurement_launches
                    (procurement_ref, launch_date, publication_date, opening_date, publication_number, publication_media, visit_required, place, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        str(launch_date),
                        str(publication_date),
                        str(opening_date),
                        publication_number,
                        ", ".join(publication_media),
                        visit_required,
                        place,
                        notes,
                        str(date.today()),
                    ),
                )
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

            submitted = st.form_submit_button("حفظ جلسة الفتح")
            if submitted:
                insert_record(
                    """
                    INSERT INTO procurement_openings
                    (procurement_ref, session_date, session_time, chair_name, members, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        str(session_date),
                        str(session_time),
                        chair_name,
                        members,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ جلسة فتح الأظرفة.")

        st.dataframe(fetch_all("SELECT * FROM procurement_openings ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[4]:
        with st.form("evaluation_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="eval_ref")
            company_name = st.text_input("اسم المتنافس")
            administrative_result = st.selectbox("الملف الإداري", ["مقبول", "مرفوض"])
            technical_score = st.number_input("التنقيط التقني", min_value=0.0, max_value=100.0, step=1.0)
            financial_offer = st.number_input("العرض المالي", min_value=0.0, step=1000.0)
            ranking = st.number_input("الترتيب", min_value=1, step=1)
            result = st.selectbox("النتيجة", ["مقبول", "مقصى"])
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ التقييم")
            if submitted:
                insert_record(
                    """
                    INSERT INTO procurement_evaluations
                    (procurement_ref, company_name, administrative_result, technical_score, financial_offer, ranking, result, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        company_name,
                        administrative_result,
                        technical_score,
                        financial_offer,
                        ranking,
                        result,
                        notes,
                        str(date.today()),
                    ),
                )
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

            submitted = st.form_submit_button("حفظ الإسناد")
            if submitted:
                insert_record(
                    """
                    INSERT INTO procurement_attributions
                    (procurement_ref, awarded_company, provisional_date, final_date, attributed_amount, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        awarded_company,
                        str(provisional_date),
                        str(final_date),
                        attributed_amount,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ الإسناد.")

        st.dataframe(fetch_all("SELECT * FROM procurement_attributions ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[6]:
        with st.form("os_form"):
            procurement_ref = st.text_input("مرجع الصفقة", key="os_ref")
            os_type = st.selectbox("نوع الأمر بالخدمة", ["OS Notification", "OS Commencement"])
            company_name = st.text_input("اسم المقاولة")
            os_date = st.date_input("تاريخ OS")
            execution_delay = st.text_input("أجل التنفيذ")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ OS")
            if submitted:
                insert_record(
                    """
                    INSERT INTO os_orders
                    (procurement_ref, os_type, company_name, os_date, execution_delay, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        procurement_ref,
                        os_type,
                        company_name,
                        str(os_date),
                        execution_delay,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ OS.")

        st.dataframe(fetch_all("SELECT * FROM os_orders ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[7]:
        procurement_ref = st.text_input("مرجع الصفقة", key="pv_ref")
        pv_type = st.selectbox(
            "نوع المحضر",
            [
                "PV ouverture des plis",
                "PV évaluation technique",
                "PV évaluation financière",
                "PV attribution provisoire",
                "PV attribution définitive",
                "PV réception provisoire",
                "PV réception définitive",
            ],
        )
        pv_notes = st.text_area("ملاحظات المحضر")
        pv_content = st.text_area("محتوى المحضر", height=260)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("حفظ PV"):
                insert_record(
                    "INSERT INTO pvs (procurement_ref, pv_type, notes, content, created_at) VALUES (?, ?, ?, ?, ?)",
                    (procurement_ref, pv_type, pv_notes, pv_content, str(date.today())),
                )
                st.success("تم حفظ المحضر.")
        with c2:
            st.download_button(
                "تحميل المحضر",
                data=pv_content if pv_content else "لا يوجد محتوى",
                file_name=f"{pv_type.replace(' ', '_')}.txt",
                mime="text/plain",
            )

        st.dataframe(fetch_all("SELECT * FROM pvs ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[8]:
        st.dataframe(fetch_all("SELECT * FROM procurements ORDER BY id DESC"), use_container_width=True, hide_index=True)


# =========================================================
# BC
# =========================================================
elif menu == "سندات الطلب BC":
    st.markdown('<div class="section-title">تدبير سندات الطلب BC</div>', unsafe_allow_html=True)

    bc_tabs = st.tabs(
        [
            "المعطيات الأساسية",
            "الاستشارة",
            "العروض",
            "Comparatif",
            "محضر افتتاح BC",
            "الإسناد",
            "التنفيذ",
            "الاستلام والأداء",
            "رسالة الاستشارة",
            "إشعار الإسناد",
            "سجل BC",
        ]
    )

    with bc_tabs[0]:
        with st.form("bc_basic_form"):
            bc_ref = st.text_input("رقم سند الطلب")
            fiscal_year = st.number_input("السنة", min_value=2024, max_value=2100, value=2026)
            subject = st.text_input("موضوع سند الطلب")
            department = st.text_input("المصلحة المعنية")
            expense_type = st.selectbox("نوع النفقة", ["توريدات", "خدمات", "أشغال"])
            budget_line = st.text_input("السطر الميزانياتي")
            estimated_amount = st.number_input("الكلفة التقديرية", min_value=0.0, step=100.0)
            manager_name = st.text_input("المسؤول عن الملف")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ BC")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_records
                    (bc_ref, fiscal_year, subject, department, expense_type, budget_line, estimated_amount, manager_name, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        fiscal_year,
                        subject,
                        department,
                        expense_type,
                        budget_line,
                        estimated_amount,
                        manager_name,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ سند الطلب.")

    with bc_tabs[1]:
        with st.form("bc_consultation_form"):
            bc_ref = st.text_input("رقم BC", key="bc_cons_ref")
            consultation_date = st.date_input("تاريخ الاستشارة")
            deadline_date = st.date_input("آخر أجل للتوصل بالعروض")
            consultation_mode = st.selectbox("طريقة الاستشارة", ["يدوي", "بريد إلكتروني", "مراسلة", "هاتف مع تأكيد"])
            suppliers = st.text_area("الموردون أو المقاولات المستشارة")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ الاستشارة")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_consultations
                    (bc_ref, consultation_date, deadline_date, consultation_mode, suppliers, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        str(consultation_date),
                        str(deadline_date),
                        consultation_mode,
                        suppliers,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ الاستشارة.")

        st.dataframe(fetch_all("SELECT * FROM bc_consultations ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[2]:
        with st.form("bc_offer_form"):
            bc_ref = st.text_input("رقم BC", key="bc_offer_ref")
            supplier_name = st.text_input("اسم المورد أو المقاولة")
            offer_ref = st.text_input("رقم العرض")
            offer_date = st.date_input("تاريخ التوصل")
            offer_amount = st.number_input("مبلغ العرض", min_value=0.0, step=100.0)
            offer_status = st.selectbox("وضعية العرض", ["مقبول", "مرفوض", "قيد الدراسة"])
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ العرض")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_offers
                    (bc_ref, supplier_name, offer_ref, offer_date, offer_amount, offer_status, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        supplier_name,
                        offer_ref,
                        str(offer_date),
                        offer_amount,
                        offer_status,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ العرض.")

        st.dataframe(fetch_all("SELECT * FROM bc_offers ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[3]:
        st.subheader("📊 جدول مقارنة الأثمان")

        bc_refs = fetch_bc_refs()
        if bc_refs:
            selected_bc = st.selectbox("اختر BC", bc_refs, key="comp_bc")
            offers = fetch_bc_offers_sorted(selected_bc)

            if offers:
                df = pd.DataFrame(
                    [
                        {
                            "المورد": r["supplier_name"],
                            "المبلغ": r["offer_amount"],
                            "الحالة": r["offer_status"],
                            "ملاحظات": r["notes"],
                        }
                        for r in offers
                    ]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)

                best = min(offers, key=lambda x: x["offer_amount"])
                st.success(f"أقل عرض: {best['supplier_name']} - {best['offer_amount']} درهم")
            else:
                st.warning("لا توجد عروض لهذا BC.")
        else:
            st.warning("لا توجد سندات طلب محفوظة.")

    with bc_tabs[4]:
        st.subheader("🧾 محاضر فتح ودراسة العروض - BC")

        bc_refs = fetch_bc_refs()
        if not bc_refs:
            st.warning("لا توجد أي سندات طلب محفوظة بعد.")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                selected_bc = st.selectbox("اختر رقم BC", bc_refs, key="pv_bc_ref")
            with col_b:
                pv_num = st.selectbox("رقم المحضر", [1, 2, 3, 4, 5, 6], key="pv_number")

            bc_info = fetch_bc_record(selected_bc)
            bc_offers = fetch_bc_offers_sorted(selected_bc)

            if bc_info:
                st.info(f"موضوع BC: {bc_info.get('subject', '')}")

            st.subheader("👥 اللجنة")
            c1, c2, c3 = st.columns(3)
            p_name = c1.text_input("Président", "MOHAMED ZILALI")
            d_name = c2.text_input("Directeur du service", "M BAREK BAK")
            t_name = c3.text_input("Technicien", "ABDELLATIF ATTAKY")

            st.subheader("🗓️ الجلسة")
            c4, c5, c6 = st.columns(3)
            reunion_date = c4.date_input("تاريخ الجلسة", date.today(), key="pv_session_date")
            reunion_hour = c5.text_input("الساعة", "10h00mn")
            session_place = c6.text_input("المكان", "Salle de réunion de la commune")

            st.subheader("📊 العروض المسجلة")
            if bc_offers:
                offers_df = pd.DataFrame(
                    [
                        {
                            "Rang": i + 1,
                            "Nom": r["supplier_name"],
                            "Montant": r["offer_amount"],
                            "Réf offre": r["offer_ref"],
                            "Date offre": r["offer_date"],
                            "Statut": r["offer_status"],
                            "Notes": r["notes"],
                        }
                        for i, r in enumerate(bc_offers)
                    ]
                )
                st.dataframe(offers_df, use_container_width=True, hide_index=True)
            else:
                st.warning("لا توجد عروض محفوظة لهذا BC في جدول العروض.")

            is_infructueux = False
            is_final_attr = False

            if pv_num == 6:
                res_6 = st.radio(
                    "نتيجة المحضر 6",
                    ["Attribution (إسناد)", "B.C Infructueux (غير مثمر)"],
                )
                is_infructueux = res_6 == "B.C Infructueux (غير مثمر)"
                is_final_attr = res_6 == "Attribution (إسناد)"
            else:
                is_final_attr = st.checkbox("هل هذا محضر إسناد نهائي؟")

            if st.button("🚀 إنشاء المحضر Word"):
                if not bc_info:
                    st.error("تعذر جلب معطيات BC.")
                elif not bc_offers:
                    st.error("لا توجد عروض مرتبطة بهذا BC.")
                else:
                    doc = Document()
                    section = doc.sections[0]

                    header = section.header
                    htable = header.add_table(1, 2)
                    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE"
                    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nالجماعة"
                    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

                    doc.add_paragraph("")
                    doc.add_heading(f"{pv_num}ème Procès-verbal", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("De la commission d’ouverture des plis\nProcédure Bon de commande").alignment = WD_ALIGN_PARAGRAPH.CENTER

                    obj_bc = bc_info.get("subject", "")
                    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
                    doc.add_paragraph(
                        f"Le {reunion_date.strftime('%d/%m/%Y')} à {reunion_hour}, la commission d’ouverture des plis composée comme suit :"
                    )
                    doc.add_paragraph(
                        f"- M. {p_name} : Président de la commission\n"
                        f"- M. {d_name} : Directeur du service\n"
                        f"- M. {t_name} : Technicien de la commune"
                    )

                    doc.add_paragraph(
                        f"S’est réunie dans {session_place} concernant l’avis d’achat du bon de commande n° {selected_bc}, "
                        f"en application des dispositions réglementaires relatives aux marchés publics."
                    )

                    if pv_num == 1:
                        doc.add_paragraph("Après vérification, les soumissionnaires ayant déposé leurs offres sont :")
                        tab = doc.add_table(rows=1, cols=3)
                        tab.style = "Table Grid"
                        hdr = tab.rows[0].cells
                        hdr[0].text = "Rang"
                        hdr[1].text = "Concurrent"
                        hdr[2].text = "Montant TTC"

                        for i, r in enumerate(bc_offers):
                            row = tab.add_row().cells
                            row[0].text = str(i + 1)
                            row[1].text = str(r["supplier_name"])
                            row[2].text = f"{r['offer_amount']} MAD"

                        curr_company = bc_offers[0]["supplier_name"]
                        curr_amount = bc_offers[0]["offer_amount"]
                        amt_w = format_to_words_fr(curr_amount)

                        doc.add_paragraph(
                            f"\nAprès examen des offres, le président de la commission invite la société : "
                            f"{curr_company} qui est le moins disant pour un montant de {curr_amount} Dhs TTC "
                            f"({amt_w}) à confirmer son offre par lettre de confirmation."
                        )
                    else:
                        idx = pv_num - 1 if pv_num <= 5 else 4

                        if idx >= len(bc_offers):
                            doc.add_paragraph(
                                "Le nombre d’offres disponibles est insuffisant pour générer ce procès-verbal."
                            )
                        else:
                            curr_company = bc_offers[idx]["supplier_name"]
                            curr_amount = bc_offers[idx]["offer_amount"]
                            amt_w = format_to_words_fr(curr_amount)

                            prev_company = ""
                            if idx - 1 >= 0 and idx - 1 < len(bc_offers):
                                prev_company = bc_offers[idx - 1]["supplier_name"]

                            if is_infructueux:
                                doc.add_paragraph(
                                    f"Après vérification, la commission constate que la société {curr_company} "
                                    f"n’a pas confirmé son offre par lettre de confirmation."
                                )
                                p_inf = doc.add_paragraph(
                                    "\nPAR CONSÉQUENT, LA COMMISSION DÉCLARE QUE CE BON DE COMMANDE EST :"
                                )
                                p_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                res_inf = doc.add_paragraph("INFRUCTUEUX")
                                res_inf.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                res_inf.runs[0].bold = True
                                res_inf.runs[0].font.size = Pt(16)

                            elif is_final_attr:
                                doc.add_paragraph(
                                    f"Après vérification, la commission constate que la société {curr_company} "
                                    f"a confirmé son offre par lettre de confirmation."
                                )
                                p_res = doc.add_paragraph(
                                    f"Le président valide la confirmation et attribue le bon de commande "
                                    f"à la société {curr_company} pour un montant de : {curr_amount} Dhs TTC ({amt_w})."
                                )
                                p_res.runs[0].bold = True

                            else:
                                doc.add_paragraph(
                                    f"Après vérification, la commission constate que la société {prev_company} "
                                    f"n’a pas confirmé son offre par lettre de confirmation."
                                )
                                doc.add_paragraph(
                                    f"Après écartement de la société {prev_company}, le président de la commission "
                                    f"invite la société : {curr_company} classée au rang {pv_num} pour un montant de "
                                    f"{curr_amount} Dhs TTC ({amt_w}) à confirmer son offre par lettre de confirmation."
                                )

                    doc.add_paragraph(
                        f"\nFait à la commune, le {reunion_date.strftime('%d/%m/%Y')}"
                    ).alignment = WD_ALIGN_PARAGRAPH.RIGHT

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

                    offers_text = "\n".join(
                        [f"{i + 1} - {r['supplier_name']} - {r['offer_amount']} MAD" for i, r in enumerate(bc_offers)]
                    )

                    pv_content = f"PV {pv_num} - BC {selected_bc}"

                    insert_record(
                        """
                        INSERT INTO bc_opening_pvs
                        (bc_ref, bc_subject, session_date, session_time, session_place, chair_name, members, offers_text, conclusion_text, pv_content, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            selected_bc,
                            obj_bc,
                            str(reunion_date),
                            reunion_hour,
                            session_place,
                            p_name,
                            f"{d_name}\n{t_name}",
                            offers_text,
                            f"PV {pv_num}",
                            pv_content,
                            str(date.today()),
                        ),
                    )

                    bio = BytesIO()
                    doc.save(bio)

                    st.download_button(
                        label=f"📥 تحميل المحضر رقم {pv_num}",
                        data=bio.getvalue(),
                        file_name=f"PV_BC_{selected_bc}_{pv_num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

        st.dataframe(fetch_all("SELECT * FROM bc_opening_pvs ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[5]:
        with st.form("bc_award_form"):
            bc_ref = st.text_input("رقم BC", key="bc_award_ref")
            awarded_supplier = st.text_input("نائل سند الطلب")
            awarded_amount = st.number_input("مبلغ الإسناد", min_value=0.0, step=100.0)
            award_date = st.date_input("تاريخ الإسناد")
            execution_deadline = st.text_input("أجل التنفيذ")
            bc_issue_date = st.date_input("تاريخ إصدار BC")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ الإسناد")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_awards
                    (bc_ref, awarded_supplier, awarded_amount, award_date, execution_deadline, bc_issue_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        awarded_supplier,
                        awarded_amount,
                        str(award_date),
                        execution_deadline,
                        str(bc_issue_date),
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ الإسناد.")

        st.dataframe(fetch_all("SELECT * FROM bc_awards ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[6]:
        with st.form("bc_execution_form"):
            bc_ref = st.text_input("رقم BC", key="bc_exec_ref")
            notification_date = st.date_input("تاريخ التبليغ")
            start_date = st.date_input("تاريخ بدء التنفيذ")
            expected_delivery = st.date_input("تاريخ التسليم المتوقع")
            execution_status = st.selectbox("حالة التنفيذ", ["لم يبدأ", "جاري", "تم"])
            execution_progress = st.slider("نسبة الإنجاز", 0, 100, 0)
            notes = st.text_area("ملاحظات التتبع")

            submitted = st.form_submit_button("حفظ التنفيذ")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_executions
                    (bc_ref, notification_date, start_date, expected_delivery, execution_status, execution_progress, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        str(notification_date),
                        str(start_date),
                        str(expected_delivery),
                        execution_status,
                        execution_progress,
                        notes,
                        str(date.today()),
                    ),
                )
                st.success("تم حفظ وضعية التنفيذ.")

        st.dataframe(fetch_all("SELECT * FROM bc_executions ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[7]:
        with st.form("bc_reception_form"):
            bc_ref = st.text_input("رقم BC", key="bc_reception_ref")
            reception_date = st.date_input("تاريخ الاستلام")
            reception_type = st.selectbox("نوع الاستلام", ["مؤقت", "نهائي"])
            conformity = st.selectbox("المطابقة", ["مطابق", "غير مطابق"])
            invoice_number = st.text_input("رقم الفاتورة")
            invoice_date = st.date_input("تاريخ الفاتورة")
            invoice_amount = st.number_input("مبلغ الفاتورة", min_value=0.0, step=100.0)
            payment_date = st.date_input("تاريخ الأداء")
            notes = st.text_area("ملاحظات")

            submitted = st.form_submit_button("حفظ الاستلام والأداء")
            if submitted:
                insert_record(
                    """
                    INSERT INTO bc_receptions
                    (bc_ref, reception_date, reception_type, conformity, invoice_number, invoice_date, invoice_amount, payment_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bc_ref,
                        str(reception_date),
                        reception_type,
                        conformity,
                        invoice_number,
                        str(invoice_date),
                        invoice_amount,
                        str(payment_date),
                        notes,
                        str(date.today()),
                    ),
                )
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
            st.download_button(
                "تحميل رسالة الاستشارة",
                data=text,
                file_name=f"Lettre_consultation_{bc_ref if bc_ref else 'BC'}.txt",
                mime="text/plain",
            )

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
            st.download_button(
                "تحميل إشعار الإسناد",
                data=text,
                file_name=f"Notification_attribution_{bc_ref if bc_ref else 'BC'}.txt",
                mime="text/plain",
            )

    with bc_tabs[10]:
        st.dataframe(fetch_all("SELECT * FROM bc_records ORDER BY id DESC"), use_container_width=True, hide_index=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("نظام تدبير مصالح الجماعة — نسخة احترافية جاهزة للنشر")
