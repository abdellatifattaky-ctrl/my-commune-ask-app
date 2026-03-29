import streamlit as st
import sqlite3

# ================= DATABASE =================
def get_conn():
    return sqlite3.connect("commune.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS correspondences (id INTEGER PRIMARY KEY, ref TEXT, subject TEXT, type TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS licenses (id INTEGER PRIMARY KEY, name TEXT, type TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT, progress INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS procurements (id INTEGER PRIMARY KEY, ref TEXT, subject TEXT)")

    conn.commit()
    conn.close()

def fetch(table):
    conn = get_conn()
    data = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    return data

def insert(table, values):
    conn = get_conn()
    placeholders = ",".join(["?"] * len(values))
    conn.execute(f"INSERT INTO {table} VALUES(NULL,{placeholders})", values)
    conn.commit()
    conn.close()

# ================= APP =================
st.set_page_config(page_title="نظام الجماعة", layout="wide")
init_db()

st.title("🏛️ نظام تدبير مصالح الجماعة")

menu = st.sidebar.selectbox("القائمة", [
    "لوحة القيادة",
    "المراسلات",
    "الرخص",
    "الموظفون",
    "المشاريع",
    "الصفقات"
])

# ================= DASHBOARD =================
if menu == "لوحة القيادة":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("المراسلات", len(fetch("correspondences")))
    c2.metric("الرخص", len(fetch("licenses")))
    c3.metric("الموظفون", len(fetch("employees")))
    c4.metric("الصفقات", len(fetch("procurements")))

# ================= CORRESPONDENCE =================
elif menu == "المراسلات":
    st.subheader("📄 المراسلات")

    with st.form("f1"):
        ref = st.text_input("رقم")
        sub = st.text_input("موضوع")
        typ = st.selectbox("نوع", ["واردة","صادرة"])
        if st.form_submit_button("حفظ"):
            insert("correspondences",(ref,sub,typ))
            st.success("تم الحفظ")

    st.dataframe(fetch("correspondences"))

# ================= LICENSE =================
elif menu == "الرخص":
    st.subheader("🧾 الرخص")

    with st.form("f2"):
        name = st.text_input("اسم")
        typ = st.selectbox("نوع", ["بناء","سكن"])
        if st.form_submit_button("حفظ"):
            insert("licenses",(name,typ))
            st.success("تم")

    st.dataframe(fetch("licenses"))

# ================= EMPLOYEE =================
elif menu == "الموظفون":
    st.subheader("👥 الموظفون")

    with st.form("f3"):
        name = st.text_input("اسم")
        dept = st.text_input("مصلحة")
        if st.form_submit_button("حفظ"):
            insert("employees",(name,dept))
            st.success("تم")

    st.dataframe(fetch("employees"))

# ================= PROJECT =================
elif menu == "المشاريع":
    st.subheader("🏗 المشاريع")

    with st.form("f4"):
        name = st.text_input("اسم المشروع")
        progress = st.slider("نسبة التقدم",0,100)
        if st.form_submit_button("حفظ"):
            insert("projects",(name,progress))
            st.success("تم")

    data = fetch("projects")
    st.dataframe(data)

    for d in data:
        st.write(d[1])
        st.progress(d[2])

# ================= PROCUREMENT =================
elif menu == "الصفقات":
    st.subheader("📑 الصفقات")

    with st.form("f5"):
        ref = st.text_input("مرجع الصفقة")
        sub = st.text_input("موضوع")
        if st.form_submit_button("حفظ"):
            insert("procurements",(ref,sub))
            st.success("تم")

    st.dataframe(fetch("procurements"))

# ================= FOOTER =================
st.markdown("---")
st.caption("نسخة واحدة - Streamlit + SQLite")
