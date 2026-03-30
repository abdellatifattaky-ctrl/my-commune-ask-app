import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. إدارة قاعدة البيانات (تجنب أخطاء OperationalError) ---
def get_conn():
    # استخدام اسم قاعدة بيانات جديد لضمان تحديث الجداول
    conn = sqlite3.connect("askaouen_final_system.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # جدول الصفقات الرئيسي
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

# --- 3. محرك توليد المستندات (مطابق لقائمتك حرفياً) ---
def generate_askaouen_docx(doc_key, m_data):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.left_margin = Cm(1.5), Cm(2)
    
    # الترويسة الرسمية للجماعة
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE ASKAOUEN").bold = True

    doc.add_paragraph("\n")

    # مسميات الملفات المأخوذة من ملفك النصي 
    titles = {
        "admin": "Pv de dossier administrative et technique",
        "tech": "Pv de dossier administrative et technique et offer technique si existance",
        "fin": "Pv de dossier offer financier",
        "3eme": "Pv de 3 eme seance pour le complement",
        "rapport": "Rapport de sous commisession pour etudier offer tech",
        "os_comm": "Os-commencement",
        "os_notif": "Os-notification"
    }
    
    display_title = titles.get(doc_key, "DOCUMENT")
    
    # العنوان المركزي المنسق
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{display_title.upper()}\n{m_data['procedure_type'].upper()} N° : {m_data['market_ref']}")
    run_t.bold = True
    run_t.font.size = Pt(14)
    run_t.underline = True

    # البيانات الأساسية
    doc.add_paragraph(f"\nOBJET : {m_data['market_object']}").bold = True
    doc.add_paragraph(f"ESTIMATION DU MAITRE D'OUVRAGE : {m_data['estimate_amount']} DHS TTC")

    # إضافة جدول المتنافسين (للمحاضر فقط)
    if "pv" in doc_key or "rapport" in doc_key or "admin" in doc_key or "fin" in doc_key:
        conn = get_conn()
        comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m_data['market_ref'],)).fetchall()
        if comps:
            doc.add_paragraph("\nLISTE DES CONCURRENTS :").bold = True
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = "Concurrent", "Montant de l'offre", "Décision"
            for c in comps:
                row = table.add_row().cells
                row[0].text, row[1].text, row[2].text = str(c['company_name']), f"{c['offer_amount']} DHS", str(c['status'])
        conn.close()

    # التوقيعات (اللجنة)
    conn = get_conn()
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m_data['market_ref'],)).fetchall()
    conn.close()
    if members:
        doc.add_paragraph("\n\nSIGNATURE DES MEMBRES DE LA COMMISSION :").bold = True
        sig_tbl = doc.add_table(rows=0, cols=2)
        for mem in members:
            row = sig_tbl.add_row().cells
            row[0].text, row[1].text = mem['member_name'], f"({mem['member_role']})"

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم (Streamlit) ---
init_db()
st.sidebar.title("SMART PRO+ ASKAOUEN")
menu = st.sidebar.radio("القائمة الرئيسية", ["إدارة الصفقات"])

if menu == "إدارة الصفقات":
    st.markdown('<h2 style="text-align: center;">نظام تدبير الصفقات العمومية - جماعة أسكاون</h2>', unsafe_allow_html=True)
    tabs = st.tabs(["📝 تسجيل صفقة", "🏢 المتنافسون", "👥 اللجنة", "📄 تحميل الملفات"])

    # تسجيل الصفقة
    with tabs[0]:
        with st.form("m_form"):
            c1, col2 = st.columns(2)
            m_ref = c1.text_input("N° AO (مرجع الصفقة)")
            m_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert national", "Appel d'offres simplifié"])
            m_obj = c1.text_area("الموضوع")
            m_amt = col2.number_input("التقدير المالي", min_value=0.0)
            d_j1, d_j2, d_p = col2.date_input("جريدة 1"), col2.date_input("جريدة 2"), col2.date_input("تاريخ البوابة")
            if st.form_submit_button("حفظ الصفقة"):
                try:
                    conn = get_conn()
                    conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_amount, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (m_ref, m_obj, m_type, m_amt, str(d_j1), str(d_j2), str(d_p), str(date.today())))
                    conn.commit(); conn.close(); st.success("✅ تم حفظ البيانات!"); st.rerun()
                except: st.error("⚠️ المرجع موجود مسبقاً")

    # تحميل الملفات (مطابق لقائمة ملفك )
    with tabs[3]:
        rows = get_conn().execute("SELECT * FROM markets").fetchall()
        if rows:
            sel_ref = st.selectbox("اختر الصفقة لإصدار الوثائق:", [r['market_ref'] for r in rows])
            m_data = next(dict(r) for r in rows if r['market_ref'] == sel_ref)
            st.divider()
            
            # مسميات الأزرار والملفات بناءً على القائمة المطلوبة 
            doc_list = [
                ("admin", "Pv dossier administratif"),
                ("tech", "Pv dossier technique"),
                ("3eme", "Pv 3ème séance"),
                ("rapport", "Rapport sous-commission"),
                ("fin", "Pv offre financier"),
                ("os_comm", "Os-commencement"),
                ("os_notif", "Os-notification")
            ]
            
            c1, c2 = st.columns(2)
            for i, (k, v) in enumerate(doc_list):
                col = c1 if i % 2 == 0 else c2
                if col.button(f"🛠️ تجهيز {v}", key=f"btn_{k}"):
                    file_data = generate_askaouen_docx(k, m_data)
                    col.download_button(f"📥 تحميل {v}", file_data, f"{v}_{sel_ref}.docx")
        else: st.warning("لا توجد بيانات مسجلة.")
