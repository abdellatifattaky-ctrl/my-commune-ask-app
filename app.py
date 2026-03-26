import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# =========================
# DB CONNECTION
# =========================
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# =========================
# TABLES CREATION
# =========================
c.execute('''CREATE TABLE IF NOT EXISTS courriers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    objet TEXT,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS marches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objet TEXT,
    entreprise TEXT,
    montant REAL,
    statut TEXT,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS conseils (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sujet TEXT,
    decision TEXT,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS employes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    poste TEXT
)''')

conn.commit()

# =========================
# APP UI
# =========================
st.set_page_config(page_title="SGCA", layout="wide")

st.title("🏛️ SGCA - Gestion Communale")

menu = [
    "Dashboard",
    "Courriers",
    "Marchés Publics",
    "Conseil Communal",
    "Employés"
]

choice = st.sidebar.selectbox("Menu", menu)

# =========================
# DASHBOARD
# =========================
if choice == "Dashboard":
    st.subheader("📊 Tableau de bord")

    df_c = pd.read_sql("SELECT * FROM courriers", conn)
    df_m = pd.read_sql("SELECT * FROM marches", conn)
    df_con = pd.read_sql("SELECT * FROM conseils", conn)

    col1, col2, col3 = st.columns(3)

    col1.metric("Courriers", len(df_c))
    col2.metric("Marchés", len(df_m))
    col3.metric("Décisions Conseil", len(df_con))

    st.write("📈 Répartition des courriers")
    if not df_c.empty:
        st.bar_chart(df_c['type'].value_counts())

# =========================
# COURRIERS
# =========================
elif choice == "Courriers":
    st.subheader("📥📤 Gestion des Courriers")

    tab1, tab2 = st.tabs(["Ajouter", "Liste"])

    with tab1:
        type_c = st.selectbox("Type", ["Arrivé", "Départ"])
        objet = st.text_input("Objet")
        date_c = st.date_input("Date", date.today())

        if st.button("Enregistrer Courrier"):
            c.execute("INSERT INTO courriers (type, objet, date) VALUES (?, ?, ?)",
                      (type_c, objet, str(date_c)))
            conn.commit()
            st.success("✅ Enregistré")

    with tab2:
        df = pd.read_sql("SELECT * FROM courriers", conn)
        st.dataframe(df)

# =========================
# MARCHÉS PUBLICS
# =========================
elif choice == "Marchés Publics":
    st.subheader("🏗️ Gestion des Marchés")

    tab1, tab2 = st.tabs(["Ajouter Marché", "Liste"])

    with tab1:
        objet = st.text_input("Objet du marché")
        entreprise = st.text_input("Entreprise")
        montant = st.number_input("Montant", min_value=0.0)
        statut = st.selectbox("Statut", ["Préparation", "En cours", "Terminé"])
        date_m = st.date_input("Date", date.today())

        if st.button("Ajouter Marché"):
            c.execute("INSERT INTO marches (objet, entreprise, montant, statut, date) VALUES (?, ?, ?, ?, ?)",
                      (objet, entreprise, montant, statut, str(date_m)))
            conn.commit()
            st.success("✅ Marché ajouté")

    with tab2:
        df = pd.read_sql("SELECT * FROM marches", conn)
        st.dataframe(df)

# =========================
# CONSEIL COMMUNAL
# =========================
elif choice == "Conseil Communal":
    st.subheader("🏛️ Conseil Communal")

    tab1, tab2 = st.tabs(["Ajouter Décision", "Liste"])

    with tab1:
        sujet = st.text_input("Sujet")
        decision = st.text_area("Décision")
        date_con = st.date_input("Date", date.today())

        if st.button("Ajouter Décision"):
            c.execute("INSERT INTO conseils (sujet, decision, date) VALUES (?, ?, ?)",
                      (sujet, decision, str(date_con)))
            conn.commit()
            st.success("✅ Décision ajoutée")

    with tab2:
        df = pd.read_sql("SELECT * FROM conseils", conn)
        st.dataframe(df)

# =========================
# EMPLOYES
# =========================
elif choice == "Employés":
    st.subheader("👥 Gestion des Employés")

    tab1, tab2 = st.tabs(["Ajouter Employé", "Liste"])

    with tab1:
        nom = st.text_input("Nom")
        poste = st.text_input("Poste")

        if st.button("Ajouter Employé"):
            c.execute("INSERT INTO employes (nom, poste) VALUES (?, ?)",
                      (nom, poste))
            conn.commit()
            st.success("✅ Employé ajouté")

    with tab2:
        df = pd.read_sql("SELECT * FROM employes", conn)
        st.dataframe(df)
