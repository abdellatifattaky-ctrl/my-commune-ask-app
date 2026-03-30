import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. إدارة قاعدة البيانات ---
def get_conn():
    conn = sqlite3.connect("askaouen_markets.db")
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

# --- 3. الدالة الجوهرية: توليد الوثيقة بناءً على قوالبك المرفوعة ---
def generate_from_template(doc_type, m):
    doc = Document()
    
    # ضبط الهوامش (Margins) لتكون مطابقة للوثائق الإدارية
    section = doc.sections[0]
    section.top_margin = Cm(1.2)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

    # --- الترويسة (Header) كما في قوالبك ---
    header_table = doc.add_table(rows=1, cols=2)
    header_table.width = Cm(17)
    
    # الجهة اليسرى (الفرنسية)
    left_cell = header_table.rows[0].cells[0].paragraphs[0]
    left_cell.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCERCLE DE TALIOUINE\nCOMMUNE ASKAOUEN").bold = True
    left_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # الجهة اليمنى (العربية) - إذا أردت إضافتها لاحقاً
    right_cell = header_table.rows[0].cells[1].paragraphs[0]
    right_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")

    # --- العنوان المركزي (مطابق للقالب) ---
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # نستخدم نفس الصياغة الموجودة في صورك
    title_run = title_p.add_run(f"{doc_type}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    title_run.bold = True
    title_run.font.size = Pt(16)
    title_run.underline = True

    doc.add_paragraph("\n")

    # --- متن المحضر (احترام الحقول) ---
    doc.add_paragraph(f"OBJET : {m['market_object']}").bold = True
    
    # المراجع القانونية (نفس التي في قوالبك)
    legal = doc.add_paragraph()
    legal.add_run("Vu le décret n° 2-22-431 du 15 chaabane 1444 (8 mars 2023) relatif aux marchés publics.").italic = True
    
    doc.add_paragraph(f"ESTIMATION DU MAITRE D'OUVRAGE : {m['estimate_amount']} DHS TTC")

    # --- جدول المتنافسين (في حال كان PV2 أو PV3) ---
    if doc_type in ["PV2", "PV3", "Rapport"]:
        doc.add_paragraph("\nLISTE DES CONCURRENTS :").bold = True
        conn = get_conn()
        comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
        if comps:
            table = doc.add_table(rows=1, cols=3)
            table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text, hdr[1].text, hdr[2].text = "CONCURRENT", "MONTANT", "DECISION"
            for c in comps:
                row = table.add_row().cells
                row[0].text, row[1].text, row[2].text = c['company_name'], f"{c['offer_amount']} DHS", c['status']

    # --- التوقيعات في الأسفل (اللجنة المتغيرة) ---
    doc.add_paragraph("\n\nMEMBRES DE LA COMMISSION :").bold = True
    conn = get_conn()
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    conn.close()
    
    if members:
        sig_table = doc.add_table(rows=0, cols=2)
        for mem in members:
            row = sig_table.add_row().cells
            row[0].text = mem['member_name']
            row[1].text = f"({mem['member_role']})"
    else:
        # إذا لم يتم إدخال لجنة، نضع أسطر فارغة للتوقيع اليدوي
        doc.add_paragraph("1. ........................................\n2. ........................................")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم (التطبيق) ---
init_db()
st.sidebar.title("SMART PRO+ V.Final")
menu = st.sidebar.radio("القائمة", ["إدارة الصفقات"])

if menu == "إدارة الصفقات":
    st.markdown('<h2 style="text-align: center;">نظام جماعة أسكاون لتدبير الصفقات</h2>', unsafe_allow_html=True)
    tabs = st.tabs(["📝 تسجيل الصفقة", "🏢 المتنافسون", "👥 اللجنة", "📥 تحميل المحاضر"])

    # تسجيل الصفقة
    with tabs[0]:
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("N° AO (المرجع)")
            p_type = c1.selectbox("Type Procédure", ["Appel d'offres ouvert", "Appel d'offres ouvert national", "Appel d'offres simplifié"])
            obj = c1.text_area("Objet (الموضوع)")
            amt = c2.number_input("Estimation (التقدير المالي)", min_value=0.0)
            j1, j2, port = c2.date_input("Journal 1"), c2.date_input("Journal 2"), c2.date_input("Portail")
            if st.form_submit_button("حفظ الصفقة"):
                conn = get_conn()
                conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_amount, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port), str(date.today())))
                conn.commit(); conn.close(); st.success("تم الحفظ بنجاح!"); st.rerun()

    # المتنافسون
    with tabs[1]:
        all_refs = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
        if all_refs:
            sel = st.selectbox("اختر الصفقة:", all_refs, key="c_sel")
            with st.form("comp_form"):
                n, o = st.text_input("اسم المتنافس"), st.number_input("المبلغ", min_value=0.0)
                s = st.selectbox("القرار", ["Admis", "Écarté"])
                if st.form_submit_button("إضافة"):
                    conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (sel, n, o, s)); conn.commit(); conn.close(); st.success("تم")

    # اللجنة
    with tabs[2]:
        if all_refs:
            sel_l = st.selectbox("اختر الصفقة:", all_refs, key="l_sel")
            with st.form("l_form"):
                m_n = st.text_input("اسم العضو")
                m_r = st.selectbox("الصفة", ["Président", "Membre", "Secrétaire"])
                if st.form_submit_button("إضافة عضو"):
                    conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (sel_l, m_n, m_r)); conn.commit(); conn.close(); st.success("تم الإضافة")

    # التحميل (أهم جزء)
    with tabs[3]:
        rows = get_conn().execute("SELECT * FROM markets").fetchall()
        if rows:
            target = st.selectbox("اختر الصفقة:", [r['market_ref'] for r in rows])
            m_data = next(dict(r) for r in rows if r['market_ref'] == target)
            st.divider()
            c1, c2, c3 = st.columns(3)
            # توليد المحاضر بنفس مسميات قوالبك
            docs = [("PV1", "PV1"), ("PV2", "PV2"), ("PV3", "PV3"), ("Rapport", "Rapport"), ("OS", "OS")]
            for i, (k, l) in enumerate(docs):
                col = [c1, c2, c3][i % 3]
                if col.button(f"تجهيز {l}"):
                    file_data = generate_from_template(l, m_data)
                    col.download_button(f"📥 تحميل {l}", file_data, f"{l}_{target}.docx")
