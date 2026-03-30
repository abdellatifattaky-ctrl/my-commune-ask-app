import streamlit as st
import sqlite3
import io
import pandas as pd
from datetime import datetime, date, timedelta
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. إدارة قاعدة البيانات ---
def get_conn():
    conn = sqlite3.connect("procurement_final_askaouen.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_amount REAL, date_j1 TEXT, date_j2 TEXT, date_portail TEXT, 
        open_date TEXT, status TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 3. محرك القوالب الرسمية (دمج المستندات المرفوعة) ---
def add_askaouen_header(doc):
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCERCLE TALIOUINE\nCAIDAT ASKAOUEN\nCOMMUNE ASKAOUEN")
    run.bold = True
    run.font.size = Pt(11)

def add_signatures(doc):
    doc.add_paragraph("\n" + "_"*30)
    table = doc.add_table(rows=2, cols=3)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cells_hdr = table.rows[0].cells
    cells_hdr[0].text = "Le Président"
    cells_hdr[1].text = "Le Directeur"
    cells_hdr[2].text = "Le Technicien"
    cells_val = table.rows[1].cells
    cells_val[0].text = "MOHAMED ZILALI"
    cells_val[1].text = "M BAREK BAK"
    cells_val[2].text = "ABDELLATIF ATTAKY"

def generate_doc(doc_type, m, committee, competitors):
    doc = Document()
    add_askaouen_header(doc)
    
    # 1. قالب المحضر الأول (1er PV) [cite: 17, 19]
    if doc_type == "PV1":
        p = doc.add_paragraph("\nPROCES VERBAL D'APPEL D'OFFRES OUVERT N°: " + m['market_ref'])
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet: {m['market_object']} [cite: 19]")
        doc.add_paragraph(f"Estimation: {m['estimate_amount']} DHS TTC [cite: 21]")
        doc.add_paragraph("\nLa commission est composée de : [cite: 17]")
        for mem in committee:
            doc.add_paragraph(f"- {mem['member_name']} : {mem['member_role']} [cite: 18]")

    # 2. قالب المحضر الثاني (2eme PV) [cite: 39, 46]
    elif doc_type == "PV2":
        doc.add_paragraph("\n2ème SEANCE PUBLIQUE - OUVERTURE DES OFFRES FINANCIERES")
        doc.add_paragraph(f"AO N°: {m['market_ref']}")
        table = doc.add_table(rows=1, cols=2); table.style = 'Table Grid'
        table.rows[0].cells[0].text = "Concurrent"; table.rows[0].cells[1].text = "Montant (DHS)"
        for c in competitors:
            row = table.add_row().cells
            row[0].text, row[1].text = c['company_name'], f"{c['offer_amount']:,.2f}"

    # 3. قالب أمر الخدمة بالتبليغ (OS Notification) [cite: 1, 2]
    elif doc_type == "OS_NOTIF":
        doc.add_paragraph("\nORDRE DE SERVICE DE LA NOTIFICATION DE L'APPROBATION [cite: 1]")
        doc.add_paragraph(f"Marché N°: {m['market_ref']} [cite: 2]")
        doc.add_paragraph(f"Entreprise: {competitors[0]['company_name'] if competitors else '..........'}")
        doc.add_paragraph(f"Objet: {m['market_object']} [cite: 3]")

    # 4. قالب أمر الخدمة ببداية الأشغال (OS Commencement) [cite: 9, 11]
    elif doc_type == "OS_START":
        doc.add_paragraph("\nORDRE DE SERVICE POUR COMMENCEMENT DES TRAVAUX [cite: 9]")
        doc.add_paragraph(f"Marché N°: {m['market_ref']} [cite: 11]")
        doc.add_paragraph("L'entrepreneur est invité à commencer les travaux à compter du: .......... [cite: 12]")

    # 5. قالب سند الطلب (PV BC) [cite: 75, 76]
    elif doc_type == "PV_BC":
        doc.add_paragraph("\n4ème PROCES VERBAL - PROCEDURE BON DE COMMANDE [cite: 75, 76]")
        doc.add_paragraph(f"Objet: {m['market_object']} [cite: 77]")
        doc.add_paragraph(f"Montant attribué: {m['estimate_amount']} DHS TTC [cite: 82]")

    add_signatures(doc) # [cite: 84]
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- 4. واجهة المستخدم النهائية ---
init_db()
st.sidebar.title("SMART PRO+ ASKAOUEN")
mode = st.sidebar.selectbox("القائمة", ["🏠 الرئيسة", "📑 الصفقات", "📊 التقارير"])

if mode == "📑 الصفقات":
    tabs = st.tabs(["➕ تسجيل", "👥 المتنافسون", "📋 اللجنة", "📄 إصدار الوثائق"])
    
    with tabs[0]: # تسجيل
        with st.form("add_m"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("مرجع الصفقة")
            obj = c1.text_area("الموضوع")
            amt = c2.number_input("التقدير المالي", min_value=0.0)
            d_o = c2.date_input("تاريخ فتح الأظرفة")
            type_m = c1.selectbox("النوع", ["AO Ouvert", "AO National", "Bon de commande"])
            if st.form_submit_button("حفظ"):
                conn = get_conn(); conn.execute("INSERT INTO markets (market_ref, market_object, estimate_amount, open_date, procedure_type) VALUES (?,?,?,?,?)", (ref, obj, amt, str(d_o), type_m)); conn.commit(); conn.close(); st.success("تم الحفظ")

    with tabs[3]: # إصدار الوثائق (الدمج النهائي)
        conn = get_conn()
        markets = conn.execute("SELECT * FROM markets").fetchall()
        if markets:
            sel = st.selectbox("اختر الصفقة:", [r['market_ref'] for r in markets])
            m_data = next(dict(r) for r in markets if r['market_ref'] == sel)
            comm = conn.execute("SELECT * FROM commission WHERE market_ref=?", (sel,)).fetchall()
            comps = conn.execute("SELECT * FROM competitors WHERE market_ref=?", (sel,)).fetchall()
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            # توزيع الأزرار حسب القوالب الستة المرفوعة
            docs_map = [("PV1", "المحضر 1", c1), ("PV2", "المحضر 2", c1), ("OS_NOTIF", "تبليغ المصادقة", c2), 
                        ("OS_START", "بداية الأشغال", c2), ("PV_BC", "محضر سند الطلب", c3), ("Rapport", "التقرير التقني", c3)]
            
            for key, label, col in docs_map:
                if col.button(f"إنشاء {label}"):
                    file = generate_doc(key, m_data, comm, comps)
                    col.download_button(f"📥 تحميل {label}", file, f"{label}_{sel}.docx")
        conn.close()

elif mode == "🏠 الرئيسة":
    st.title("جماعة أسكاون - نظام تدبير الصفقات")
    st.info("مرحباً بك في النظام الموحد. استخدم القائمة الجانبية لإدارة البيانات وتوليد المحاضر.")
