import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from docx import Document
from io import BytesIO

# --- 1. إعدادات المنصة وقاعدة البيانات ---
st.set_page_config(page_title="منظومة جماعة أسكاون الرقمية", layout="wide")

conn = sqlite3.connect('askaouen_full_system.db', check_same_thread=False)
c = conn.cursor()

# إنشاء جميع الجداول الضرورية
c.execute('CREATE TABLE IF NOT EXISTS budget (type TEXT, item TEXT, amount REAL, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS staff (name TEXT, grade TEXT, status TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS permits (type TEXT, requester TEXT, status TEXT, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS sessions (type TEXT, s_date TEXT, agenda TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS fuel (vehicle TEXT, liters REAL, driver TEXT, date TEXT)')
conn.commit()

# --- 2. نظام الصلاحيات والدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None

def check_login(user, pwd):
    users = {
        "admin_askaoun": {"pwd": "DM_2026", "role": "مدير المصالح"},
        "tech_urban": {"pwd": "Askaoun@Tech", "role": "مصلحة التعمير"},
        "fin_service": {"pwd": "Askaoun@Fin", "role": "المصلحة المالية"},
        "staff_office": {"pwd": "Askaoun@RH", "role": "مصلحة الموظفين"}
    }
    if user in users and users[user]["pwd"] == pwd:
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = users[user]["role"]
        return True
    return False

# واجهة تسجيل الدخول
if not st.session_state['logged_in']:
    st.title("🏛️ بوابة الإدارة الرقمية - جماعة أسكاون")
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            if check_login(u, p): st.rerun()
            else: st.error("خطأ في البيانات")
    st.stop()

# --- 3. القائمة الجانبية وتوزيع الصلاحيات ---
role = st.session_state['user_role']
st.sidebar.title(f"👤 {role}")

all_menus = {
    "مدير المصالح": ["📊 الميزانية", "🏛️ أشغال المجلس", "🏠 التعمير", "🏗️ الصفقات", "👥 الموظفين", "⛽ المحروقات"],
    "مصلحة التعمير": ["🏠 التعمير", "🏗️ الصفقات"],
    "المصلحة المالية": ["📊 الميزانية", "⛽ المحروقات"],
    "مصلحة الموظفين": ["👥 الموظفين"]
}

menu = st.sidebar.radio("الانتقال إلى:", all_menus.get(role, []))
if st.sidebar.button("تسجيل الخروج"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- 4. محتوى الوحدات الإدارية ---

# مصلحة الميزانية والمالية
if menu == "📊 الميزانية":
    st.header("📊 تتبع التوازن المالي للجماعة")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("b_form"):
            b_type = st.selectbox("النوع", ["مداخيل", "مصاريف"])
            b_item = st.text_input("البيان")
            b_amt = st.number_input("المبلغ", min_value=0.0)
            if st.form_submit_button("حفظ"):
                c.execute("INSERT INTO budget VALUES (?,?,?,?)", (b_type, b_item, b_amt, str(date.today())))
                conn.commit()
    with col2:
        df_b = pd.read_sql_query("SELECT * FROM budget", conn)
        if not df_b.empty:
            rev = df_b[df_b['type']=='مداخيل']['amount'].sum()
            exp = df_b[df_b['type']=='مصاريف']['amount'].sum()
            st.metric("الفائض الحالي", f"{rev-exp:,.2f} DH")
            st.dataframe(df_b.tail(5), use_container_width=True)

# مصلحة التعمير والرخص
elif menu == "🏠 التعمير":
    st.header("🏠 تدبير الرخص والتعمير")
    with st.form("p_form"):
        req = st.text_input("صاحب الطلب")
        p_type = st.selectbox("الرخصة", ["بناء", "سكن", "ربط"])
        if st.form_submit_button("تسجيل الطلب"):
            c.execute("INSERT INTO permits VALUES (?,?,'قيد الدراسة',?)", (p_type, req, str(date.today())))
            conn.commit()
    
    st.subheader("تحميل رخصة تجريبية")
    if st.button("توليد ملف Word"):
        doc = Document()
        doc.add_heading(f"Autorisation de : {p_type}", 0)
        doc.add_paragraph(f"Demandeur : {req}\nDate : {date.today()}\nCommune Askaoun")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل الرخصة", bio.getvalue(), "Permit.docx")

# مصلحة أشغال المجلس
elif menu == "🏛️ أشغال المجلس":
    st.header("🏛️ الدورات والمقررات")
    with st.form("s_form"):
        s_type = st.selectbox("الدورة", ["عادية", "استثنائية"])
        s_date = st.date_input("التاريخ")
        agenda = st.text_area("جدول الأعمال")
        if st.form_submit_button("برمجة"):
            c.execute("INSERT INTO sessions VALUES (?,?,?)", (s_type, str(s_date), agenda))
            conn.commit()
    df_s = pd.read_sql_query("SELECT * FROM sessions", conn)
    st.table(df_s)

# مصلحة الصفقات والمحاضر
elif menu == "🏗️ الصفقات":
    st.header("🏗️ الصفقات وسندات الطلب")
    ao_num = st.text_input("رقم الصفقة/السند")
    if st.button("توليد محضر فتح الأظرفة (نموذج)"):
        doc = Document()
        doc.add_paragraph("PROCES-VERBAL D'OUVERTURE DES PLIS").bold = True
        doc.add_paragraph(f"N° : {ao_num}\nObjet : Travaux de construction à Askaoun")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر", bio.getvalue(), "PV_AO.docx")

# مصلحة الموظفين والمحروقات (تتبع نفس المنطق)
elif menu == "👥 الموظفين":
    st.header("👥 سجل الموارد البشرية")
    df_rh = pd.read_sql_query("SELECT * FROM staff", conn)
    st.dataframe(df_rh)

elif menu == "⛽ المحروقات":
    st.header("⛽ تتبع المحروقات")
    v = st.text_input("رقم الآلية")
    l = st.number_input("اللترات", min_value=1.0)
    if st.button("تسجيل"):
        c.execute("INSERT INTO fuel VALUES (?,?, 'سائق 1', ?)", (v, l, str(date.today())))
        conn.commit()
