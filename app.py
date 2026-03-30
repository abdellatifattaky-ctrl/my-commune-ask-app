import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. الدوال الأصلية وتعديل قاعدة البيانات ---

def init_procurement_smart_tables():
    conn = sqlite3.connect("procurement.db")
    c = conn.cursor()
    # أضفنا حقول التواريخ الجديدة هنا
    c.execute("""CREATE TABLE IF NOT EXISTS market_master_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT, 
        market_object TEXT, 
        estimate_amount REAL, 
        date_journal_1 TEXT,
        date_journal_2 TEXT,
        date_portail TEXT,
        created_at TEXT)""")
    conn.commit()
    conn.close()

def get_market_refs():
    conn = sqlite3.connect("procurement.db")
    rows = conn.execute("SELECT DISTINCT market_ref FROM market_master_data").fetchall()
    conn.close()
    return [r[0] for r in rows]

# --- 2. منطق البرنامج والقالب الأصلي ---

menu = st.sidebar.selectbox("القائمة", ["الصفقات العمومية"])

if menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية SMART PRO+</div>', unsafe_allow_html=True)
    
    init_procurement_smart_tables()

    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 توليد المحاضر"])

    # --- التبويب الأول: إدخال البيانات مع تواريخ النشر ---
    with tabs[0]:
        st.subheader("إدخال بيانات الصفقة وتواريخ النشر")
        with st.form("market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة (N° AO)")
                m_obj = st.text_area("موضوع الصفقة")
                m_amount = st.number_input("التقدير المالي", min_value=0.0)
            
            with col2:
                st.write("**📅 تواريخ النشر الإجباري:**")
                d_j1 = st.date_input("تاريخ النشر بالجريدة 1")
                d_j2 = st.date_input("تاريخ النشر بالجريدة 2")
                d_portail = st.date_input("تاريخ النشر بالبوابة (Portail)")
                m_date_open = st.date_input("تاريخ فتح الأظرفة")

            if st.form_submit_button("حفظ الصفقة"):
                conn = sqlite3.connect("procurement.db")
                conn.execute("""INSERT INTO market_master_data 
                    (market_ref, market_object, estimate_amount, date_journal_1, date_journal_2, date_portail, created_at) 
                    VALUES (?,?,?,?,?,?,?)""",
                    (m_ref, m_obj, m_amount, str(d_j1), str(d_j2), str(d_portail), str(m_date_open)))
                conn.commit()
                conn.close()
                st.success(f"✅ تم حفظ الصفقة {m_ref} مع تواريخ النشر")

    # --- التبويب الثالث: توليد المستندات مع إدراج التواريخ ---
    with tabs[2]:
        st.subheader("إصدار الوثائق الرسمية (Docx)")
        all_refs = get_market_refs()
        
        if all_refs:
            target_ref = st.selectbox("اختر الصفقة:", all_refs, key="gen_docs")
            
            # جلب البيانات كاملة بما فيها التواريخ
            conn = sqlite3.connect("procurement.db")
            conn.row_factory = sqlite3.Row
            m = conn.execute("SELECT * FROM market_master_data WHERE market_ref = ?", (target_ref,)).fetchone()
            conn.close()

            if m:
                col1, col2, col3 = st.columns(3)
                
                # مثال لدالة إنشاء مستند PV1 يحتوي على التواريخ
                if col1.button("📄 إنشاء PV1"):
                    doc = Document()
                    # (تنسيق الرأس كما سبق...)
                    doc.add_heading(f"PROCES VERBAL N° {m['market_ref']}", level=1)
                    doc.add_paragraph(f"Objet: {m['market_object']}")
                    
                    # إدراج تواريخ النشر داخل النص
                    p = doc.add_paragraph()
                    p.add_run(f"L'avis d'appel d'offres a été publié dans:\n")
                    p.add_run(f"- Journal 1 le: {m['date_journal_1']}\n")
                    p.add_run(f"- Journal 2 le: {m['date_journal_2']}\n")
                    p.add_run(f"- Portail des Marchés Publics le: {m['date_portail']}")
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.download_button("📥 تحميل PV1", bio.getvalue(), f"PV1_{target_ref}.docx")
                
                # بقية الأزرار (PV2, PV3, Rapport...) تتبع نفس النمط
                if col1.button("📄 إنشاء PV2"): st.info("جاري التحضير...")
                if col2.button("📄 إنشاء PV3"): st.info("جاري التحضير...")
                if col2.button("📝 Rapport"): st.info("جاري التحضير...")
                if col3.button("🔔 OS"): st.info("جاري التحضير...")
                if col3.button("📩 OS Notification"): st.info("جاري التحضير...")

        else:
            st.warning("يجب إضافة صفقة أولاً.")
