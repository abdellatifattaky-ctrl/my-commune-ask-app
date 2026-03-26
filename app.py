import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from docx import Document
import os

# =====================
# إعدادات الصفحة والمجلدات
# =====================
st.set_page_config(page_title="نظام إدارة الجماعة القروية SGCA", layout="wide")
st.title("🏛️ نظام إدارة الجماعة القروية (SGCA) - النسخة الكاملة")

DB_FILE = "sgca.db"
UPLOAD_FOLDER = "uploads"
ARCHIVE_FOLDER = "archive"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# =====================
# إنشاء الجداول (قاعدة البيانات)
# =====================
# جدول المستخدمين
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
# جدول المراسلات
c.execute('''CREATE TABLE IF NOT EXISTS courrier (id INTEGER PRIMARY KEY, numero TEXT, type TEXT, objet TEXT, date TEXT, fichier TEXT)''')
# جدول الصفقات
c.execute('''CREATE TABLE IF NOT EXISTS marches (id INTEGER PRIMARY KEY, numero TEXT, objet TEXT, entreprise TEXT, montant REAL, statut TEXT)''')
# جدول الميزانية
c.execute('''CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, type TEXT, montant REAL, description TEXT)''')
# جدول الأملاك
c.execute('''CREATE TABLE IF NOT EXISTS admin_biens (id INTEGER PRIMARY KEY, nom TEXT, type TEXT, valeur REAL, statut TEXT)''')
# جدول الرسائل
c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, sujet TEXT, contenu TEXT, date TEXT)''')
# جدول المحاضر (PV) - الإضافة الجديدة
c.execute('''CREATE TABLE IF NOT EXISTS pv_records (
    id INTEGER PRIMARY KEY, titre TEXT, type_pv TEXT, date_pv TEXT, lieu TEXT, 
    description TEXT, fichier_word TEXT, fichier_scanned TEXT)''')

c.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", ("admin","admin123","Admin"))
conn.commit()

# =====================
# نظام تسجيل الدخول
# =====================
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.subheader("🔐 تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم")
    pass_input = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user_input, pass_input))
        user = c.fetchone()
        if user:
            st.session_state.logged = True
            st.session_state.username = user_input
            st.session_state.role = user[3]
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.stop()

# =====================
# القائمة الجانبية
# =====================
st.sidebar.markdown(f"**مرحباً: {st.session_state.username}** 👤")
menu = ["📊 Dashboard", "📥 مكتب الضبط", "🏗️ الصفقات", "📜 مركز المحاضر", "💰 الميزانية", "🏠 الأملاك", "✉️ الرسائل"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged = False
    st.rerun()

# =====================
# 1. Dashboard
# =====================
if choice == "📊 Dashboard":
    st.subheader("📊 لوحة التحكم العامة")
    col1, col2, col3, col4 = st.columns(4)
    
    # جلب إحصائيات سريعة
    count_courrier = pd.read_sql("SELECT COUNT(*) FROM courrier", conn).iloc[0,0]
    count_marches = pd.read_sql("SELECT COUNT(*) FROM marches", conn).iloc[0,0]
    count_pv = pd.read_sql("SELECT COUNT(*) FROM pv_records", conn).iloc[0,0]
    total_budget = pd.read_sql("SELECT SUM(montant) FROM budget WHERE type='Recette'", conn).iloc[0,0] or 0

    col1.metric("المراسلات", count_courrier)
    col2.metric("الصفقات النشطة", count_marches)
    col3.metric("المحاضر الموثقة", count_pv)
    col4.metric("إجمالي المداخيل", f"{total_budget} درهم")

# =====================
# 2. مركز المحاضر (القسم المطلوب)
# =====================
elif choice == "📜 مركز المحاضر":
    st.subheader("🧾 إدارة وأرشفة المحاضر (PV)")
    t1, t2, t3 = st.tabs(["📝 إنشاء محضر جديد", "📤 رفع نسخة موقعة", "📂 الأرشيف الرقمي"])

    with t1:
        st.write("### توليد مسودة Word")
        c1, c2 = st.columns(2)
        with c1:
            type_p = st.selectbox("نوع المحضر", ["دورة المجلس", "اللجنة الدائمة", "فتح الأظرفة", "زيارة ميدانية"])
            t_title = st.text_input("عنوان المحضر")
        with c2:
            t_date = st.date_input("تاريخ الاجتماع", date.today())
            t_lieu = st.text_input("المكان", "مقر الجماعة")
        
        t_content = st.text_area("خلاصة الاجتماع والمقررات")
        
        if st.button("حفظ وتوليد ملف Word"):
            doc = Document()
            doc.add_heading(f"المملكة المغربية - جماعة قروية", 0)
            doc.add_heading(f"محضر {type_p}", level=1)
            doc.add_paragraph(f"الموضوع: {t_title}")
            doc.add_paragraph(f"التاريخ: {t_date} | المكان: {t_lieu}")
            doc.add_heading("المقررات والنتائج:", level=2)
            doc.add_paragraph(t_content)
            
            f_name = f"PV_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            f_path = os.path.join(ARCHIVE_FOLDER, f_name)
            doc.save(f_path)
            
            c.execute("INSERT INTO pv_records (titre, type_pv, date_pv, lieu, description, fichier_word) VALUES (?,?,?,?,?,?)",
                      (t_title, type_p, str(t_date), t_lieu, t_content, f_path))
            conn.commit()
            st.success("تم الحفظ بنجاح")

    with t2:
        st.write("### أرشفة النسخة النهائية (PDF)")
        pvs_to_sign = pd.read_sql("SELECT id, titre FROM pv_records WHERE fichier_scanned IS NULL", conn)
        if not pvs_to_sign.empty:
            selected_pv = st.selectbox("اختر المحضر", pvs_to_sign['titre'])
            scanned_file = st.file_uploader("رفع PDF موقع ومختوم", type=["pdf"])
            if st.button("اعتماد النسخة النهائية"):
                if scanned_file:
                    s_path = os.path.join(UPLOAD_FOLDER, f"FINAL_{scanned_file.name}")
                    with open(s_path, "wb") as f:
                        f.write(scanned_file.getbuffer())
                    c.execute("UPDATE pv_records SET fichier_scanned=? WHERE titre=?", (s_path, selected_pv))
                    conn.commit()
                    st.success("تمت الأرشفة بنجاح")
        else:
            st.info("لا توجد محاضر معلقة")

    with t3:
        st.write("### البحث في السجلات")
        search = st.text_input("بحث بالاسم...")
        df_pvs = pd.read_sql(f"SELECT * FROM pv_records WHERE titre LIKE '%{search}%'", conn)
        st.table(df_pvs[['titre', 'type_pv', 'date_pv', 'lieu']])

# =====================
# 3. مكتب الضبط
# =====================
elif choice == "📥 مكتب الضبط":
    st.subheader("📥 وارد وصادر الجماعة")
    with st.expander("إضافة مراسلة جديدة"):
        num = st.text_input("الرقم الترتيبي")
        obj = st.text_input("الموضوع")
        typ = st.selectbox("النوع", ["وارد", "صادر"])
        if st.button("تسجيل"):
            c.execute("INSERT INTO courrier (numero, type, objet, date) VALUES (?,?,?,?)", (num, typ, obj, str(date.today())))
            conn.commit()
            st.success("تم التسجيل")
    st.dataframe(pd.read_sql("SELECT * FROM courrier", conn))

# (يمكن إضافة باقي الأقسام مثل الصفقات والميزانية بنفس النمط)

st.sidebar.info("SGCA v2.0 - 2026")
