import streamlit as st
import sqlite3
import io
from datetime import date
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from num2words import num2words

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SMART PRO+ الصفقات", layout="wide")

# --- دوال قاعدة البيانات ---
def get_conn():
    # ملاحظة: sqlite3 ستنشئ الملف تلقائياً في مستودع GitHub الخاص بك عند التشغيل
    conn = sqlite3.connect("procurement_db.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS markets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_ref TEXT,
            market_object TEXT,
            estimate_amount REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def format_amount_fr(value):
    try:
        val = float(value)
        words = num2words(val, lang="fr").upper()
        return f"{words} DIRHAMS"
    except:
        return "________________"

# --- دالة إنشاء مستند الوورد ---
def create_pv1(data):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2)
    
    # الهيدر
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("ROYAUME DU MAROC\nCOMMUNE ASKAOUEN").bold = True
    
    doc.add_paragraph("\n")
    
    # العنوان
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"PROCES VERBAL N°: {data['market_ref']}")
    run.bold = True
    run.font.size = Pt(14)
    
    # التفاصيل
    doc.add_paragraph(f"Objet: {data['market_object']}")
    doc.add_paragraph(f"Montant estimatif: {data['estimate_amount']} DHS")
    doc.add_paragraph(f"Arrêté à la somme de: {format_amount_fr(data['estimate_amount'])}")
    
    doc.add_paragraph("\n\nFait à Askaouen, le " + str(date.today()))
    
    target = io.BytesIO()
    doc.save(target)
    return target.getvalue()

# --- واجهة المستخدم ---
init_db() # تشغيل التأسيس

st.sidebar.title("🛠️ لوحة التحكم")
menu = st.sidebar.selectbox("اختر القسم", ["الرئيسية", "الصفقات العمومية"])

if menu == "الرئيسية":
    st.title("مرحباً بك في تطبيق تدبير الصفقات 🚀")
    st.write("هذا التطبيق مخصص لتبسيط استخراج المحاضر القانونية.")

elif menu == "الصفقات العمومية":
    st.header("🏢 إدارة الصفقات العمومية")
    
    t1, t2 = st.tabs(["➕ إضافة صفقة", "📄 استخراج PV1"])
    
    with t1:
        with st.form("add_market"):
            ref = st.text_input("رقم الصفقة")
            obj = st.text_area("موضوع الصفقة")
            amt = st.number_input("التقدير المالي", min_value=0.0)
            if st.form_submit_button("حفظ"):
                if ref and obj:
                    conn = get_conn()
                    conn.execute("INSERT INTO markets (market_ref, market_object, estimate_amount, created_at) VALUES (?,?,?,?)",
                                 (ref, obj, amt, str(date.today())))
                    conn.commit()
                    conn.close()
                    st.success("تم الحفظ بنجاح في قاعدة البيانات!")
                else:
                    st.error("يرجى ملء الحقول المطلوبة")

    with t2:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM markets").fetchall()
        conn.close()
        
        if rows:
            market_names = {r['market_ref']: r for r in rows}
            choice = st.selectbox("اختر الصفقة", list(market_names.keys()))
            
            if st.button("تجهيز الملف للتحميل"):
                selected_data = dict(market_names[choice])
                docx_file = create_pv1(selected_data)
                
                st.download_button(
                    label="💾 تحميل محضر PV1",
                    data=docx_file,
                    file_name=f"PV1_{choice}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("لا توجد صفقات مسجلة بعد.")
