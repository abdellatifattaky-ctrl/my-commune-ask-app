import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. قاعدة البيانات (إصدار ثابت لتجنب أخطاء الصور السابقة) ---
def get_conn():
    conn = sqlite3.connect("askaouen_final_v5.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_amount REAL, date_j1 TEXT, date_j2 TEXT,
        date_portail TEXT, created_at TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 3. دالة توليد المستندات (مطابقة تماماً لقائمتك) ---
def generate_askaouen_doc(doc_key, m):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.left_margin = Cm(1.5), Cm(2)
    
    # الترويسة الرسمية
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE ASKAOUEN").bold = True

    doc.add_paragraph("\n")

    # مسميات الملفات كما وردت في ملفك "program les marche docx.docx"
    doc_titles = {
        "pv_admin": "Pv de dossier administrative et technique",
        "pv_tech": "Pv de dossier administrative et technique et offer technique si existance",
        "pv_3eme": "Pv de 3 eme seance pour le complement",
        "pv_fin": "Pv de dossier offer financier",
        "rapport_tech": "Rapport de sous commisession pour etudier offer tech",
        "os_comm": "Os-commencement",
        "os_notif": "Os-notification"
    }
    
    title_text = doc_titles.get(doc_key, "DOCUMENT")
    
    # العنوان المركزي
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{title_text.upper()}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True
    run_t.font.size = Pt(14)
    run_t.underline = True

    # محتوى المستند
    doc.add_paragraph(f"\nOBJET : {m['market_object']}").bold = True
    doc.add_paragraph(f"ESTIMATION : {m['estimate_amount']} DHS TTC")
    
    # إضافة جدول المتنافسين للمحاضر
    if "pv" in doc_key or "rapport" in doc_key:
        conn = get_conn()
        comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
        if comps:
            doc.add_paragraph("\nLISTE DES CONCURRENTS :").bold = True
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = "Concurrent", "Montant", "Décision"
            for c in comps:
                row = table.add_row().cells
                row[0].text, row[1].text, row[2].text = str(c['company_name']), f"{c['offer_amount']} DHS", str(c['status'])
        conn.close()

    # التوقيعات (أعضاء اللجنة)
    doc.add_paragraph("\n\nSIGNATURES :").bold = True
    conn = get_conn()
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    conn.close()
    if members:
        sig_tbl = doc.add_table(rows=0, cols=2)
        for mem in members:
            row = sig_tbl.add_row().cells
            row[0].text, row[1].text = mem['member_name'], f"({mem['member_role']})"

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم ---
init_db()
st.title("📂 نظام تدبير الصفقات - جماعة أسكاون")

tabs = st.tabs(["1️⃣ تسجيل الصفقة", "2️⃣ المتنافسون واللجنة", "3️⃣ تحميل الملفات (DOCX)"])

with tabs[0]:
    with st.form("market_form"):
        col1, col2 = st.columns(2)
        ref = col1.text_input("مرجع الصفقة (N° AO)")
        p_type = col1.selectbox("نوع المسطرة", ["Appel d'offres ouvert national", "Appel d'offres simplifié"])
        obj = col1.text_area("الموضوع")
        amt = col2.number_input("التقدير المالي", min_value=0.0)
        j1, j2, port = col2.date_input("ج1"), col2.date_input("ج2"), col2.date_input("البوابة")
        if st.form_submit_button("حفظ الصفقة"):
            conn = get_conn()
            conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_amount, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port), str(date.today())))
            conn.commit(); conn.close(); st.success("تم الحفظ!")

with tabs[1]:
    all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
    if all_m:
        sel_m = st.selectbox("اختر الصفقة:", all_m)
        c1, c2 = st.columns(2)
        with c1.form("comp_f"):
            st.write("إضافة متنافس")
            n, o = st.text_input("الشركة"), st.number_input("المبلغ", min_value=0.0)
            s = st.selectbox("القرار", ["Admis", "Écarté"])
            if st.form_submit_button("إضافة شركة"):
                conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (sel_m, n, o, s)); conn.commit(); conn.close(); st.success("تم")
        with c2.form("comm_f"):
            st.write("إضافة عضو لجنة")
            m_n, m_r = st.text_input("الاسم"), st.text_input("الصفة")
            if st.form_submit_button("إضافة عضو"):
                conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (sel_m, m_n, m_r)); conn.commit(); conn.close(); st.success("تم")

with tabs[2]:
    markets = get_conn().execute("SELECT * FROM markets").fetchall()
    if markets:
        target = st.selectbox("اختر الصفقة للتحميل:", [r['market_ref'] for r in markets], key="final_sel")
        m_data = next(dict(r) for r in markets if r['market_ref'] == target)
        
        st.write("### 📄 القائمة الرسمية للملفات:")
        # هذه القائمة مطابقة تماماً للملف النصي الذي رفعته 
        doc_list = [
            ("pv_admin", "Pv de dossier administrative et technique"),
            ("pv_tech", "Pv technique et offre technique"),
            ("pv_3eme", "Pv 3ème séance (Complément)"),
            ("rapport_tech", "Rapport sous-commission tech"),
            ("pv_fin", "Pv dossier offre financier"),
            ("os_comm", "Os-commencement"),
            ("os_notif", "Os-notification")
        ]
        
        c1, c2 = st.columns(2)
        for i, (key, label) in enumerate(doc_list):
            col = c1 if i % 2 == 0 else c2
            if col.button(f"🛠️ تجهيز {label}"):
                file_bytes = generate_askaouen_doc(key, m_data)
                col.download_button(f"📥 تحميل {label}", file_bytes, f"{key}_{target}.docx")
    else:
        st.warning("لا توجد صفقات مسجلة.")
