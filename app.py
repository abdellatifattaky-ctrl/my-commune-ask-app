import streamlit as st
import sqlite3
from datetime import date

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="نظام تدبير مصالح الجماعة",
    page_icon="🏛️",
    layout="wide",
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
html, body, [class*="css"]  {
    direction: rtl;
    text-align: right;
    font-family: "Arial", sans-serif;
}
.block-container {
    padding-top: 1.2rem;
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
.card {
    background: #ffffff;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    margin-bottom: 14px;
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
""", unsafe_allow_html=True)

# =========================
# DATABASE
# =========================
def get_conn():
    return sqlite3.connect("commune.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS correspondences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT,
            subject TEXT,
            ctype TEXT,
            department TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT,
            license_type TEXT,
            status TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            department TEXT,
            position TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            progress INTEGER,
            budget TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS pvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_ref TEXT,
            pv_type TEXT,
            notes TEXT,
            content TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

    c.execute("""
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
    """)

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

# =========================
# SIDEBAR
# =========================
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

# =========================
# HEADER
# =========================
st.markdown("""
<div class="main-title">
    <h1>نظام تدبير مصالح الجماعة</h1>
    <p>نسخة احترافية بواجهة عربية محسنة — Streamlit + SQLite</p>
</div>
""", unsafe_allow_html=True)

# =========================
# DASHBOARD
# =========================
if menu == "لوحة القيادة":
    st.markdown('<div class="section-title">لوحة القيادة</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f'<div class="small-card"><h3>{count_rows("correspondences")}</h3><p>المراسلات</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="small-card"><h3>{count_rows("licenses")}</h3><p>الرخص</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="small-card"><h3>{count_rows("employees")}</h3><p>الموظفون</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="small-card"><h3>{count_rows("projects")}</h3><p>المشاريع</p></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="small-card"><h3>{count_rows("procurements")}</h3><p>الصفقات</p></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="small-card"><h3>{count_rows("bc_records")}</h3><p>BC</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ملخص الوضعية")
    dashboard_data = [
        {"الوحدة": "المراسلات", "عدد السجلات": count_rows("correspondences"), "الوضعية": "نشطة"},
        {"الوحدة": "الرخص", "عدد السجلات": count_rows("licenses"), "الوضعية": "قيد المعالجة"},
        {"الوحدة": "الموظفون", "عدد السجلات": count_rows("employees"), "الوضعية": "مستقرة"},
        {"الوحدة": "المشاريع", "عدد السجلات": count_rows("projects"), "الوضعية": "تتبع مستمر"},
        {"الوحدة": "الصفقات العمومية", "عدد السجلات": count_rows("procurements"), "الوضعية": "جارية"},
        {"الوحدة": "سندات الطلب BC", "عدد السجلات": count_rows("bc_records"), "الوضعية": "جارية"},
    ]
    st.dataframe(dashboard_data, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CORRESPONDENCES
# =========================
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
                (reference, subject, ctype, department, status, str(date.today()))
            )
            st.success("تم حفظ المراسلة بنجاح.")

    rows = fetch_all("SELECT * FROM correspondences ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)

# =========================
# LICENSES
# =========================
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
                (applicant_name, license_type, status, notes, str(date.today()))
            )
            st.success("تم حفظ الطلب.")

    rows = fetch_all("SELECT * FROM licenses ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)

# =========================
# EMPLOYEES
# =========================
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
                (full_name, department, position, status, str(date.today()))
            )
            st.success("تم حفظ الموظف.")

    rows = fetch_all("SELECT * FROM employees ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)

# =========================
# PROJECTS
# =========================
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
                (project_name, progress, budget, status, str(date.today()))
            )
            st.success("تم حفظ المشروع.")

    rows = fetch_all("SELECT * FROM projects ORDER BY id DESC")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.subheader("نسب التقدم")
    for row in rows[:10]:
        st.write(f"**{row['project_name']}**")
        st.progress(int(row["progress"]))

# =========================
# PROCUREMENTS
# =========================
elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "البيانات الأساسية",
        "CPS",
        "Lancement",
        "Ouverture des plis",
        "Évaluation",
        "Attribution",
        "OS",
        "PVs",
        "سجل الصفقات",
    ])

    with tabs[0]:
        with st.form("procurement_form"):
            c1, c2 = st.columns(2)
            with c1:
                reference = st.text_input("مرجع الصفقة")
                subject = st.text_input("موضوع الصفقة")
                owner = st.text_input("صاحب المشروع", value="الجماعة الترابية")
                procedure_type = st.selectbox("طريقة الإبرام", ["طلب عروض مفتوح", "طلب عروض محدود", "سند طلب", "مباراة معمارية"])
                estimated_cost = st.number_input("الكلفة التقديرية", min_value=0.0, step=1000.0)
            with c2:
                fiscal_year = st.number_input("السنة المالية", min_value=2024, max_value=2100, value=2026)
                department = st.text_input("المصلحة المعنية")
                market_type = st.selectbox("نوع الصفقة", ["أشغال", "توريدات", "خدمات"])
                status = st.selectbox("المرحلة الحالية", ["إعداد", "إطلاق", "فتح الأظرفة", "التقييم", "الإسناد", "التنفيذ"])
            submitted = st.form_submit_button("حفظ الصفقة")

            if submitted:
                insert_record(
                    """INSERT INTO procurements
                    (reference, subject, owner, procedure_type, estimated_cost, fiscal_year, department, market_type, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (reference, subject, owner, procedure_type, estimated_cost, fiscal_year, department, market_type, status, str(date.today()))
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
                    """INSERT INTO cps
                    (procurement_ref, cps_subject, execution_delay, temporary_guarantee, final_guarantee, payment_terms, penalties, reception_terms, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, cps_subject, execution_delay, temporary_guarantee, final_guarantee, payment_terms, penalties, reception_terms, notes, str(date.today()))
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
                    """INSERT INTO procurement_launches
                    (procurement_ref, launch_date, publication_date, opening_date, publication_number, publication_media, visit_required, place, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, str(launch_date), str(publication_date), str(opening_date), publication_number, ", ".join(publication_media), visit_required, place, notes, str(date.today()))
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
                    """INSERT INTO procurement_openings
                    (procurement_ref, session_date, session_time, chair_name, members, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, str(session_date), str(session_time), chair_name, members, notes, str(date.today()))
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
                    """INSERT INTO procurement_evaluations
                    (procurement_ref, company_name, administrative_result, technical_score, financial_offer, ranking, result, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, company_name, administrative_result, technical_score, financial_offer, ranking, result, notes, str(date.today()))
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
                    """INSERT INTO procurement_attributions
                    (procurement_ref, awarded_company, provisional_date, final_date, attributed_amount, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, awarded_company, str(provisional_date), str(final_date), attributed_amount, notes, str(date.today()))
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
                    """INSERT INTO os_orders
                    (procurement_ref, os_type, company_name, os_date, execution_delay, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (procurement_ref, os_type, company_name, str(os_date), execution_delay, notes, str(date.today()))
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
                    (procurement_ref, pv_type, pv_notes, pv_content, str(date.today()))
                )
                st.success("تم حفظ المحضر.")
        with c2:
            st.download_button(
                "تحميل المحضر",
                data=pv_content if pv_content else "لا يوجد محتوى",
                file_name=f"{pv_type.replace(' ', '_')}.txt",
                mime="text/plain"
            )

        st.dataframe(fetch_all("SELECT * FROM pvs ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with tabs[8]:
        st.dataframe(fetch_all("SELECT * FROM procurements ORDER BY id DESC"), use_container_width=True, hide_index=True)

# =========================
# BC
# =========================
elif menu == "سندات الطلب BC":
    st.markdown('<div class="section-title">تدبير سندات الطلب BC</div>', unsafe_allow_html=True)

    bc_tabs = st.tabs([
        "المعطيات الأساسية",
        "الاستشارة",
        "العروض",
        "محضر افتتاح BC",
        "الإسناد",
        "التنفيذ",
        "الاستلام والأداء",
        "سجل BC",
    ])

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
                    """INSERT INTO bc_records
                    (bc_ref, fiscal_year, subject, department, expense_type, budget_line, estimated_amount, manager_name, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, fiscal_year, subject, department, expense_type, budget_line, estimated_amount, manager_name, notes, str(date.today()))
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
                    """INSERT INTO bc_consultations
                    (bc_ref, consultation_date, deadline_date, consultation_mode, suppliers, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, str(consultation_date), str(deadline_date), consultation_mode, suppliers, notes, str(date.today()))
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
                    """INSERT INTO bc_offers
                    (bc_ref, supplier_name, offer_ref, offer_date, offer_amount, offer_status, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, supplier_name, offer_ref, str(offer_date), offer_amount, offer_status, notes, str(date.today()))
                )
                st.success("تم حفظ العرض.")

        st.dataframe(fetch_all("SELECT * FROM bc_offers ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[3]:
        bc_ref_pv = st.text_input("رقم سند الطلب", key="bc_ref_pv")
        bc_subject_pv = st.text_input("موضوع سند الطلب", key="bc_subject_pv")
        session_date_pv = st.date_input("تاريخ الجلسة", key="session_date_pv")
        session_time_pv = st.time_input("ساعة الجلسة", key="session_time_pv")
        session_place_pv = st.text_input("مكان الجلسة", value="مقر الجماعة", key="session_place_pv")
        chair_pv = st.text_input("رئيس الجلسة", key="chair_pv")
        members_pv = st.text_area("أعضاء اللجنة", key="members_pv", placeholder="الاسم 1\nالاسم 2\nالاسم 3")

        st.markdown("#### العروض المتوصل بها")
        supplier1 = st.text_input("المورد 1", key="supplier1")
        amount1 = st.number_input("مبلغ العرض 1", min_value=0.0, step=100.0, key="amount1")
        note1 = st.text_input("ملاحظات 1", key="note1")

        supplier2 = st.text_input("المورد 2", key="supplier2")
        amount2 = st.number_input("مبلغ العرض 2", min_value=0.0, step=100.0, key="amount2")
        note2 = st.text_input("ملاحظات 2", key="note2")

        supplier3 = st.text_input("المورد 3", key="supplier3")
        amount3 = st.number_input("مبلغ العرض 3", min_value=0.0, step=100.0, key="amount3")
        note3 = st.text_input("ملاحظات 3", key="note3")

        offers = []
        if supplier1:
            offers.append((supplier1, amount1, note1))
        if supplier2:
            offers.append((supplier2, amount2, note2))
        if supplier3:
            offers.append((supplier3, amount3, note3))

        if offers:
            best_offer = min(offers, key=lambda x: x[1])
            auto_conclusion = f"بعد دراسة العروض، تبين أن أقل عرض هو عرض {best_offer[0]} بمبلغ {best_offer[1]} درهم."
        else:
            auto_conclusion = "لم يتم تسجيل أي عرض."

        st.info(auto_conclusion)

        conclusion_pv = st.text_area("الخلاصة النهائية", value=auto_conclusion, key="conclusion_pv")

        offers_table = []
        if supplier1:
            offers_table.append(f"- {supplier1}: مبلغ العرض {amount1} درهم. ملاحظات: {note1}")
        if supplier2:
            offers_table.append(f"- {supplier2}: مبلغ العرض {amount2} درهم. ملاحظات: {note2}")
        if supplier3:
            offers_table.append(f"- {supplier3}: مبلغ العرض {amount3} درهم. ملاحظات: {note3}")

        pv_text = f"""المملكة المغربية
الجماعة الترابية

محضر فتح ودراسة العروض
المتعلقة بسند الطلب رقم: {bc_ref_pv}

بتاريخ {session_date_pv} على الساعة {session_time_pv}، اجتمعت اللجنة/المصلحة المختصة بمقر {session_place_pv}
لدراسة العروض المتعلقة بسند الطلب رقم {bc_ref_pv} الخاص بـ: {bc_subject_pv}.

ترأس الجلسة السيد/السيدة: {chair_pv}
وبحضور السادة:
{members_pv}

وبعد حصر العروض المتوصل بها، تم تسجيل ما يلي:
{chr(10).join(offers_table) if offers_table else "لا توجد عروض مسجلة."}

وبعد دراسة العروض والمقارنة بينها، خلصت اللجنة إلى ما يلي:
{conclusion_pv}

وحرر هذا المحضر في نفس اليوم من أجل ما يلزم.
"""

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("معاينة محضر الافتتاح BC"):
                st.text_area("نص المحضر", value=pv_text, height=380)
        with c2:
            if st.button("حفظ محضر الافتتاح BC"):
                insert_record(
                    """INSERT INTO bc_opening_pvs
                    (bc_ref, bc_subject, session_date, session_time, session_place, chair_name, members, offers_text, conclusion_text, pv_content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        bc_ref_pv, bc_subject_pv, str(session_date_pv), str(session_time_pv),
                        session_place_pv, chair_pv, members_pv, "\n".join(offers_table),
                        conclusion_pv, pv_text, str(date.today())
                    )
                )
                st.success("تم حفظ محضر الافتتاح.")
        with c3:
            st.download_button(
                label="تحميل محضر الافتتاح BC",
                data=pv_text,
                file_name=f"PV_Ouverture_BC_{bc_ref_pv if bc_ref_pv else 'sans_ref'}.txt",
                mime="text/plain"
            )

        st.dataframe(fetch_all("SELECT * FROM bc_opening_pvs ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[4]:
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
                    """INSERT INTO bc_awards
                    (bc_ref, awarded_supplier, awarded_amount, award_date, execution_deadline, bc_issue_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, awarded_supplier, awarded_amount, str(award_date), execution_deadline, str(bc_issue_date), notes, str(date.today()))
                )
                st.success("تم حفظ الإسناد.")

        st.dataframe(fetch_all("SELECT * FROM bc_awards ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[5]:
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
                    """INSERT INTO bc_executions
                    (bc_ref, notification_date, start_date, expected_delivery, execution_status, execution_progress, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, str(notification_date), str(start_date), str(expected_delivery), execution_status, execution_progress, notes, str(date.today()))
                )
                st.success("تم حفظ وضعية التنفيذ.")

        st.dataframe(fetch_all("SELECT * FROM bc_executions ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[6]:
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
                    """INSERT INTO bc_receptions
                    (bc_ref, reception_date, reception_type, conformity, invoice_number, invoice_date, invoice_amount, payment_date, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bc_ref, str(reception_date), reception_type, conformity, invoice_number, str(invoice_date), invoice_amount, str(payment_date), notes, str(date.today()))
                )
                st.success("تم حفظ بيانات الاستلام والأداء.")

        st.dataframe(fetch_all("SELECT * FROM bc_receptions ORDER BY id DESC"), use_container_width=True, hide_index=True)

    with bc_tabs[7]:
        st.dataframe(fetch_all("SELECT * FROM bc_records ORDER BY id DESC"), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("نظام تدبير مصالح الجماعة — نسخة عربية محسنة بملف واحد")
