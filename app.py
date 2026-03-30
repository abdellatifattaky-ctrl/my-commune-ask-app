import streamlit as st
import sqlite3
import io
from datetime import date

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر Streamlit على الإطلاق) ---
st.set_page_config(page_title="SMART PRO+ الصفقات", layout="wide")

# --- 2. دوال قاعدة البيانات (مع التواريخ الجديدة) ---
def get_conn():
    conn = sqlite3.connect("procurement.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # إنشاء الجدول مع كافة الحقول المطلوبة (المرجع، الموضوع، المبلغ، وتواريخ النشر)
    c.execute("""
        CREATE TABLE IF NOT EXISTS market_master_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_ref TEXT,
            market_object TEXT,
            estimate_amount REAL,
            date_journal_1 TEXT,
            date_journal_2 TEXT,
            date_portail TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_market_refs():
    try:
        conn = get_conn()
        rows = conn.execute("SELECT DISTINCT market_ref FROM market_master_data").fetchall()
        conn.close()
        return [r['market_ref'] for r in rows]
    except:
        return []

# --- 3. تشغيل التأسيس ---
init_db()

# --- 4. واجهة المستخدم (القالب الأصلي) ---
st.sidebar.title("القائمة الرئيسية")
menu = st.sidebar.selectbox("اختر القسم:", ["الصفحة الرئيسية", "الصفقات العمومية"])

if menu == "الصفحة الرئيسية":
    st.title("👋 مرحباً بك في نظام تدبير الجماعة")
    st.info("الرجاء اختيار 'الصفقات العمومية' من القائمة الجانبية.")

elif menu == "الصفقات العمومية":
    st.markdown('<h2 style="text-align: center; color: #1E3A8A;">تدبير الصفقات العمومية SMART PRO+</h2>', unsafe_allow_html=True)

    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 توليد المحاضر"])

    # --- التبويب الأول: إدخال البيانات ---
    with tabs[0]:
        st.subheader("إدخال بيانات الصفقة وتواريخ النشر")
        with st.form("market_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة (N° AO)")
                m_obj = st.text_area("موضوع الصفقة")
                m_amount = st.number_input("التقدير المالي (TTC)", min_value=0.0)
            
            with col2:
                st.write("**📅 تواريخ النشر:**")
                d_j1 = st.date_input("تاريخ النشر بالجريدة 1", value=date.today())
                d_j2 = st.date_input("تاريخ النشر بالجريدة 2", value=date.today())
                d_portail = st.date_input("تاريخ النشر بالبوابة", value=date.today())
                m_open_date = st.date_input("تاريخ فتح الأظرفة", value=date.today())

            if st.form_submit_button("حفظ الصفقة"):
                if m_ref and m_obj:
                    conn = get_conn()
                    conn.execute("""INSERT INTO market_master_data 
                        (market_ref, market_object, estimate_amount, date_journal_1, date_journal_2, date_portail, created_at) 
                        VALUES (?,?,?,?,?,?,?)""",
                        (m_ref, m_obj, m_amount, str(d_j1), str(d_j2), str(d_portail), str(m_open_date)))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ تم حفظ الصفقة {m_ref} بنجاح!")
                    st.rerun() # تحديث الصفحة لرؤية البيانات الجديدة
                else:
                    st.error("⚠️ يرجى إدخال المرجع والموضوع!")

    # --- التبويب الثاني: الإدارة ---
    with tabs[1]:
        st.subheader("الصفقات المسجلة")
        conn = get_conn()
        data = conn.execute("SELECT * FROM market_master_data ORDER BY id DESC").fetchall()
        conn.close()
        if data:
            st.table(data)
        else:
            st.info("لا توجد صفقات مسجلة حالياً.")

    # --- التبويب الثالث: توليد المستندات ---
    with tabs[2]:
        st.subheader("إصدار الوثائق (Docx)")
        refs = get_market_refs()
        if refs:
            target = st.selectbox("اختر الصفقة:", refs)
            st.write(f"سيتم إصدار الوثائق لـ: **{target}**")
            
            c1, c2, c3 = st.columns(3)
            buttons = ["PV1", "PV2", "PV3", "Rapport", "OS", "OS Notification"]
            # هنا ستوضع دوال التحميل لاحقاً
            for i, btn_name in enumerate(buttons):
                col = [c1, c2, c3][i % 3]
                if col.button(f"إنشاء {btn_name}"):
                    st.toast(f"جاري تحضير {btn_name}...")
        else:
            st.warning("يرجى إضافة صفقة أولاً.")
