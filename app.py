import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- 1. الإعدادات والروابط القانونية ---
st.set_page_config(page_title="منظومة جماعة أسكاون الرقمية 2026", layout="wide")

# ثوابت النظام
MAX_BC_LIMIT = 500000  # سقف 50 مليون سنتيم لسندات الطلب
LAW_NOTICE_DAYS = 15   # أجل استدعاء أعضاء المجلس (المادة 35)

# الاتصال بقاعدة البيانات وإنشاء الجداول
conn = sqlite3.connect('askaouen_legal_system.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS properties (name TEXT, type TEXT, status TEXT, rent REAL)')
c.execute('CREATE TABLE IF NOT EXISTS legal_cases (ref TEXT, opponent TEXT, court TEXT, status TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS permits (type TEXT, requester TEXT, status TEXT, date TEXT)')
conn.commit()

# --- 2. إدارة الجلسة والدخول (حل مشكلة KeyError) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

def check_login(u, p):
    users = {
        "admin_askaoun": {"pwd": "DM_2026", "role": "مدير المصالح"},
        "tech_urban": {"pwd": "Askaoun@Tech", "role": "مصلحة التعمير"},
        "fin_service": {"pwd": "Askaoun@Fin", "role": "المصلحة المالية"}
    }
    if u in users and users[u]["pwd"] == p:
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = users[u]["role"]
        return True
    return False

# واجهة الدخول المنفصلة
if not st.session_state['logged_in']:
    st.title("🏛️ بوابة الإدارة الرقمية - جماعة أسكاون")
    st.subheader("الامتثال للقوانين المغربية: 113.14 | 57.19 | مرسوم صفقات 2023")
    with st.form("login_form"):
        u_input = st.text_input("اسم المستخدم")
        p_input = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول آمن"):
            if check_login(u_input, p_input):
                st.rerun()
            else:
                st.error("⚠️ بيانات الدخول غير صحيحة")
    st.stop()  # التوقف هنا حتى يتم تسجيل الدخول

# --- 3. لوحة التحكم بعد الدخول الآمن ---
role = st.session_state['user_role']
st.sidebar.title(f"👤 {role}")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.rerun()

menu = st.sidebar.radio("المصالح الإدارية والقانونية:", [
    "📑 الصفقات وسندات الطلب (50M)",
    "⚖️ شؤون المجلس والاستدعاءات",
    "🏠 الأملاك الجماعية (57.19)",
    "⚖️ المنازعات القضائية",
    "🏠 التعمير والرخص (12.90)"
])

# --- 4. محتوى المصالح والوظائف ---

# أ. الصفقات (مرسوم مارس 2023)
if menu == "📑 الصفقات وسندات الطلب (50M)":
    st.header("📑 تدبير الطلبيات والصفقات")
    st.info(f"💡 سقف سند الطلب (BC) مبرمج قانونياً على {MAX_BC_LIMIT:,} درهم.")
    with st.form("bc_gen"):
        obj = st.text_input("موضوع الطلبية")
        amt = st.number_input("المبلغ الإجمالي (DH)", min_value=0.0)
        vendor = st.text_input("المورد المختار")
        if st.form_submit_button("توليد ملف السند"):
            if amt > MAX_BC_LIMIT:
                st.error("⚠️ خرق قانوني: المبلغ يتجاوز 50 مليون سنتيم!")
            else:
                st.success("✅ العملية مطابقة للمادة 91 من مرسوم الصفقات.")
                doc = Document()
                doc.add_heading('Bon de Commande - Commune Askaoun', 0)
                doc.add_paragraph(f"Objet: {obj}\nMontant: {amt} DH\nFournisseur: {vendor}")
                bio = BytesIO(); doc.save(bio)
                st.download_button("📥 تحميل المستند", bio.getvalue(), "BC_Askaoun.docx")

# ب. شؤون المجلس (قانون 113.14)
elif menu == "⚖️ شؤون المجلس والاستدعاءات":
    st.header("⚖️ استدعاءات الأعضاء والمقررات")
    with st.form("conv_form"):
        s_type = st.selectbox("نوع الدورة", ["عادية فبراير", "عادية ماي", "عادية أكتوبر", "استثنائية"])
        s_date = st.date_input("تاريخ الاجتماع")
        agenda = st.text_area("جدول الأعمال")
        if st.form_submit_button("توليد الاستدعاء الرسمي"):
            diff = (s_date - date.today()).days
            if "عادية" in s_type and diff < LAW_NOTICE_DAYS:
                st.warning(f"⚠️ مخالفة للمادة 35: الأجل المتبقي ({diff} أيام) أقل من 15 يوماً!")
            
            doc = Document()
            doc.add_heading('إستدعاء لحضور دورة المجلس', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph(f"بناءً على المادة 35 من القانون التنظيمي 113.14...")
            doc.add_paragraph(f"يدعوكم رئيس الجماعة لحضور {s_type} يوم {s_date}")
            doc.add_paragraph(f"جدول الأعمال: {agenda}")
            bio = BytesIO(); doc.save(bio)
            st.download_button("📥 تحميل الاستدعاء (Docx)", bio.getvalue(), "Convocation.docx")

# ج. الأملاك الجماعية (قانون 57.19)
elif menu == "🏠 الأملاك الجماعية (57.19)":
    st.header("🏠 سجل الممتلكات والجبايات")
    with st.form("prop_add"):
        p_name = st.text_input("اسم العقار")
        p_type = st.selectbox("النوع", ["محل تجاري", "بقعة أرضية", "سكن وظيفي"])
        rent = st.number_input("السومة الكرائية", min_value=0.0)
        if st.form_submit_button("تسجيل الملك"):
            c.execute("INSERT INTO properties VALUES (?, ?, 'محفظ', ?)", (p_name, p_type, rent))
            conn.commit()
            st.success("تم الحفظ في سجل المحتويات.")
    st.dataframe(pd.read_sql_query("SELECT * FROM properties", conn), use_container_width=True)

# د. المنازعات القضائية
elif menu == "⚖️ المنازعات القضائية":
    st.header("⚖️ تتبع القضايا والمنازعات")
    st.warning("تنبيه لمدير المصالح: تتبع الآجال القانونية للطعن يجنب الجماعة غرامات التأخير.")
    with st.form("case_add"):
        ref = st.text_input("رقم الملف القضائي")
        opp = st.text_input("الطرف الخصم")
        if st.form_submit_button("تسجيل ملف قضائي"):
            c.execute("INSERT INTO legal_cases VALUES (?, ?, 'إدارية أكادير', 'قيد التقاضي')", (ref, opp))
            conn.commit()
    st.table(pd.read_sql_query("SELECT * FROM legal_cases", conn))

# هـ. التعمير (قانون 12.90)
elif menu == "🏠 التعمير والرخص (12.90)":
    st.header("🏠 مصلحة التعمير والشرطة الإدارية")
    with st.form("permit_add"):
        req = st.text_input("صاحب الطلب")
        p_type = st.selectbox("نوع الرخصة", ["رخصة بناء", "شهادة سكن", "رخصة ربط"])
        if st.form_submit_button("تسجيل الطلب"):
            c.execute("INSERT INTO permits VALUES (?, ?, 'قيد الدراسة', ?)", (p_type, req, str(date.today())))
            conn.commit()
    st.dataframe(pd.read_sql_query("SELECT * FROM permits", conn), use_container_width=True)
