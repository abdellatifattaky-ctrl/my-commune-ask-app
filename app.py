import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ الصفقات", layout="wide")

# --- 2. إدارة قاعدة البيانات (V4) ---
def get_conn():
    conn = sqlite3.connect("procurement_v4.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # جدول الصفقات
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_amount REAL, date_j1 TEXT, date_j2 TEXT,
        date_portail TEXT, created_at TEXT)""")
    
    # جدول المتنافسين
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    
    # جدول أعضاء اللجنة
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    
    conn.commit()
    conn.close()

# --- 3. دالة توليد ملفات الوورد الذكية ---
def generate_docx(doc_title, m):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    
    # الرأس (Header)
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE ASKAOUEN").bold = True

    doc.add_paragraph("\n")
    
    # العنوان
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{doc_title}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True
    run_t.font.size = Pt(14)

    # التفاصيل
    doc.add_paragraph(f"Objet: {m['market_object']}")
    doc.add_paragraph(f"Estimation: {m['estimate_amount']} DHS TTC")
    doc.add_paragraph(f"Publicité: J1: {m['date_j1']} | J2: {m['date_j2']} | Portail: {m['date_portail']}")

    # إضافة المتنافسين
    conn = get_conn()
    comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    if comps:
        doc.add_paragraph("\nTableau des Concurrents:").bold = True
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text = "Concurrent", "Montant", "Décision"
        for c in comps:
            row = table.add_row().cells
            row[0].text, row[1].text, row[2].text = c['company_name'], f"{c['offer_amount']} DHS", c['status']

    # إضافة أعضاء اللجنة (التوقيعات)
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    conn.close()
    
    if members:
        doc.add_paragraph("\n\nSignature des membres de la commission :").bold = True
        sig_table = doc.add_table(rows=0, cols=2)
        for mem in members:
            row = sig_table.add_row().cells
            row[0].text = mem['member_name']
            row[1].text = f"({mem['member_role']})"

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today()}")
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم ---
init_db()
menu = st.sidebar.selectbox("القائمة", ["الصفقات العمومية"])

if menu == "الصفقات العمومية":
    st.markdown('<h2 style="text-align: center;">نظام SMART PRO+ لإدارة الصفقات</h2>', unsafe_allow_html=True)
    tabs = st.tabs(["➕ تسجيل صفقة", "👥 المتنافسون", "📋 اللجنة", "📄 تحميل المحاضر"])

    # تسجيل الصفقة
    with tabs[0]:
        with st.form("m_form"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("مرجع الصفقة")
            p_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert", "Appel d'offres ouvert national", "Appel d'offres simplifié"])
            obj = c1.text_area("الموضوع")
            amt = c2.number_input("التقدير المالي", min_value=0.0)
            j1, j2, port = c2.date_input("ج1"), c2.date_input("ج2"), c2.date_input("البوابة")
            if st.form_submit_button("حفظ"):
                conn = get_conn()
                conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_amount, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port), str(date.today())))
                conn.commit(); conn.close(); st.success("تم الحفظ!"); st.rerun()

    # المتنافسون
    with tabs[1]:
        all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
        if all_m:
            s_m = st.selectbox("اختر الصفقة:", all_m, key="comp_s")
            with st.form("c_form"):
                n, o = st.text_input("الشركة"), st.number_input("المبلغ", min_value=0.0)
                s = st.selectbox("الحالة", ["Admis", "Écarté"])
                if st.form_submit_button("إضافة"):
                    conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (s_m, n, o, s)); conn.commit(); conn.close(); st.success("تمت الإضافة")
        else: st.info("سجل صفقة أولاً")

    # اللجنة (الجديد)
    with tabs[2]:
        if all_m:
            s_m_l = st.selectbox("اختر الصفقة لتحديد لجنتها:", all_m, key="comm_s")
            with st.form("l_form"):
                m_n = st.text_input("اسم العضو")
                m_r = st.selectbox("الصفة", ["الرئيس", "عضو", "ممثل الخازن"])
                if st.form_submit_button("إضافة عضو"):
                    conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (s_m_l, m_n, m_r)); conn.commit(); conn.close(); st.success("تمت إضافة العضو")
        else: st.info("سجل صفقة أولاً")

    # التحميل
    with tabs[3]:
        markets = get_conn().execute("SELECT * FROM markets").fetchall()
        if markets:
            t_ref = st.selectbox("اختر الصفقة للتحميل:", [r['market_ref'] for r in markets])
            m_data = next(dict(r) for r in markets if r['market_ref'] == t_ref)
            st.divider()
            c1, c2, c3 = st.columns(3)
            for i, (k, l) in enumerate([("PV1", "PV1"), ("PV2", "PV2"), ("PV3", "PV3"), ("Rapport", "Rapport"), ("OS", "OS"), ("Notif", "Notification")]):
                col = [c1, c2, c3][i % 3]
                if col.button(f"إنشاء {l}", key=f"b_{k}"):
                    data = generate_docx(l, m_data)
                    col.download_button(f"📥 تحميل {l}", data, f"{l}_{t_ref}.docx", key=f"d_{k}")
