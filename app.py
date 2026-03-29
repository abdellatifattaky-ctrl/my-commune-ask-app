import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. تعريف الدوال الأساسية (توضع في بداية الملف) ---

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

# --- 2. منطق البرنامج الرئيسي ---

# ملاحظة: تأكد من تعريف متغير menu قبل هذا السطر (مثلاً عبر sidebar)
# سنستخدم 'if' بدلاً من 'elif' لتجنب خطأ SyntaxError إذا كان هذا أول شرط
if menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية SMART PRO+</div>', unsafe_allow_html=True)

    # تشغيل تأسيس الجداول
    init_procurement_smart_tables()

    # إنشاء التبويبات
    tabs = st.tabs(["➕ صفقة جديدة", "📊 إدارة المتنافسين", "📄 إصدار الوثائق"])

    with tabs[0]:
        st.subheader("تسجيل بيانات الصفقة")
        with st.form("new_market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("رقم الصفقة (N° AO)")
                m_obj = st.text_area("موضوع الصفقة")
            with col2:
                m_est = st.number_input("التقدير المالي (Estimation)", min_value=0.0)
                m_date = st.date_input("تاريخ اليوم", value=date.today())
            
            submit = st.form_submit_button("حفظ البيانات")
            
            if submit:
                if m_ref and m_obj:
                    # هنا نضع كود الحفظ في قاعدة البيانات
                    st.success(f"✅ تم تسجيل الصفقة رقم {m_ref} بنجاح")
                else:
                    st.error("⚠️ يرجى ملء الحقول الأساسية (الرقم والموضوع)")

    with tabs[1]:
        st.subheader("لائحة المتنافسين")
        st.info("هنا يمكنك إضافة الشركات المتنافسة ونقاطها التقنية.")

    with tabs[2]:
        st.subheader("تحميل المحاضر والوثائق")
        all_refs = get_market_refs()
        if all_refs:
            selected = st.selectbox("اختر رقم الصفقة المراد معالجتها:", all_refs)
            if st.button("توليد ملف PV1"):
                st.write(f"جاري تحضير محضر فتح الأظرفة للصفقة: {selected}")
        else:
            st.warning("لا توجد صفقات مسجلة في قاعدة البيانات حالياً.")
