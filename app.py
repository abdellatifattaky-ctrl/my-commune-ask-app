import streamlit as st
from datetime import date

st.set_page_config(page_title="محاضر الصفقات", layout="wide")

# =========================
# INIT
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
    "PV 1",
    "PV 2",
    "PV 3"
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

    membres = []
    for i in range(nb):
        name = st.text_input(f"اسم العضو {i+1}", key=f"m{i}")
        role = st.selectbox("الصفة", ["رئيس", "عضو", "مقرر"], key=f"r{i}")
        membres.append(f"{name} ({role})")

    st.session_state.data["membres"] = membres

# =========================
# PAGE 3
# =========================
elif page == "المتنافسون":
    st.subheader("المتنافسون")

    nb = st.number_input("عدد المتنافسين", 1, 20, 3)

    concurrents = []
    for i in range(nb):
        name = st.text_input(f"اسم الشركة {i+1}", key=f"c{i}")
        montant = st.number_input(f"المبلغ {i+1}", key=f"amt{i}", step=1000.0)
        concurrents.append((name, montant))

    st.session_state.data["concurrents"] = concurrents

# =========================
# PV1
# =========================
elif page == "PV 1":
    if st.button("توليد محضر فتح الأظرفة"):
        d = st.session_state.data

        liste = "\n".join([f"{i+1}) {c[0]}" for i, c in enumerate(d["concurrents"])])

        pv = f"""
PROCES VERBAL D'APPEL D'OFFRES OUVERT

1ère Séance Publique

Le {d['date']} à {d['heure']} la commission s’est réunie à {d['lieu']}.

Président : {d['president']}
Membres : {", ".join(d['membres'])}

Objet : {d['objet']}
N° : {d['reference']}

Liste des concurrents :
{liste}

La séance est levée.
"""

        st.text_area("المحضر", pv, height=400)

# =========================
# PV2
# =========================
elif page == "PV 2":
    if st.button("توليد محضر التقييم"):
        d = st.session_state.data

        lignes = "\n".join([f"{c[0]} : {c[1]} DHS" for c in d["concurrents"]])

        pv = f"""
PROCES VERBAL 2ème Séance

Objet : {d['objet']}

Ouverture des offres financières :

{lignes}

Classement effectué.
"""

        st.text_area("المحضر", pv, height=400)

# =========================
# PV3
# =========================
elif page == "PV 3":
    if st.button("توليد محضر الإسناد"):
        d = st.session_state.data

        if d["concurrents"]:
            winner = min(d["concurrents"], key=lambda x: x[1])
        else:
            winner = ("", 0)

        pv = f"""
PROCES VERBAL 3ème Séance

Après étude des offres،
La commission propose إسناد الصفقة إلى :

{winner[0]} بمبلغ {winner[1]} DHS

Objet : {d['objet']}
"""

        st.text_area("المحضر", pv, height=400)
