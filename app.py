import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ الصفقات", layout="wide")

# --- 2. قاعدة البيانات (إضافة جدول الحصص Lots) ---
def get_conn():
    conn = sqlite3.connect("procurement.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_procurement_smart_tables():
    conn = get_conn()
    c = conn.cursor()
    # جدول الصفقات
    c.execute("""CREATE TABLE IF NOT EXISTS market_master_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT, market_object TEXT, 
        procedure_type TEXT, estimate_amount REAL, date_journal_1 TEXT, 
        date_journal_2 TEXT, date_portail TEXT, created_at TEXT)""")
    
    # جدول الحصص (Lots)
    c.execute("""CREATE TABLE IF NOT EXISTS market_lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT, lot_number INTEGER, 
        lot_title TEXT, lot_estimate REAL)""")
    
    # جدول المتنافسين (مرتبط بالصفقة وبالحصة)
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT, lot_id INTEGER, 
        company_name TEXT, offer_amount REAL, status TEXT)""")
    conn.commit()
    conn.close()

# --- 3. دالة توليد الوورد المحترفة ---
def generate_docx(title, m_data):
    doc = Document()
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("ROYAUME DU MAROC\nCOMMUNE ASKAOUEN").bold = True
    
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.add_run(f"{title}\n{m_data['procedure_type'].upper()} N° : {m_data['market_ref']}").bold = True
    
    doc.add_paragraph(f"Objet: {m_data['market_object']}")
    
    # جلب الحصص والمتنافسين
    conn = get_conn()
    lots = conn.execute("SELECT * FROM market_lots WHERE market_ref = ?", (m_data['market_ref'],)).fetchall()
    
    if lots:
        for lot in lots:
            doc.add_paragraph(f"\nLOT N° {lot['lot_number']}: {lot['lot_title']}").bold = True
            comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ? AND lot_id = ?", (m_data['market_ref'], lot['id'])).fetchall()
            if comps:
                table = doc.add_table(rows=1, cols=3)
                table.style = 'Table Grid'
                hdr = table.rows[0].cells
                hdr[0].text, hdr[1].text, hdr[2].text = "Concurrent", "Offre", "Décision"
                for c in comps:
                    row = table.add_row().cells
                    row[0].text, row[1].text, row[2].text = c['company_name'], f"{c['offer_amount']} DHS", c['status']
    conn.close()

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم (القالب الأصلي) ---
init_procurement_smart_tables()
menu = st.sidebar.selectbox("القائمة", ["الصفقات العمومية"])

if menu == "الصفقات العمومية":
    st.markdown('<h2 style="text-align:center;">تدبير الصفقات SMART PRO+</h2>', unsafe_allow_html=True)
    tabs = st.tabs(["➕ تسجيل صفقة", "📦 الحصص (Lots)", "👥 المتنافسون", "📄 تحميل المحاضر"])

    with tabs[0]: # تسجيل صفقة
        with st.form("f_market"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("مرجع الصفقة")
            p_type = c1.selectbox("النوع", ["Appel d'offres ouvert", "Appel d'offres simplifié"])
            obj = c1.text_area("الموضوع")
            amt = c2.number_input("التقدير الإجمالي", min_value=0.0)
            j1, j2, port = c2.date_input("ج1"), c2.date_input("ج2"), c2.date_input("البوابة")
            if st.form_submit_button("حفظ الصفقة"):
                conn = get_conn(); conn.execute("INSERT INTO market_master_data (market_ref, market_object, procedure_type, estimate_amount, date_journal_1, date_journal_2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port), str(date.today()))); conn.commit(); conn.close()
                st.success("تم الحفظ!"); st.rerun()

    with tabs[1]: # الحصص
        st.subheader("إضافة حصص الصفقة")
        all_refs = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM market_master_data").fetchall()]
        if all_refs:
            sel_ref = st.selectbox("اختر الصفقة:", all_refs, key="lot_sel")
            with st.form("f_lot"):
                l_num = st.number_input("رقم الحصة", min_value=1)
                l_tit = st.text_input("عنوان الحصة")
                l_est = st.number_input("تقدير الحصة", min_value=0.0)
                if st.form_submit_button("إضافة الحصة"):
                    conn = get_conn(); conn.execute("INSERT INTO market_lots (market_ref, lot_number, lot_title, lot_estimate) VALUES (?,?,?,?)", (sel_ref, l_num, l_tit, l_est)); conn.commit(); conn.close()
                    st.success(f"تمت إضافة الحصة {l_num}")
        else: st.info("سجل صفقة أولاً")

    with tabs[2]: # المتنافسون
        st.subheader("إضافة المتنافسين حسب الحصة")
        if all_refs:
            ref_c = st.selectbox("اختر الصفقة:", all_refs, key="c_ref_sel")
            lots = get_conn().execute("SELECT * FROM market_lots WHERE market_ref = ?", (ref_c,)).fetchall()
            if lots:
                sel_lot = st.selectbox("اختر الحصة:", [f"Lot {l['lot_number']}: {l['lot_title']}" for l in lots])
                lot_id = [l['id'] for l in lots if f"Lot {l['lot_number']}: {l['lot_title']}" == sel_lot][0]
                with st.form("f_comp"):
                    name = st.text_input("اسم الشركة")
                    offer = st.number_input("المبلغ", min_value=0.0)
                    stat = st.selectbox("القرار", ["Admis", "Écarté"])
                    if st.form_submit_button("إضافة"):
                        conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, lot_id, company_name, offer_amount, status) VALUES (?,?,?,?,?)", (ref_c, lot_id, name, offer, stat)); conn.commit(); conn.close()
                        st.success("تمت الإضافة")
            else: st.warning("أضف حصصاً لهذه الصفقة أولاً")

    with tabs[3]: # التحميل
        markets = get_conn().execute("SELECT * FROM market_master_data").fetchall()
        if markets:
            target = st.selectbox("اختر الصفقة للتحميل:", [m['market_ref'] for m in markets], key="final_sel")
            m_data = next(dict(m) for m in markets if m['market_ref'] == target)
            c1, c2, c3 = st.columns(3)
            for i, (k, l) in enumerate([("PV1", "PV1"), ("PV2", "PV2"), ("PV3", "PV3"), ("Rapport", "RAPPORT"), ("OS", "OS")]):
                col = [c1, c2, c3][i % 3]
                if col.button(f"تجهيز {l}"):
                    col.download_button(f"📥 تحميل {l}", generate_docx(l, m_data), f"{l}_{target}.docx")
