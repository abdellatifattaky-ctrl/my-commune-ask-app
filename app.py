import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ ASKAOUEN", layout="wide")

# --- 2. إدارة قاعدة البيانات (V6 - النسخة الشاملة) ---
def get_conn():
    conn = sqlite3.connect("askaouen_final_v6.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # جدول الصفقات مع التقدير لكل حصة
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_total REAL, estimate_per_lot TEXT, 
        date_j1 TEXT, date_j2 TEXT, date_portail TEXT, created_at TEXT)""")
    
    # جدول المتنافسين مع العرض المالي
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    
    # جدول أعضاء اللجنة
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 3. دالة توليد الوثائق (نظام الأسطر Lignes والقائمة التسعة) ---
def generate_askaouen_final_doc(doc_key, m):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.left_margin = Cm(1.5), Cm(2)
    
    # الترويسة الرسمية
    header = doc.add_paragraph()
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE ASKAOUEN").bold = True

    # مسميات الوثائق حسب ملفك (program les marche docx.docx)
    titles = {
        "pv_admin": "Pv de dossier administrative et technique",
        "pv_tech": "Pv de dossier administrative et technique et offer technique si existance",
        "os_comm": "Os-commencement",
        "os_notif": "Os-notification",
        "pv_3eme": "Pv de 3 eme seance pour le complement",
        "rapport": "Rapport de sous commisession pour etudier offer tech",
        "pv_fin": "Pv de dossier offer financier"
    }
    
    doc.add_paragraph("\n")
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{titles.get(doc_key, '').upper()}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True; run_t.font.size = Pt(14); run_t.underline = True

    doc.add_paragraph(f"\nOBJET : {m['market_object']}").bold = True
    
    # عرض التقدير المالي (الإجمالي وبالحصص)
    doc.add_paragraph(f"ESTIMATION TOTALE : {m['estimate_total']} DHS TTC")
    if m['estimate_per_lot']:
        doc.add_paragraph(f"ESTIMATION PAR LOT : {m['estimate_per_lot']}")

    # --- عرض المتنافسين على شكل أسطر (Lines) بدلاً من الجدول ---
    conn = get_conn()
    comps = conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    
    if comps:
        doc.add_paragraph("\nLISTE DES CONCURRENTS ET OFFRES FINANCIERES :").bold = True
        for c in comps:
            # عرض سطري: اسم الشركة - المبلغ - الحالة
            line = doc.add_paragraph(style='List Bullet')
            line.add_run(f"Concurrent : ").bold = True
            line.add_run(f"{c['company_name']}")
            line.add_run(f"  |  Montant Proposé : ").bold = True
            line.add_run(f"{c['offer_amount']} DHS")
            line.add_run(f"  |  Décision : ").bold = True
            line.add_run(f"{c['status']}")

    # التوقيعات
    members = conn.execute("SELECT * FROM commission WHERE market_ref = ?", (m['market_ref'],)).fetchall()
    conn.close()
    if members:
        doc.add_paragraph("\n\nMEMBRES DE LA COMMISSION :").bold = True
        for mem in members:
            doc.add_paragraph(f"- {mem['member_name']} ({mem['member_role']}) : ...........................")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- 4. واجهة البرنامج ---
init_db()
st.title("📂 نظام أسكاون المتطور - SMART PRO+")

tabs = st.tabs(["📝 إدخال الصفقة", "🏢 المتنافسون واللجنة", "📥 تحميل المحاضر التسعة"])

with tabs[0]:
    with st.form("m_form"):
        c1, c2 = st.columns(2)
        ref = c1.text_input("مرجع الصفقة (N° AO)")
        # إضافة الخيار الجديد الذي طلبته
        p_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert", "Appel d'offres ouvert national", "Appel d'offres simplifié"])
        obj = c1.text_area("موضوع الصفقة")
        amt_total = c2.number_input("التقدير المالي الإجمالي", min_value=0.0)
        amt_lots = c2.text_input("التقدير لكل حصة (مثال: Lot1: 100k, Lot2: 50k)")
        j1, j2, port = c2.date_input("جريدة 1"), c2.date_input("جريدة 2"), c2.date_input("تاريخ البوابة")
        if st.form_submit_button("حفظ"):
            conn = get_conn()
            conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_total, estimate_per_lot, date_j1, date_j2, date_portail, created_at) VALUES (?,?,?,?,?,?,?,?,?)", (ref, obj, p_type, amt_total, amt_lots, str(j1), str(j2), str(port), str(date.today())))
            conn.commit(); conn.close(); st.success("تم الحفظ!")

with tabs[1]:
    all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
    if all_m:
        sel = st.selectbox("اختر الصفقة:", all_m)
        col_a, col_b = st.columns(2)
        with col_a.form("comp"):
            st.write("إضافة متنافس وعرضه المالي")
            n, o = st.text_input("اسم الشركة"), st.number_input("مبلغ العرض (Offre Financière)", min_value=0.0)
            s = st.selectbox("القرار", ["Admis", "Écarté"])
            if st.form_submit_button("إضافة"):
                conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (sel, n, o, s)); conn.commit(); conn.close(); st.success("تم")
        with col_b.form("comm"):
            st.write("أعضاء اللجنة")
            m_n, m_r = st.text_input("الاسم الكامل"), st.text_input("الصفة")
            if st.form_submit_button("إضافة عضو"):
                conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (sel, m_n, m_r)); conn.commit(); conn.close(); st.success("تم")

with tabs[2]:
    rows = get_conn().execute("SELECT * FROM markets").fetchall()
    if rows:
        target = st.selectbox("اختر الصفقة للتحميل:", [r['market_ref'] for r in rows])
        m_data = next(dict(r) for r in rows if r['market_ref'] == target)
        st.write("### 📄 الوثائق الرسمية التسعة (حسب القائمة):")
        
        doc_list = [
            ("pv_admin", "1. Pv administratif et technique"),
            ("pv_tech", "2. Pv administratif/technique/offre tech"),
            ("os_comm", "3. Os-commencement"),
            ("os_notif", "4. Os-notification"),
            ("pv_3eme", "5. Pv 3ème séance (Complément)"),
            ("rapport", "6. Rapport sous-commission tech"),
            ("pv_fin", "7. Pv dossier offre financier")
        ]
        
        c1, c2 = st.columns(2)
        for i, (k, v) in enumerate(doc_list):
            col = c1 if i % 2 == 0 else c2
            if col.button(f"🛠️ تجهيز {v}"):
                data = generate_askaouen_final_doc(k, m_data)
                col.download_button(f"📥 تحميل {v}", data, f"{k}_{target}.docx")
