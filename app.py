import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- 1. الإعدادات القانونية والتقنية ---
st.set_page_config(page_title="منظومة جماعة أسكاون الرقمية 2026", layout="wide")

MAX_BC_LIMIT = 500000  # سقف 50 مليون سنتيم حسب طلب مدير المصالح
LAW_NOTICE_DAYS = 15   # أجل استدعاء أعضاء المجلس (المادة 35)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('askaouen_integrated_system.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول القانونية
c.execute('CREATE TABLE IF NOT EXISTS budget (type TEXT, item TEXT, amount REAL, date TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS members (name TEXT, district TEXT, phone TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS properties (name TEXT, type TEXT, status TEXT, rent REAL)')
c.execute('CREATE TABLE IF NOT EXISTS legal_cases (ref TEXT, opponent TEXT, court TEXT, status TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS permits (type TEXT, requester TEXT, status TEXT, date TEXT)')
conn.commit()

# --- 2. نظام الدخول والصلاحيات ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

def login_system():
    if not st.session_state['logged_in']:
        st.title("🏛️ بوابة الإدارة الرقمية - جماعة أسكاون")
        st.subheader("الامتثال للقوانين المغربية: 113.14 | 57.19 | مرسوم صفقات 2023")
        with st.form("login_gate"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول آمن"):
                users = {
                    "admin_askaoun": {"pwd": "DM_2026", "role": "مدير المصالح"},
                    "tech_urban": {"pwd": "Askaoun@Tech", "role": "التعمير"},
                    "fin_service": {"pwd": "Askaoun@Fin", "role": "المالية"}
                }
                if u in users and users[u]["pwd"] == p:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = users[u]["role"]
                    st.rerun()
                else: st.error("خطأ في بيانات الدخول")
        st.stop()

login_system()

# --- 3. واجهة التحكم الرئيسية ---
role = st.session_state['role']
st.sidebar.title(f"👤 {role}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state['logged_in'] = False
    st.rerun()

menu = st.sidebar.radio("المصالح الإدارية:", [
    "📑 الصفقات وسندات الطلب (50M)",
    "⚖️ شؤون المجلس والاستدعاءات",
    "🏠 الأملاك الجماعية والجبايات",
    "⚖️ المنازعات القضائية",
    "👥 الموارد البشرية",
    "🏠 التعمير والرخص"
])

# --- 4. الوظائف والمصالح ---

# أ. مصلحة الصفقات (مرسوم مارس 2023)
if menu == "📑 الصفقات وسندات الطلب (50M)":
    st.header("📑 تدبير الطلبيات العمومية (مرسوم 8 مارس 2023)")
    st.info(f"💡 السقف المعتمد لسندات الطلب (BC): {MAX_BC_LIMIT:,} درهم")
    
    with st.form("bc_form"):
        col1, col2 = st.columns(2)
        obj = col1.text_input("موضوع الطلبية")
        amt = col2.number_input("المبلغ (TTC)", min_value=0.0)
        vendor = st.text_input("المورد المقترح (بعد استشارة 3 منافسين)")
        
        if st.form_submit_button("حفظ وتوليد السند"):
            if amt > MAX_BC_LIMIT:
                st.error("⚠️ خرق قانوني: المبلغ يتجاوز سقف 50 مليون سنتيم!")
            else:
                st.success("✅ العملية مطابقة للمادة 91 من مرسوم الصفقات.")
                # توليد مستند Word
                doc = Document()
                doc.add_heading('BON DE COMMANDE (BC)', 0)
                doc.add_paragraph(f"Conformément au décret n° 2-22-431 du 8 mars 2023.")
                doc.add_paragraph(f"Objet: {obj}\nMontant: {amt} DH\nFournisseur: {vendor}")
                bio = BytesIO(); doc.save(bio)
                st.download_button("📥 تحميل سند الطلب جاهز", bio.getvalue(), "BC_Askaoun.docx")

# ب. شؤون المجلس والاستدعاءات (قانون 113.14)
elif menu == "⚖️ شؤون المجلس والاستدعاءات":
    st.header("⚖️ تدبير دورات المجلس (المادة 35)")
    tab1, tab2 = st.tabs(["📧 إرسال الاستدعاءات", "📜 سجل المقررات"])
    
    with tab1:
        with st.form("conv"):
            s_type = st.selectbox("نوع الدورة", ["عادية فبراير", "عادية ماي", "عادية أكتوبر", "استثنائية"])
            s_date = st.date_input("تاريخ الانعقاد")
            agenda = st.text_area("جدول الأعمال")
            if st.form_submit_button("تجهيز الاستدعاء الرسمي"):
                diff = (s_date - date.today()).days
                if "عادية" in s_type and diff < LAW_NOTICE_DAYS:
                    st.warning(f"⚠️ المادة 35: الأجل المتبقي ({diff} يوم) أقل من 15 يوماً القانونية!")
                
                doc = Document()
                p = doc.add_paragraph("المملكة المغربية - وزارة الداخلية\nجماعة أسكاون")
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                doc.add_heading('إستدعاء لحضور دورة المجلس', 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph(f"بناءً على المادة 35 من القانون التنظيمي 113.14...")
                doc.add_paragraph(f"يدعوكم رئيس الجماعة لحضور {s_type} يوم {s_date}")
                doc.add_paragraph(f"جدول الأعمال: {agenda}")
                bio = BytesIO(); doc.save(bio)
                st.download_button("📥 تحميل الاستدعاء (Docx)", bio.getvalue(), "Convocation.docx")

# ج. الأملاك الجماعية (قانون 57.19)
elif menu == "🏠 الأملاك الجماعية والجبايات":
    st.header("🏠 تدبير الأملاك العقارية (Loi 57.19)")
    with st.expander("➕ تسجيل ملك جماعي جديد (سجل المحتويات)"):
        with st.form("prop"):
            name = st.text_input("اسم العقار")
            t = st.selectbox("النوع", ["دكان كراء", "بقعة أرضية", "مرفق عمومي"])
            rent = st.number_input("السومة الكرائية شهرياً", min_value=0.0)
            if st.form_submit_button("حفظ"):
                c.execute("INSERT INTO properties VALUES (?, ?, 'محفظ', ?)", (name, t, rent))
                conn.commit()
    df_p = pd.read_sql_query("SELECT * FROM properties", conn)
    st.dataframe(df_p, use_container_width=True)

# د. المنازعات القضائية
elif menu == "⚖️ المنازعات القضائية":
    st.header("⚖️ تتبع القضايا بالمحاكم الإدارية")
    st.warning("تنبيه: تتبع المنازعات يحمي ميزانية الجماعة من الاقتطاعات المفاجئة.")
    with st.form("lawsuit"):
        ref = st.text_input("رقم الملف")
        opp = st.text_input("الطرف الخصم")
        court = st.selectbox("المحكمة", ["إدارية أكادير", "استئنافية مراكش", "محكمة النقض"])
        if st.form_submit_button("تسجيل القضية"):
            c.execute("INSERT INTO legal_cases VALUES (?, ?, ?, 'في طور التقاضي')", (ref, opp, court))
            conn.commit()
    df_l = pd.read_sql_query("SELECT * FROM legal_cases", conn)
    st.table(df_l)

# هـ. الموارد البشرية والتعمير (نماذج سريعة)
elif menu == "👥 الموارد البشرية":
    st.header("👥 تدبير الموظفين (Loi 113.14)")
    st.info("هنا يتم تتبع المسار المهني والترقيات.")
    df_rh = pd.read_sql_query("SELECT * FROM staff", conn)
    st.write(df_rh)

elif menu == "🏠 التعمير والرخص":
    st.header("🏠 مصلحة التعمير (Loi 12.90)")
    with st.form("permit"):
        req = st.text_input("صاحب الطلب")
        p_type = st.selectbox("النوع", ["رخصة بناء", "شهادة سكن", "رخصة إصلاح"])
        if st.form_submit_button("تسجيل الملف"):
            c.execute("INSERT INTO permits VALUES (?, ?, 'قيد الدراسة', ?)", (p_type, req, str(date.today())))
            conn.commit()
    st.dataframe(pd.read_sql_query("SELECT * FROM permits", conn), use_container_width=True)
