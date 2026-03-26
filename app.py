import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta
from docx import Document
import os
from fpdf import FPDF

st.set_page_config(page_title="نظام إدارة الجماعة القروية SGCA", layout="wide")
st.title("🏛️ نظام إدارة الجماعة القروية (SGCA)")

# =====================
# إعداد المجلدات وقاعدة البيانات
# =====================
DB_FILE = "sgca.db"
UPLOAD_FOLDER = "uploads"
ARCHIVE_FOLDER = "archive"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# =====================
# إنشاء الجداول الأساسية
# =====================
c.execute('''CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS courrier (
id INTEGER PRIMARY KEY, numero TEXT, type TEXT, objet TEXT, date TEXT, fichier TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS marches (
id INTEGER PRIMARY KEY, numero TEXT, objet TEXT, entreprise TEXT, montant REAL, statut TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS budget (
id INTEGER PRIMARY KEY, type TEXT, montant REAL, description TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS biens (
id INTEGER PRIMARY KEY, nom TEXT, type TEXT, valeur REAL, statut TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS messages (
id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, sujet TEXT, contenu TEXT, date TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS convocations (
id INTEGER PRIMARY KEY, type_conv TEXT, date_reunion TEXT, heure TEXT, lieu TEXT, ordre TEXT, membre TEXT, fichier TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS pv_cour (
id INTEGER PRIMARY KEY, titre TEXT, lieu TEXT, ordre TEXT, membres TEXT, fichier TEXT)''')

conn.commit()

# =====================
# تسجيل الدخول
# =====================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged:
    st.subheader("🔐 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        if user:
            st.session_state.logged = True
            st.session_state.username = username
            st.session_state.role = user[3]
            st.success(f"تم تسجيل الدخول كـ {st.session_state.role}")
        else:
            st.error("خطأ في اسم المستخدم أو كلمة المرور")
    st.stop()

# =====================
# قائمة التطبيق
# =====================
menu = [
"📊 Dashboard",
"📥 مكتب الضبط",
"🏗️ الصفقات",
"🧾 PV الصفقات",
"💰 الميزانية",
"🏠 الأملاك",
"📨 الدورات واللجن",
"✉️ الرسائل"
]

choice = st.sidebar.selectbox("القائمة", menu)

# =====================
# DASHBOARD
# =====================
if choice == "📊 Dashboard":
    st.subheader("📊 لوحة التحكم")
    df_courrier = pd.read_sql("SELECT * FROM courrier", conn)
    df_marches = pd.read_sql("SELECT * FROM marches", conn)
    df_budget = pd.read_sql("SELECT * FROM budget", conn)
    df_biens = pd.read_sql("SELECT * FROM biens", conn)
    df_conv = pd.read_sql("SELECT * FROM convocations", conn)
    df_msg = pd.read_sql(f"SELECT * FROM messages WHERE receiver='{st.session_state.username}'", conn)

    st.metric("عدد المراسلات", len(df_courrier))
    st.metric("عدد الصفقات", len(df_marches))
    st.metric("إجمالي الميزانية", df_budget["montant"].sum() if not df_budget.empty else 0)
    st.metric("عدد الأملاك", len(df_biens))
    st.metric("عدد الاستدعاءات القادمة", len(df_conv))
    st.metric("عدد الرسائل الواردة", len(df_msg))

# =====================
# مكتب الضبط
# =====================
elif choice == "📥 مكتب الضبط":
    st.subheader("📥 إضافة وارد/صادر")
    numero = st.text_input("رقم الوثيقة")
    objet = st.text_input("الموضوع")
    file = st.file_uploader("رفع PDF", type=["pdf"])
    path=""
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(path,"wb") as f:
            f.write(file.getbuffer())
    if st.button("حفظ الوثيقة"):
        c.execute("INSERT INTO courrier VALUES (NULL,?,?,?, ?,?)",
                  (numero,"Arrivé",objet,str(date.today()),path))
        conn.commit()
        st.success("تم الحفظ")
    df = pd.read_sql("SELECT * FROM courrier", conn)
    st.dataframe(df)

# =====================
# الصفقات
# =====================
elif choice == "🏗️ الصفقات":
    st.subheader("🏗️ إضافة صفقة")
    numero = st.text_input("رقم الصفقة")
    objet = st.text_input("موضوع الصفقة")
    entreprise = st.text_input("المقاولة")
    montant = st.number_input("المبلغ")
    statut = st.selectbox("الحالة", ["AO","Ouverture","Analyse","Attribution","Exécution"])
    if st.button("إضافة الصفقة"):
        c.execute("INSERT INTO marches VALUES(NULL,?,?,?,?,?)",
                  (numero,objet,entreprise,montant,statut))
        conn.commit()
        st.success("تمت الإضافة")
    df = pd.read_sql("SELECT * FROM marches", conn)
    st.dataframe(df)

# =====================
# PV الصفقات
# =====================
elif choice == "🧾 PV الصفقات":
    type_pv = st.selectbox("نوع PV", ["Ouverture des plis","Analyse des offres","Attribution"])
    numero = st.text_input("رقم الصفقة")
    objet = st.text_input("موضوع الصفقة")
    entreprise = st.text_input("المقاولة (اختياري)")
    montant = st.text_input("المبلغ (اختياري)")
    if st.button("توليد PV"):
        doc = Document()
        doc.add_heading("Procès-Verbal", 0)
        doc.add_paragraph(f"Marché N°: {numero}")
        doc.add_paragraph(f"Objet: {objet}")
        doc.add_paragraph(f"Type de PV: {type_pv}")
        if entreprise:
            doc.add_paragraph(f"Entreprise: {entreprise}")
        if montant:
            doc.add_paragraph(f"Montant: {montant}")
        doc.add_paragraph("Signature de la commission: __________")
        # رقم تسلسلي تلقائي
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"PV_{type_pv.replace(' ','_')}_{ts}.docx"
        doc.save(file_name)
        # أرشيف تلقائي
        os.rename(file_name, os.path.join(ARCHIVE_FOLDER,file_name))
        with open(os.path.join(ARCHIVE_FOLDER,file_name),"rb") as f:
            st.download_button("📥 تحميل PV الصفقة", f, file_name=file_name)

# =====================
# الميزانية
# =====================
elif choice == "💰 الميزانية":
    st.subheader("💰 إضافة مداخيل أو مصاريف")
    type_b = st.selectbox("نوع العملية", ["Recette","Dépense"])
    montant = st.number_input("المبلغ")
    desc = st.text_input("الوصف")
    if st.button("إضافة"):
        c.execute("INSERT INTO budget VALUES(NULL,?,?,?)",(type_b,montant,desc))
        conn.commit()
        st.success("تمت الإضافة")
    df = pd.read_sql("SELECT * FROM budget", conn)
    st.dataframe(df)

# =====================
# الأملاك
# =====================
elif choice == "🏠 الأملاك":
    st.subheader("🏠 إضافة ملكية")
    nom = st.text_input("اسم الملكية")
    type_b = st.selectbox("نوع الملكية", ["Terrain","Local","Autre"])
    valeur = st.number_input("القيمة")
    statut = st.selectbox("الحالة", ["Loué","Libre"])
    if st.button("إضافة"):
        c.execute("INSERT INTO biens VALUES(NULL,?,?,?,?)",
                  (nom,type_b,valeur,statut))
        conn.commit()
        st.success("تمت الإضافة")
    df = pd.read_sql("SELECT * FROM biens", conn)
    st.dataframe(df)

# =====================
# الدورات واللجن + استدعاءات
# =====================
elif choice == "📨 الدورات واللجن":
    st.subheader("📨 توليد استدعاءات الأعضاء")
    type_conv = st.selectbox("نوع الاستدعاء", ["دورة المجلس", "اجتماع لجنة"])
    date_reunion = st.date_input("تاريخ الاجتماع", date.today())
    heure = st.text_input("الساعة", "10:00")
    lieu = st.text_input("المكان", "مقر الجماعة")
    ordre = st.text_area("جدول الأعمال", "1- الموضوع الأول\n2- الموضوع الثاني")
    membres = st.text_area("أسماء الأعضاء (كل اسم في سطر)", "أحمد\nمحمد\nفاطمة")
    if st.button("توليد الاستدعاءات"):
        files = []
        for membre in membres.split("\n"):
            if not membre.strip():
                continue
            doc = Document()
            doc.add_heading("المملكة المغربية", 0)
            doc.add_paragraph("جماعة …")
            doc.add_heading("📨 استدعاء", level=1)
            doc.add_paragraph(f"إلى السيد/ة: {membre}")
            doc.add_paragraph(f"يشرفني أن أدعوكم لحضور {type_conv} يوم {date_reunion} على الساعة {heure} بـ {lieu}.")
            doc.add_paragraph("جدول الأعمال:\n" + ordre)
            doc.add_paragraph("\nسلام.\nتوقيع الرئيس: __________")
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"convocation_{membre}_{ts}.docx"
            doc.save(file_name)
            os.rename(file_name, os.path.join(ARCHIVE_FOLDER,file_name))
            c.execute("INSERT INTO convocations VALUES(NULL,?,?,?,?,?,?,?,?)",
                      (type_conv,str(date_reunion),heure,lieu,ordre,membre,file_name))
            conn.commit()
            files.append(file_name)
        st.success("تم إنشاء الاستدعاءات")
        for file_name in files:
            with open(os.path.join(ARCHIVE_FOLDER,file_name),"rb") as f:
                st.download_button("📥 تحميل " + file_name, f, file_name=file_name)

# =====================
# الرسائل الداخلية
# =====================
elif choice == "✉️ الرسائل":
    st.subheader("✉️ إرسال رسالة لموظف")
    receiver = st.text_input("إلى (اسم الموظف)")
    sujet = st.text_input("الموضوع")
    contenu = st.text_area("المحتوى")
    if st.button("إرسال"):
        c.execute("INSERT INTO messages VALUES(NULL,?,?,?, ?,?)",
                  (st.session_state.username, receiver, sujet, contenu, str(date.today())))
        conn.commit()
        st.success("تم إرسال الرسالة")
    st.subheader("📥 الرسائل الواردة")
    df = pd.read_sql(f"SELECT * FROM messages WHERE receiver='{st.session_state.username}'", conn)
    st.dataframe(df)
