import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات التطبيق ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. قاعدة البيانات الاحترافية ---
def get_conn():
    conn = sqlite3.connect("askaouen_procurement.db")
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
    # جدول اللجنة
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 3. محرك توليد المحاضر (مطابق للنماذج المرفوعة) ---
def generate_askaouen_doc(doc_type, m):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(1.5), Cm(1.5)
    
    # ترويسة الجماعة (Header)
    header_tbl = doc.add_table(rows=1, cols=2)
    header_tbl.width = Cm(18)
    left_cell = header_tbl.rows[0].cells[0].paragraphs[0]
    left_cell.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE ASKAOUEN").bold = True
    left_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.add_paragraph("\n")

    # تحديد مسمى المحضر بناءً على القائمة المقدمة
    doc_mapping = {
        "PV_ADMIN": "PV DE DOSSIER ADMINISTRATIF ET TECHNIQUE",
        "PV_TECH": "PV DE DOSSIER TECHNIQUE ET OFFRE TECHNIQUE",
        "PV_FIN": "PV DE DOSSIER OFFRE FINANCIER",
        "RAPPORT": "RAPPORT DE LA SOUS-COMMISSION TECHNIQUE",
        "OS_NOTIF": "OS-NOTIFICATION",
        "OS_COMM": "OS-COMMENCEMENT"
    }
    
    title_text = doc_mapping.get(doc_type, doc_type)
    
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title_p.add_run(f"{title_text}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True
    run_t.font.size = Pt(14)
    run_t.underline = True

    doc.add_paragraph(f"\nOBJET : {m['market_object']}").bold = True
    doc.add_paragraph(f"ESTIMATION : {m['estimate_amount']} DHS TTC")

    # إضافة جدول المتنافسين للمحاضر (PVs)
    if "PV" in doc_type or "RAPPORT" in doc_type:
        conn = get_conn()
        comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
        if comps:
            doc.add_paragraph("\nTABLEAU DES OFFRES :").bold = True
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = "Concurrent", "Montant", "Décision"
            for c in comps:
                row = table.add_row().cells
                row[0].text, row[1].text, row[2].text = c['company_name'], f"{c['offer_amount']} DHS", c['status']
        conn.close()

    # التوقيعات (اللجنة)
    doc.add_paragraph("\n\nSIGNATURE DES MEMBRES :").bold = True
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

# --- 4. واجهة البرنامج ---
init_db()
st.sidebar.title("MENU ASKAOUEN")
option = st.sidebar.selectbox("الانتقال إلى:", ["إدارة الصفقات", "الإحصائيات"])

if option == "إدارة الصفقات":
    st.title("💼 تدبير الصفقات العمومية - جماعة أسكاون")
    
    tabs = st.tabs(["الصفقة", "المتنافسون", "اللجنة", "توليد الوثائق"])

    with tabs[0]: # تسجيل الصفقة
        with st.form("m_form"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("مرجع الصفقة")
            p_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert national", "Appel d'offres simplifié"])
            obj = c1.text_area("الموضوع")
            amt = c2.number_input("التقدير", min_value=0.0)
            j1, j2, port = c2.date_input("جريدة 1"), c2.date_input("جريدة 2"), c2.date_input("البوابة")
            if st.form_submit_button("حفظ"):
                conn = get_conn()
                conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_amount, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port), str(date.today())))
                conn.commit(); conn.close(); st.success("تم الحفظ!")

    with tabs[3]: # توليد الوثائق حسب القائمة المطلوبة
        markets = get_conn().execute("SELECT * FROM markets").fetchall()
        if markets:
            sel_ref = st.selectbox("اختر الصفقة لإصدار ملفاتها:", [r['market_ref'] for r in markets])
            m_data = next(dict(r) for r in markets if r['market_ref'] == sel_ref)
            
            st.write("### اختر الوثيقة المراد تحميلها:")
            c1, c2 = st.columns(2)
            
            # الربط مع القائمة التي قدمتها في المستند
            doc_list = [
                ("PV_ADMIN", "Pv dossier administratif [cite: 3]"),
                ("PV_TECH", "Pv dossier technique [cite: 4]"),
                ("PV_FIN", "Pv offre financier [cite: 9]"),
                ("RAPPORT", "Rapport sous-commission [cite: 8]"),
                ("OS_NOTIF", "OS-Notification [cite: 6]"),
                ("OS_COMM", "OS-Commencement [cite: 5]")
            ]
            
            for i, (k, v) in enumerate(doc_list):
                col = c1 if i % 2 == 0 else c2
                if col.button(f"تجهيز {v}"):
                    data = generate_askaouen_doc(k, m_data)
                    col.download_button(f"📥 تحميل {k}", data, f"{k}_{sel_ref}.docx")
