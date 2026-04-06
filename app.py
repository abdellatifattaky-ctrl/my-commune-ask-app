import streamlit as st
from datetime import date

st.set_page_config(page_title="محاضر الصفقات", layout="wide")

st.title("📄 نظام توليد محاضر الصفقات")

# =========================
# SESSION
# =========================
if "data" not in st.session_state:
    st.session_state.data = {
        "reference": "",
        "objet": "",
        "date": str(date.today()),
        "heure": "10:00",
        "lieu": "",
        "president": "",
        "membres": [],
        "concurrents": []
    }

# =========================
# SIDEBAR
# =========================
page = st.sidebar.radio("القائمة", [
    "المعلومات",
    "اللجنة",
    "المتنافسون",
    "PV 1 (فتح)",
    "PV 2 (مالي)",
    "PV 3 (الإسناد)"
])

# =========================
# PAGE 1
# =========================
if page == "المعلومات":
    st.subheader("معلومات الصفقة")

    st.session_state.data["reference"] = st.text_input("رقم الصفقة")
    st.session_state.data["objet"] = st.text_input("موضوع الصفقة")
    st.session_state.data["date"] = str(st.date_input("التاريخ"))
    st.session_state.data["heure"] = st.text_input("الساعة", "10:00")
    st.session_state.data["lieu"] = st.text_input("المكان")
    st.session_state.data["president"] = st.text_input("الرئيس")

# =========================
# PAGE 2
# =========================
elif page == "اللجنة":
    st.subheader("أعضاء اللجنة")

    nb = st.number_input("عدد الأعضاء", 1, 10, 3)

    st.session_state.data["membres"] = []
    for i in range(nb):
        name = st.text_input(f"عضو {i+1}", key=f"m{i}")
        role = st.selectbox("الصفة", ["عضو", "مقرر", "رئيس"], key=f"r{i}")
        st.session_state.data["membres"].append(f"{name} ({role})")

# =========================
# PAGE 3
# =========================
elif page == "المتنافسون":
    st.subheader("المتنافسون")

    nb = st.number_input("عدد المتنافسين", 1, 20, 3)

    st.session_state.data["concurrents"] = []
    for i in range(nb):
        name = st.text_input(f"شركة {i+1}", key=f"c{i}")
        montant = st.number_input(f"المبلغ {i+1}", key=f"m{i}", step=1000.0)
        st.session_state.data["concurrents"].append((name, montant))

# =========================
# PV1
# =========================
elif page == "PV 1 (فتح)":
    if st.button("توليد PV1"):
        d = st.session_state.data

        concurrents = "\n".join([f"{i+1}) {c[0]}" for i, c in enumerate(d["concurrents"])])

        pv = f"""
PROCES VERBAL D'APPEL D'OFFRES OUVERT

Séance Publique

Le {d['date']} à {d['heure']} la commission s’est réunie à {d['lieu']}.

Président : {d['president']}
Membres : {", ".join(d['membres'])}

Objet : {d['objet']}
N° : {d['reference']}

Liste des concurrents :
{concurrents}

La séance est levée.
"""

        st.text_area("PV1", pv, height=400)

# =========================
# PV2
# =========================
elif page == "PV 2 (مالي)":
    if st.button("توليد PV2"):
        d = st.session_state.data

        lignes = "\n".join([f"{c[0]} : {c[1]} DHS" for c in d["concurrents"]])

        pv = f"""
PROCES VERBAL 2ème Séance

Objet : {d['objet']}

Ouverture des offres financières :

{lignes}

Classement effectué.
"""

        st.text_area("PV2", pv, height=400)

# =========================
# PV3
# =========================
elif page == "PV 3 (الإسناد)":
    if st.button("توليد PV3"):
        d = st.session_state.data

        winner = min(d["concurrents"], key=lambda x: x[1]) if d["concurrents"] else ("", 0)

        pv = f"""
PROCES VERBAL 3ème Séance

Après étude des offres,
La commission propose l’attribution du marché à :

{winner[0]} pour un montant de {winner[1]} DHS

Objet : {d['objet']}
"""

        st.text_area("PV3", pv, height=400)
