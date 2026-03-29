import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- المحافظة على الدوال الأصلية الخاصة بك ---
def get_conn():
    conn = sqlite3.connect("procurement.db")
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all(query, params=()):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- تعريف القائمة الجانبية (هذا السطر يحل مشكلة NameError) ---
menu = st.sidebar.selectbox("القائمة", ["الصفقات العمومية"]) 

# --- القالب الأصلي الخاص بك ---
if menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية SMART PRO+</div>', unsafe_allow_html=True)

    # 1. تعريف الدوال (Functions) داخل السياق
    def init_procurement_smart_tables():
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS market_master_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                market_object TEXT,
                estimate_amount REAL,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_market_refs():
        rows = fetch_all("SELECT DISTINCT market_ref FROM market_master_data WHERE market_ref IS NOT NULL")
        return [r["market_ref"] for r in rows]

    def get_market_data(market_ref):
        rows = fetch_all("SELECT * FROM market_master_data WHERE market_ref = ? LIMIT 1", (market_ref,))
        return rows[0] if rows else None

    # 2. تشغيل التأسيس (بمحاذاة صحيحة)
    init_procurement_smart_tables()

    # 3. واجهة المستخدم (UI) بنفس قوالبك
    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 توليد المحاضر"])

    with tabs[0]:
        st.subheader("إدخال بيانات الصفقة الأساسية")
        with st.form("market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة (N° AO)", placeholder="مثال: 01/2024")
                m_obj = st.text_area("موضوع الصفقة")
            with col2:
                m_date = st.date_input("تاريخ فتح الأظرفة")
                m_amount = st.number_input("التقدير المالي", min_value=0.0)

            submit_btn = st.form_submit_button("حفظ")
            if submit_btn:
                # كود الحفظ الفعلي ليعمل الزر
                conn = get_conn()
                conn.execute("INSERT INTO market_master_data (market_ref, market_object, estimate_amount, created_at) VALUES (?, ?, ?, ?)",
                             (m_ref, m_obj, m_amount, str(m_date)))
                conn.commit()
                conn.close()
                st.success(f"تم حفظ {m_ref} بنجاح")

    with tabs[1]:
        st.subheader("قائمة الصفقات المسجلة")
        refs = get_market_refs()
        if refs:
            selected_ref = st.selectbox("اختر صفقة:", refs)
            data = get_market_data(selected_ref)
            if data:
                st.write(dict(data))
        else:
            st.info("لا توجد صفقات مسجلة حالياً.")

    with tabs[2]:
        st.subheader("تحميل المحاضر والوثائق (Docx)")
        all_refs = get_market_refs()
        if all_refs:
            target_ref = st.selectbox("اختر الصفقة لإصدار وثائقها:", all_refs, key="gen_docs")
            if st.button("إنشاء PV1"):
                st.info(f"جاري تحضير الملف للصفقة {target_ref}...")
        else:
            st.warning("يجب إضافة صفقة أولاً.")
