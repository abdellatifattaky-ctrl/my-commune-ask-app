import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ الصفقات", layout="wide")

# --- 2. دوال قاعدة البيانات ---
def get_conn():
    conn = sqlite3.connect("procurement.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # تحديث الجدول ليشمل نوع المسطرة (Type de Procédure)
    c.execute("""
        CREATE TABLE IF NOT EXISTS market_master_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_ref TEXT,
            market_object TEXT,
            procedure_type TEXT,
            estimate_amount REAL,
            date_journal_1 TEXT,
            date_journal_2 TEXT,
            date_portail TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- 3. دالة توليد المستندات الذكية ---
def generate_smart_docx(title, m):
    doc = Document()
    # (تنسيق الرأس كما في قوالبك السابقة)
    section = doc.sections[0]
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("ROYAUME DU MAROC\nCOMMUNE ASKAOUEN").bold = True

    # صياغة العنوان بناءً على نوع المسطرة
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    proc_name = m['procedure_type'] # Appel d'offres ouvert / Simplifié...
    run_t = t.add_run(f"{title}\n{proc_name} N° : {m['market_ref']}")
    run_t.bold = True
    run_t.font.size = Pt(14)

    # إضافة تفاصيل النشر واللجنة (تتغير آلياً)
    doc.add_paragraph(f"Objet: {m['market_object']}")
    doc.add_paragraph(f"Publié le: {m['date_portail']} (Portail) / {m['date_journal_1']} (J1)")
    
    # مكان مخصص لتوقيع اللجنة
    doc.add_paragraph("\n\nMEMBRES DE LA COMMISSION :")
    doc.add_paragraph("1. ................................ (Président)")
    doc.add_paragraph("2. ................................ (Membre)")
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم (نفس قوالبك الأصلية) ---
init_db()
menu = st.sidebar.selectbox("القائمة", ["الصفقات العمومية"])

if menu == "الصفقات العمومية":
    st.markdown('<h2 style="text-align: center;">تدبير الصفقات SMART PRO+</h2>', unsafe_allow_html=True)

    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 تحميل المحاضر"])

    with tabs[0]:
        with st.form("market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة")
                # إضافة اختيار نوع المسطرة (الطلب الذي قدمته)
                m_type = st.selectbox("نوع المسطرة (Procédure)", 
                                    ["Appel d'offres ouvert", 
                                     "Appel d'offres ouvert national", 
                                     "Appel d'offres simplifié",
                                     "Consultation architecturale"])
                m_obj = st.text_area("الموضوع")
            with col2:
                m_amt = st.number_input("التقدير المالي", min_value=0.0)
                d_j1 = st.date_input("جريدة 1")
                d_j2 = st.date_input("جريدة 2")
                d_p = st.date_input("البوابة (Portail)")

            if st.form_submit_button("حفظ البيانات"):
                conn = get_conn()
                conn.execute("""INSERT INTO market_master_data 
                    (market_ref, market_object, procedure_type, estimate_amount, date_journal_1, date_journal_2, date_portail, created_at) 
                    VALUES (?,?,?,?,?,?,?,?)""", (m_ref, m_obj, m_type, m_amt, str(d_j1), str(d_j2), str(d_p), str(date.today())))
                conn.commit()
                conn.close()
                st.success("تم الحفظ بنجاح!")

    with tabs[2]:
        conn = get_conn()
        markets = conn.execute("SELECT * FROM market_master_data").fetchall()
        conn.close()
        
        if markets:
            selected_ref = st.selectbox("اختر الصفقة:", [x['market_ref'] for x in markets])
            m_data = [x for x in markets if x['market_ref'] == selected_ref][0]
            
            st.info(f"نوع المسطرة: {m_data['procedure_type']}")
            
            c1, c2, c3 = st.columns(3)
            # توليد الملفات بناءً على البيانات المخزنة
            if c1.button("📄 PV1"):
                st.download_button("تحميل PV1", generate_smart_docx("PV1", m_data), f"PV1_{selected_ref}.docx")
            if c1.button("📄 PV2"):
                st.download_button("تحميل PV2", generate_smart_docx("PV2", m_data), f"PV2_{selected_ref}.docx")
            if c2.button("📄 PV3"):
                st.download_button("تحميل PV3", generate_smart_docx("PV3", m_data), f"PV3_{selected_ref}.docx")
            if c2.button("📝 Rapport"):
                st.download_button("تحميل Rapport", generate_smart_docx("Rapport", m_data), f"Rapport_{selected_ref}.docx")
            if c3.button("🔔 OS"):
                st.download_button("تحميل OS", generate_smart_docx("OS", m_data), f"OS_{selected_ref}.docx")
            if c3.button("📩 OS Notification"):
                st.download_button("تحميل Notification", generate_smart_docx("Notification", m_data), f"Notif_{selected_ref}.docx")
        else:
            st.warning("لا توجد صفقات.")
