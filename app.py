import streamlit as st
import sqlite3
import io
import pandas as pd
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. إعدادات وقاعدة البيانات ---
def get_conn():
    conn = sqlite3.connect("askaouen_final_2023.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_ref TEXT UNIQUE, market_object TEXT, procedure_type TEXT,
        estimate_total REAL, date_j1 TEXT, date_j2 TEXT, date_portail TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        company_name TEXT, offer_amount REAL, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS commission (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market_ref TEXT,
        member_name TEXT, member_role TEXT)""")
    conn.commit()
    conn.close()

# --- 2. معادلة الثمن المرجعي (مرسوم 2023) ---
def calculate_ref_price(admin_est, offers):
    if not offers: return admin_est
    avg_offers = sum(offers) / len(offers)
    return (admin_est + avg_offers) / 2

# --- 3. محرك توليد الوثائق (القائمة التسعة + التنسيق السطري) ---
def generate_askaouen_docx(doc_key, m, comps, members):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.left_margin = Cm(1.5), Cm(2)
    
    # الترويسة الرسمية
    header = doc.add_paragraph()
    header.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCERCLE DE TALIOUINE\nCOMMUNE ASKAOUEN").bold = True

    # مسميات المحاضر (قائمة ملفك الأصلية)
    titles = {
        "pv_admin": "Pv de dossier administrative et technique",
        "pv_tech": "Pv de dossier administrative et technique et offer technique si existance",
        "pv_3eme": "Pv de 3 eme seance pour le complement",
        "pv_fin": "Pv de dossier offer financier",
        "rapport": "Rapport de sous commisession pour etudier offer tech",
        "os_comm": "Os-commencement",
        "os_notif": "Os-notification"
    }
    
    doc.add_paragraph("\n")
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = t.add_run(f"{titles.get(doc_key, '').upper()}\n{m['procedure_type'].upper()} N° : {m['market_ref']}")
    run_t.bold = True; run_t.font.size = Pt(14); run_t.underline = True

    # الإشارة لمرسوم 2023
    legal = doc.add_paragraph()
    legal.add_run("Vu le décret n° 2-22-431 du 15 chaâbane 1444 (8 mars 2023) relatif aux marchés publics.").italic = True

    doc.add_paragraph(f"\nOBJET : {m['market_object']}").bold = True
    doc.add_paragraph(f"ESTIMATION DE L'ADMINISTRATION : {m['estimate_total']:,.2f} DHS TTC")

    # تطبيق معادلة الثمن المرجعي في المحضر المالي
    if doc_key == "pv_fin":
        prices = [c['offer_amount'] for c in comps if c['offer_amount'] > 0]
        final_ref = calculate_ref_price(m['estimate_total'], prices)
        doc.add_paragraph(f"PRIX DE REFERENCE CALCULE (Moyenne MO/Concurrents) : {final_ref:,.2f} DHS TTC").bold = True

    # عرض المتنافسين بشكل سطري (Lignes)
    if comps:
        doc.add_paragraph("\nEXAMEN DES OFFRES DES CONCURRENTS :").bold = True
        for c in comps:
            p = doc.add_paragraph(style='List Bullet')
            if doc_key == "pv_fin":
                p.add_run(f"Société : {c['company_name']} | Offre Financière : ").bold = True
                p.add_run(f"{c['offer_amount']:,.2f} DHS TTC")
            else:
                p.add_run(f"Société : {c['company_name']} | Décision : {c['status']}")

    # التوقيعات (اللجنة)
    if members:
        doc.add_paragraph("\n\nMEMBRES DE LA COMMISSION :").bold = True
        for mem in members:
            doc.add_paragraph(f"- {mem['member_name']} ({mem['member_role']}) : ...........................")

    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}")
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

# --- 4. واجهة المستخدم Streamlit ---
init_db()
st.title("💼 SMART PRO+ | جماعة أسكاون (مرسوم 2023)")

tabs = st.tabs(["1️⃣ تسجيل الصفقة", "2️⃣ المتنافسون واللجنة", "3️⃣ المحاضر والمعادلة"])

with tabs[0]:
    with st.form("m_form"):
        c1, c2 = st.columns(2)
        ref = c1.text_input("مرجع الصفقة (N° AO)")
        p_type = c1.selectbox("نوع المسطرة", ["Appel d'offres ouvert", "Appel d'offres ouvert national", "Appel d'offres simplifié"])
        obj = c1.text_area("الموضوع")
        amt = c2.number_input("تقدير الإدارة (Estimation MO)", min_value=0.0)
        j1, j2, port = c2.date_input("جريدة 1"), c2.date_input("جريدة 2"), c2.date_input("البوابة")
        if st.form_submit_button("حفظ الصفقة"):
            conn = get_conn()
            conn.execute("INSERT INTO markets (market_ref, market_object, procedure_type, estimate_total, date_j1, date_j2, date_portail) VALUES (?,?,?,?,?,?,?)", (ref, obj, p_type, amt, str(j1), str(j2), str(port)))
            conn.commit(); conn.close(); st.success("✅ تم الحفظ")

with tabs[1]:
    all_m = [r['market_ref'] for r in get_conn().execute("SELECT market_ref FROM markets").fetchall()]
    if all_m:
        sel = st.selectbox("اختر الصفقة لتعبئة البيانات:", all_m)
        col_a, col_b = st.columns(2)
        with col_a.form("comp_form"):
            st.write("🏢 إضافة شركة متنافسة")
            c_name, c_price = st.text_input("اسم الشركة"), st.number_input("المبلغ المعروض", min_value=0.0)
            c_status = st.selectbox("الحالة", ["Admis", "Écarté"])
            if st.form_submit_button("إضافة"):
                conn = get_conn(); conn.execute("INSERT INTO competitors (market_ref, company_name, offer_amount, status) VALUES (?,?,?,?)", (sel, c_name, c_price, c_status)); conn.commit(); conn.close(); st.success("تم")
        with col_b.form("comm_form"):
            st.write("👥 أعضاء اللجنة")
            m_name, m_role = st.text_input("الاسم الكامل"), st.text_input("الصفة")
            if st.form_submit_button("إضافة عضو"):
                conn = get_conn(); conn.execute("INSERT INTO commission (market_ref, member_name, member_role) VALUES (?,?,?)", (sel, m_name, m_role)); conn.commit(); conn.close(); st.success("تم")

with tabs[2]:
    rows = get_conn().execute("SELECT * FROM markets").fetchall()
    if rows:
        target = st.selectbox("اختر الصفقة لإصدار الوثائق:", [r['market_ref'] for r in rows])
        conn = get_conn()
        m_data = dict(conn.execute("SELECT * FROM markets WHERE market_ref = ?", (target,)).fetchone())
        comps = [dict(r) for r in conn.execute("SELECT * FROM competitors WHERE market_ref = ?", (target,)).fetchall()]
        members = [dict(r) for r in conn.execute("SELECT * FROM commission WHERE market_ref = ?", (target,)).fetchall()]
        conn.close()

        # عرض نتيجة المعادلة الحسابية للمعاينة
        if comps:
            final_p = calculate_ref_price(m_data['estimate_total'], [c['offer_amount'] for c in comps])
            st.info(f"⚖️ الثمن المرجعي المحسوب (المعادلة): {final_p:,.2f} DHS")

        st.write("### 📄 تحميل القائمة الرسمية:")
        doc_list = [
            ("pv_admin", "Pv dossier administratif"), ("pv_tech", "Pv dossier technique"),
            ("pv_3eme", "Pv 3ème séance"), ("rapport", "Rapport sous-commission"),
            ("pv_fin", "Pv dossier offre financier (مع العروض السطرية)"),
            ("os_comm", "Os-commencement"), ("os_notif", "Os-notification")
        ]
        
        c1, c2 = st.columns(2)
        for i, (k, v) in enumerate(doc_list):
            col = c1 if i % 2 == 0 else c2
            if col.button(f"🛠️ تجهيز {v}"):
                file_bytes = generate_askaouen_docx(k, m_data, comps, members)
                col.download_button(f"📥 تحميل {v}", file_bytes, f"{k}_{target}.docx")
