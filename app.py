import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة وقاعدة البيانات ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

def get_conn():
    conn = sqlite3.connect("askaouen_v7.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_total REAL, estimate_per_lot TEXT, date_j1 TEXT, date_j2 TEXT, date_portail TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 2. دالة توليد المستندات (مع تفعيل العروض المالية السطرية) ---
def generate_askaouen_doc(doc_key, m):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.left_margin = Cm(1.5), Cm(2)
    
    # الترويسة [cite: 1]
    header = doc.add_paragraph()
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE ASKAOUEN").bold = True

    # مسميات الملفات حسب قائمتك [cite: 2, 3, 4, 5, 6, 7, 8, 9]
    titles = {
        "pv_admin": "Pv de dossier administrative et technique",
        "pv_tech_exist": "Pv de dossier administrative et technique et offer technique si existance",
        "os_comm": "Os-commencement",
        "os_notif": "Os-notification",
        "pv_3eme": "Pv de 3 eme seance pour le complement",
        "rapport_tech": "Rapport de sous commisession pour etudier offer tech",
        "pv_fin": "Pv de dossier offer financier"
    }
    
    doc.add_paragraph("\n")
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{titles.get(doc_key, '').upper()}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True; run_t.font.size = Pt(14); run_t.underline = True

    doc.add_paragraph(f"\nOBJET : {m['market_object']}").bold = True
    doc.add_paragraph(f"ESTIMATION TOTALE : {m['estimate_total']} DHS TTC")
    if m['estimate_per_lot']:
        doc.add_paragraph(f"ESTIMATION PAR LOT : {m['estimate_per_lot']}")

    # --- عرض المتنافسين والعروض المالية بشكل سطري (Ligne) [ملاحظتك الأخيرة] ---
    conn = get_conn()
    comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    
    if comps:
        doc.add_paragraph("\nPRESENTATION DES OFFRES DES CONCURRENTS :").bold = True
        for c in comps:
            p = doc.add_paragraph(style='List Bullet')
            # في محضر العرض المالي (PV Finance) نظهر المبلغ بوضوح 
            if doc_key == "pv_fin":
                p.add_run(f"La société : ").bold = True
                p.add_run(f"{c['company_name']}")
                p.add_run(f" a proposé une offre de : ").bold = True
                p.add_run(f"{c['offer_amount']} DHS TTC.")
            else:
                p.add_run(f"Concurrent : {c['company_name']} | Statut : {c['status']}")

    # التوقيعات (اللجنة)
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    conn.close()
    if members:
        doc.add_paragraph("\n\nMEMBRES DE LA COMMISSION :").bold = True
        for mem in members:
            doc.add_paragraph(f"- {mem['member_name']} ({mem['member_role']}) : ...........................")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- 3. واجهة المستخدم ---
init_db()
st.title("📂 نظام تدبير صفقات جماعة أسكاون")

tabs = st.tabs(["الصفقة", "المتنافسون واللجنة", "تحميل الملفات"])

with tabs[0]:
    with st.form("m_form"):
        c1, c2 = st.columns(2)
        ref = c1.text_input("مرجع الصفقة")
        p_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert", "Appel d'offres ouvert national", "Appel d'offres simplifié"])
        obj = c1.text_area("الموضوع")
        amt_total = c2.number_input("التقدير الإجمالي", min_value=0.0)
        amt_lots = c2.text_input("التقدير لكل حصة")
        j1, j2, port = c2.date_input("جريدة 1"), c2.date_input("جريدة 2"), c2.date_input("البوابة")
        if st.form_submit_button("حفظ"):
            conn = get_conn()
            conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_total, estimate_per_lot, date_j1, date_j2, date_portail) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt_total, amt_lots, str(j1), str(j2), str(port)))
            conn.commit(); conn.close(); st.success("تم الحفظ")

with tabs[1]:
    all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
    if all_m:
        sel = st.selectbox("اختر الصفقة:", all_m)
        c1, c2 = st.columns(2)
        with c1.form("comp"):
            n, o = st.text_input("الشركة"), st.number_input("العرض المالي (Offre)", min_value=0.0)
            s = st.selectbox("الحالة", ["Admis", "Écarté"])
            if st.form_submit_button("إضافة متنافس"):
                conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (sel, n, o, s)); conn.commit(); conn.close(); st.success("تم")
        with c2.form("comm"):
            m_n, m_r = st.text_input("اسم العضو"), st.text_input("الصفة")
            if st.form_submit_button("إضافة عضو لجنة"):
                conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (sel, m_n, m_r)); conn.commit(); conn.close(); st.success("تم")

with tabs[2]:
    rows = get_conn().execute("SELECT * FROM markets").fetchall()
    if rows:
        target = st.selectbox("اختر الصفقة:", [r['market_ref'] for r in rows])
        m_data = next(dict(r) for r in rows if r['market_ref'] == target)
        doc_list = [
            ("pv_admin", "Pv dossier administratif [cite: 3]"),
            ("pv_tech_exist", "Pv administratif et technique/offre tech [cite: 4]"),
            ("pv_3eme", "Pv 3ème séance (Complément) [cite: 7]"),
            ("rapport_tech", "Rapport sous-commission tech [cite: 8]"),
            ("pv_fin", "Pv dossier offre financier (مع العروض المالية) "),
            ("os_comm", "Os-commencement [cite: 5]"),
            ("os_notif", "Os-notification [cite: 6]")
        ]
        for k, v in doc_list:
            if st.button(f"تجهيز {v}"):
                data = generate_askaouen_doc(k, m_data)
                st.download_button(f"📥 تحميل {v}", data, f"{k}_{target}.docx")
