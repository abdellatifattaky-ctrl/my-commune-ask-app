import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# =====================
# إنشاء الجداول
# =====================
c.execute('''CREATE TABLE IF NOT EXISTS courrier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT,
    type TEXT,
    objet TEXT,
    date TEXT,
    fichier TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    date TEXT,
    ordre TEXT,
    pv TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS commissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    membres TEXT,
    pv TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS marches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT,
    objet TEXT,
    entreprise TEXT,
    montant REAL,
    statut TEXT
)''')

conn.commit()

# =====================
# واجهة التطبيق
# =====================
st.set_page_config(page_title="نظام الجماعة", layout="wide")

st.title("🏛️ نظام تدبير الجماعة")

menu = [
    "📊 لوحة القيادة",
    "📥 مكتب الضبط",
    "🏛️ دورات المجلس",
    "👥 اللجن",
    "🏗️ الصفقات",
    "🧾 توليد محضر"
]

choice = st.sidebar.selectbox("القائمة", menu)

# =====================
# Dashboard
# =====================
if choice == "📊 لوحة القيادة":
    st.subheader("إحصائيات")

    df1 = pd.read_sql("SELECT * FROM courrier", conn)
    df2 = pd.read_sql("SELECT * FROM sessions", conn)
    df3 = pd.read_sql("SELECT * FROM marches", conn)

    col1, col2, col3 = st.columns(3)

    col1.metric("المراسلات", len(df1))
    col2.metric("الدورات", len(df2))
    col3.metric("الصفقات", len(df3))

# =====================
# مكتب الضبط
# =====================
elif choice == "📥 مكتب الضبط":
    st.subheader("تدبير المراسلات")

    numero = st.text_input("رقم المراسلة")
    type_c = st.selectbox("النوع", ["وارد", "صادر"])
    objet = st.text_input("الموضوع")
    date_c = st.date_input("التاريخ", date.today())
    file = st.file_uploader("رفع الوثيقة")

    if st.button("حفظ"):
        c.execute("INSERT INTO courrier (numero, type, objet, date, fichier) VALUES (?, ?, ?, ?, ?)",
                  (numero, type_c, objet, str(date_c), str(file)))
        conn.commit()
        st.success("تم الحفظ")

    df = pd.read_sql("SELECT * FROM courrier", conn)
    st.dataframe(df)

# =====================
# الدورات
# =====================
elif choice == "🏛️ دورات المجلس":
    st.subheader("إدارة الدورات")

    type_s = st.selectbox("نوع الدورة", ["عادية", "استثنائية"])
    date_s = st.date_input("التاريخ")
    ordre = st.text_area("جدول الأعمال")
    pv = st.file_uploader("محضر الدورة")

    if st.button("إضافة دورة"):
        c.execute("INSERT INTO sessions (type, date, ordre, pv) VALUES (?, ?, ?, ?)",
                  (type_s, str(date_s), ordre, str(pv)))
        conn.commit()
        st.success("تمت الإضافة")

    df = pd.read_sql("SELECT * FROM sessions", conn)
    st.dataframe(df)

# =====================
# اللجن
# =====================
elif choice == "👥 اللجن":
    st.subheader("تدبير اللجن")

    nom = st.text_input("اسم اللجنة")
    membres = st.text_area("الأعضاء")
    pv = st.file_uploader("محضر اللجنة")

    if st.button("إضافة لجنة"):
        c.execute("INSERT INTO commissions (nom, membres, pv) VALUES (?, ?, ?)",
                  (nom, membres, str(pv)))
        conn.commit()
        st.success("تمت الإضافة")

    df = pd.read_sql("SELECT * FROM commissions", conn)
    st.dataframe(df)

# =====================
# الصفقات
# =====================
elif choice == "🏗️ الصفقات":
    st.subheader("تدبير الصفقات")

    numero = st.text_input("رقم الصفقة")
    objet = st.text_input("الموضوع")
    entreprise = st.text_input("المقاولة")
    montant = st.number_input("المبلغ", min_value=0.0)
    statut = st.selectbox("الحالة", ["إعلان", "فتح الأظرفة", "إسناد", "تنفيذ"])

    if st.button("إضافة صفقة"):
        c.execute("INSERT INTO marches (numero, objet, entreprise, montant, statut) VALUES (?, ?, ?, ?, ?)",
                  (numero, objet, entreprise, montant, statut))
        conn.commit()
        st.success("تمت الإضافة")

    df = pd.read_sql("SELECT * FROM marches", conn)
    st.dataframe(df)

# =====================
# توليد محضر
# =====================
elif choice == "🧾 توليد محضر":
    st.subheader("إنشاء محضر دورة")

    titre = st.text_input("عنوان الدورة")
    contenu = st.text_area("محتوى المحضر")

    if st.button("إنشاء"):
        texte = f"""
        محضر دورة

        العنوان: {titre}

        المحتوى:
        {contenu}

        التاريخ: {date.today()}
        """
        st.download_button("تحميل المحضر", texte)
