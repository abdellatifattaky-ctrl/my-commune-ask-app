import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# إنشاء جدول إن لم يكن موجود
c.execute('''
CREATE TABLE IF NOT EXISTS courriers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    objet TEXT,
    date TEXT
)
''')
conn.commit()

# واجهة التطبيق
st.title("📂 SGCA - Gestion des Courriers")

menu = ["Ajouter Courrier", "Afficher Courriers"]
choice = st.sidebar.selectbox("Menu", menu)

# إضافة مراسلة
if choice == "Ajouter Courrier":
    st.subheader("➕ Ajouter un courrier")

    type_courrier = st.selectbox("Type", ["Arrivé", "Départ"])
    objet = st.text_input("Objet")
    date_c = st.date_input("Date", date.today())

    if st.button("Enregistrer"):
        c.execute("INSERT INTO courriers (type, objet, date) VALUES (?, ?, ?)",
                  (type_courrier, objet, str(date_c)))
        conn.commit()
        st.success("✅ Courrier enregistré")

# عرض المراسلات
elif choice == "Afficher Courriers":
    st.subheader("📄 Liste des courriers")

    df = pd.read_sql_query("SELECT * FROM courriers", conn)
    st.dataframe(df)

    st.write("📊 Statistiques")
    st.write(df['type'].value_counts())
