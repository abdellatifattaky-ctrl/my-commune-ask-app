import streamlit as st
import sqlite3
import io
import pandas as pd
from datetime import datetime, date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- قاعدة البيانات ---
def get_conn():
    conn = sqlite3.connect("procurement_final_v10.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_amount REAL, open_date TEXT, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    conn.commit(); conn.close()

# --- محرك دمج النصوص الحرفية من القوالب المرفوعة ---
def generate_official_doc(doc_type, m, comps):
    doc = Document()
    
    # الإعدادات العامة للهوامش والخط
    section = doc.sections[0]
    section.left_margin = Cm(2)
    
    # 1. الترويسة الرسمية (ثابتة في كل ملفاتك)
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCERCLE TALIOUINE\nCAIDAT ASKAOUEN\nCOMMUNE ASKAOUEN").bold = True

    # --- دمج قالب المحضر الأول (حرفياً من 1er_PV.docx) ---
    if doc_type == "PV1":
        title = doc.add_paragraph("\nPROCES VERBAL D'APPEL D'OFFRES OUVERT\nSUR OFFRE DE PRIX N: " + m['market_ref'])
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].bold = True
        
        doc.add_paragraph(f"Le {m['open_date']} à 10h, une commission d'appel d'offres... est composée comme suit :")
        doc.add_paragraph("ZILALI MOHAMED : PRESIDENT DE LA C/T ASKAOUEN --- PRESIDENT")
        doc.add_paragraph("BAK MOBAREK : DIRECTEUR DES SERVICES --- MEMBRE")
        doc.add_paragraph("ABDELLATIF ATTAKAY : TECHNICIEN A LA COMMUNE --- MEMBRE")
        
        doc.add_paragraph(f"\nObjet: {m['market_object']}")
        doc.add_paragraph(f"Estimation: {m['estimate_amount']} DHS TTC")

    # --- دمج قالب المحضر الثاني (حرفياً من 2eme_pv.docx) ---
    elif doc_type == "PV2":
        doc.add_paragraph("\nPROCES VERBAL D'APPEL D'OFFRES OUVERT\n2eme Séance Publique").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Conformément à la décision... la commission d'appel d'offres N: {m['market_ref']}")
        doc.add_paragraph("\nOuverture des enveloppes des concurrents admissibles portant la mention 'offres financières' :")
        
        table = doc.add_table(rows=1, cols=2); table.style = 'Table Grid'
        table.rows[0].cells[0].text = "Concurrent"; table.rows[0].cells[1].text = "Montant"
        for c in comps:
            row = table.add_row().cells
            row[0].text, row[1].text = c['company_name'], f"{c['offer_amount']}"

    # --- دمج قالب التبليغ (حرفياً من os_noitificatin.docx) ---
    elif doc_type == "OS_NOTIF":
        doc.add_paragraph("\nORDRE DE SERVICE DE LA NOTIFICATION\nDE L’APPROBATION DU MARCHE N: " + m['market_ref']).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Le maître d’ouvrage représenté par Mr ZILALI MOHAMED en qualités du président...")
        doc.add_paragraph(f"Informe l'entreprise que le marché ayant pour objet: {m['market_object']} est approuvé.")

    # --- دمج قالب بداية الأشغال (حرفياً من os_commencement.docx) ---
    elif doc_type == "OS_START":
        doc.add_paragraph("\nORDRE DE SERVICE A L’ENTREPRENEUR POUR\nCOMMENCEMENT DES TRAVAUX").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Marché N°: {m['market_ref']}")
        doc.add_paragraph(f"Objet: {m['market_object']}")
        doc.add_paragraph("\nPar conséquent, l'intéressé est invité à commencer les travaux objet du présent marché à compter du: ..........")

    # --- التوقيعات (حرفياً كما في الصور والملفات) ---
    doc.add_paragraph("\n\nFait à Askaouen, le " + str(date.today()))
    sig = doc.add_table(rows=2, cols=3)
    sig.rows[0].cells[0].text = "Le Président"
    sig.rows[0].cells[1].text = "Le Directeur"
    sig.rows[0].cells[2].text = "Le Technicien"
    sig.rows[1].cells[0].text = "MOHAMED ZILALI"
    sig.rows[1].cells[1].text = "M BAREK BAK"
    sig.rows[1].cells[2].text = "ABDELLATIF ATTAKY"

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- الواجهة ---
init_db()
st.sidebar.title("SMART PRO+ ASKAOUEN")
menu = st.sidebar.selectbox("القائمة", ["إدارة الصفقات", "لوحة التحكم"])

if menu == "إدارة الصفقات":
    t1, t2, t3 = st.tabs(["تسجيل الصفقة", "المتنافسون", "تحميل القوالب الرسمية"])
    
    with t1:
        with st.form("m_f"):
            ref = st.text_input("مرجع الصفقة (N° AO)")
            obj = st.text_area("الموضوع")
            amt = st.number_input("التقدير المالي", min_value=0.0)
            d_o = st.date_input("تاريخ فتح الأظرفة")
            if st.form_submit_button("حفظ"):
                conn = get_conn(); conn.execute("INSERT INTO markets (market_ref, market_object, estimate_amount, open_date) VALUES (?,?,?,?)", (ref, obj, amt, str(d_o))); conn.commit(); conn.close(); st.success("تم الحفظ")

    with t2:
        all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
        if all_m:
            s_m = st.selectbox("اختر الصفقة:", all_m)
            with st.form("c_f"):
                c_n = st.text_input("اسم الشركة")
                c_o = st.number_input("المبلغ", min_value=0.0)
                if st.form_submit_button("إضافة"):
                    conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount) VALUES (?,?,?)", (s_m, c_n, c_o)); conn.commit(); conn.close(); st.success("تمت الإضافة")

    with t3:
        markets = get_conn().execute("SELECT * FROM markets").fetchall()
        if markets:
            sel_m = st.selectbox("الصفقة المراد تحميل ملفاتها:", [r['market_ref'] for r in markets])
            m_data = next(dict(r) for r in markets if r['market_ref'] == sel_m)
            comps = get_conn().execute("SELECT * FROM competitors WHERE market_ref=?", (sel_m,)).fetchall()
            
            st.info("اختر القالب الرسمي لتحميله بنصوصه الحرفية:")
            c1, c2 = st.columns(2)
            
            # الربط المباشر مع النصوص المستخرجة من ملفاتك
            docs_info = [
                ("PV1", "المحضر الأول (1er PV)", c1),
                ("PV2", "المحضر الثاني (2eme PV)", c1),
                ("OS_NOTIF", "تبليغ المصادقة (OS Notif)", c2),
                ("OS_START", "بداية الأشغال (OS Start)", c2)
            ]
            
            for key, label, col in docs_info:
                if col.button(f"تجهيز {label}"):
                    file_data = generate_official_doc(key, m_data, comps)
                    col.download_button(f"📥 تحميل {label}", file_data, f"{label}_{sel_m}.docx")
