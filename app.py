import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# --- 1. إعدادات المنصة ---
st.set_page_config(page_title="مدير مصالح أسكاون - النظام الموحد", layout="wide", initial_sidebar_state="expanded")

# --- 2. محرك قاعدة البيانات (الدائم) ---
# ملاحظة: في Streamlit Cloud، يفضل ربطه لاحقاً بـ Google Sheets للحفظ الأبدي
conn = sqlite3.connect('askaouen_admin_v2.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
c.execute('CREATE TABLE IF NOT EXISTS budget (type TEXT, item TEXT, amount REAL, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS fuel (vehicle TEXT, liters REAL, driver TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS staff (name TEXT, grade TEXT, task TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS rent (unit TEXT, tenant TEXT, price REAL, status TEXT)')
conn.commit()

# --- 3. تصميم الواجهة الجانبية ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Coat_of_arms_of_Morocco.svg", width=70)
    st.title("جماعة أسكاون")
    st.markdown("---")
    choice = st.radio("قائمة التسيير:", [
        "🏠 لوحة القيادة المالية",
        "🏗️ الطلبيات العمومية (BC/AO)",
        "⛽ تتبع المحروقات",
        "👥 تدبير الموظفين",
        "💰 الممتلكات والكراء",
        "📂 مكتب الضبط والأرشيف"
    ])
    st.markdown("---")
    st.caption(f"📅 التاريخ: {date.today()}")
    st.info("مرحباً سيادة مدير المصالح")

# --- 4. الوظائف البرمجية لكل قسم ---

# --- القسم 1: لوحة القيادة المالية ---
if choice == "🏠 لوحة القيادة المالية":
    st.header("📊 ميزانية الجماعة: المداخيل والمصاريف")
    
    # استمارة إدخال سريعة
    with st.expander("➕ تسجيل عملية مالية جديدة"):
        with st.form("budget_form"):
            col1, col2, col3 = st.columns(3)
            b_type = col1.selectbox("نوع العملية", ["مداخيل", "مصاريف"])
            b_item = col2.text_input("البيان / التفصيل")
            b_amount = col3.number_input("المبلغ بالدرهم", min_value=0.0)
            if st.form_submit_button("حفظ العملية"):
                c.execute("INSERT INTO budget VALUES (?, ?, ?, ?)", (b_type, b_item, b_amount, str(date.today())))
                conn.commit()
                st.success("تم الحفظ وتحديث الميزانية")
                st.rerun()

    # عرض التحليلات المالية
    df_b = pd.read_sql_query("SELECT * FROM budget", conn)
    if not df_b.empty:
        total_rev = df_b[df_b['type'] == 'مداخيل']['amount'].sum()
        total_exp = df_b[df_b['type'] == 'مصاريف']['amount'].sum()
        balance = total_rev - total_exp
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي المداخيل", f"{total_rev:,.2f} DH")
        m2.metric("إجمالي المصاريف", f"-{total_exp:,.2f} DH", delta_color="inverse")
        m3.metric("الفائض التقديري", f"{balance:,.2f} DH", delta=f"{(balance/total_rev*100):.1f}%" if total_rev > 0 else 0)
        
        st.subheader("📝 السجل المالي الأخير")
        st.dataframe(df_b.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("لا توجد بيانات مالية مسجلة. ابدأ بإضافة أول عملية.")

# --- القسم 2: الطلبيات العمومية (BC/AO) ---
elif choice == "🏗️ الطلبيات العمومية (BC/AO)":
    st.header("🏗️ تدبير الصفقات وسندات الطلب")
    st.warning("⚠️ هذا القسم بانتظار نصوص المحاضر (PV) بالفرنسية التي ستوافينا بها غداً.")
    
    t1, t2 = st.tabs(["📄 سندات الطلب (BC)", "🏢 الصفقات الكبرى (AO)"])
    with t1:
        st.subheader("إعداد سند طلب جديد")
        bc_ref = st.text_input("مرجع سند الطلب (N° BC)")
        st.button("تجهيز الملف الإداري")
    with t2:
        st.subheader("تتبع مراحل الصفقات العمومية")
        st.selectbox("الحالة الحالية", ["إعداد DCE", "الإعلان", "فتح الأظرفة", "المصادقة"])

# --- القسم 3: تتبع المحروقات ---
elif choice == "⛽ تتبع المحروقات":
    st.header("⛽ سجل استهلاك آليات الجماعة")
    with st.form("fuel_form"):
        c1, c2, c3 = st.columns(3)
        v = c1.selectbox("الآلية", ["شاحنة النفايات", "سيارة الإسعاف", "جرافة", "سيارة المصلحة"])
        l = c2.number_input("الكمية (لتر)", min_value=1.0)
        d = c3.text_input("اسم السائق")
        if st.form_submit_button("تسجيل الوصول"):
            c.execute("INSERT INTO fuel VALUES (?, ?, ?, ?)", (v, l, d, str(date.today())))
            conn.commit()
            st.rerun()
    
    df_f = pd.read_sql_query("SELECT * FROM fuel", conn)
    st.dataframe(df_f, use_container_width=True)

# --- القسم 4: الموظفين ---
elif choice == "👥 تدبير الموظفين":
    st.header("👥 سجل الموارد البشرية")
    with st.expander("➕ إضافة موظف جديد"):
        with st.form("staff_form"):
            s_n = st.text_input("الاسم الكامل")
            s_g = st.text_input("السلم / الإطار")
            s_t = st.text_input("المهمة الحالية")
            if st.form_submit_button("حفظ الموظف"):
                c.execute("INSERT INTO staff VALUES (?, ?, ?)", (s_n, s_g, s_t))
                conn.commit()
                st.rerun()
    
    df_s = pd.read_sql_query("SELECT * FROM staff", conn)
    st.table(df_s)

# --- القسم 5: الممتلكات والكراء ---
elif choice == "💰 الممتلكات والكراء":
    st.header("💰 مداخيل كراء ممتلكات الجماعة")
    with st.form("rent_form"):
        c1, c2, c3 = st.columns(3)
        prop = c1.text_input("اسم المحل/المرفق")
        ten = c2.text_input("المستأجر")
        val = c3.number_input("السومة الشهرية")
        if st.form_submit_button("تسجيل المرفق"):
            c.execute("INSERT INTO rent VALUES (?, ?, ?, 'مؤدى')", (prop, ten, val))
            conn.commit()
            st.rerun()
    
    df_r = pd.read_sql_query("SELECT * FROM rent", conn)
    st.dataframe(df_r, use_container_width=True)

# --- القسم 6: مكتب الضبط ---
elif choice == "📂 مكتب الضبط والأرشيف":
    st.header("📂 تتبع المراسلات والملفات")
    st.info("هنا سيتم أرشفة المراسلات الواردة من العمالة والخزينة.")
    st.text_input("بحث برقم الإرسالية...")
