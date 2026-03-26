import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# --- 1. إعدادات الصفحة (ضروري تكون هي الأولى) ---
st.set_page_config(page_title="مدير مصالح أسكاون - النظام الشامل", layout="wide")

# --- 2. تخصيص المظهر (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Coat_of_arms_of_Morocco.svg", width=80)
    st.title("جماعة أسكاون")
    st.write("---")
    menu = st.radio("القائمة الرئيسية:", [
        "📊 لوحة القيادة (Dashboard)",
        "🏗️ سندات الطلب والصفقات (BC/AO)",
        "👥 الموارد البشرية (RH)",
        "🚜 الحظيرة والمحروقات",
        "💰 المداخيل والممتلكات (الكراء)",
        "🏛️ الدورات والمقررات",
        "📂 مكتب الضبط الرقمي"
    ])
    st.write("---")
    st.info("متصل بصفة: مدير المصالح")

# --- 4. محتوى الوحدات ---

# --- الوحدة 1: لوحة القيادة ---
if menu == "📊 لوحة القيادة (Dashboard)":
    st.header("📊 الوضعية العامة للجماعة")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("مراسلات مستعجلة", "3", "🔴")
    c2.metric("صفقات جارية", "5", "🔵")
    c3.metric("آليات في الخدمة", "90%", "🟢")
    c4.metric("فائض الميزانية التقديري", "240k", "DH")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📉 استهلاك فصول الميزانية")
        df_budget = pd.DataFrame({
            "الفصل": ["المحروقات", "أدوات المكتب", "قطع الغيار", "الإطعام"],
            "المستهلك": [85, 40, 20, 15],
            "المتبقي": [15, 60, 80, 85]
        })
        fig = px.bar(df_budget, x="الفصل", y=["المستهلك", "المتبقي"], title="نسبة الاستهلاك %")
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        st.subheader("🔔 تنبيهات النظام الذكية")
        st.error("شركة 'OUBRAIM' تجاوزت أجل التنفيذ في سند الطلب رقم 04/2026.")
        st.warning("الفحص التقني لشاحنة النفايات رقم 1 ينتهي بعد 3 أيام.")

# --- الوحدة 2: سندات الطلب والصفقات ---
elif menu == "🏗️ سندات الطلب والصفقات (BC/AO)":
    st.header("🏗️ تدبير الطلبيات العمومية")
    tab1, tab2 = st.tabs(["📝 سندات الطلب (BC)", "🏗️ الصفقات الكبرى (AO)"])
    with tab1:
        st.subheader("إعداد محاضر BC")
        bc_num = st.text_input("رقم السند", "01/ASK/2026")
        st.info("غداً سنضيف هنا النصوص الفرنسية المصححة (PV, Notification, OS).")
        if st.button("تجهيز الملف المؤقت"): st.success("الملف جاهز")
    with tab2:
        st.subheader("تتبع مراحل AO")
        st.select_slider("مرحلة الصفقة:", options=["DCE", "النشر", "فتح الأظرفة", "التقييم", "المصادقة"])

# --- الوحدة 3: الموارد البشرية ---
elif menu == "👥 الموارد البشرية (RH)":
    st.header("👥 تدبير الموظفين")
    st.subheader("⏰ تنبيهات التقاعد (Retraite)")
    df_rh = pd.DataFrame([
        {"الموظف": "أحمد ..", "الإطار": "محرر", "تاريخ التقاعد": "2026-11-20"},
        {"الموظف": "خديجة ..", "الإطار": "متصرف", "تاريخ التقاعد": "2027-04-15"}
    ])
    st.table(df_rh)
    if st.button("توليد قرار رخصة إدارية"): st.info("جاري إعداد النموذج...")

# --- الوحدة 4: الحظيرة والمحروقات ---
elif menu == "🚜 الحظيرة والمحروقات":
    st.header("🚜 تتبع الآليات والمحروقات")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("⛽ سجل الكازوال")
        st.number_input("الكمية (لتر)", value=0)
        st.button("تسجيل استهلاك")
    with col_v2:
        st.subheader("🛠️ الحالة التقنية")
        st.write("سيارة الإسعاف: تأمين ينتهي في 30/04/2026")

# --- الوحدة 5: المداخيل والممتلكات ---
elif menu == "💰 المداخيل والممتلكات (الكراء)":
    st.header("💰 مداخيل الجماعة (الكراء)")
    rent_data = pd.DataFrame([
        {"المرفق": "محل 1", "المستأجر": "أحمد", "السومة": 1200, "الحالة": "🔴 متأخر"},
        {"المرفق": "مجزرة", "المستأجر": "شركة X", "السومة": 5000, "الحالة": "🟢 مؤدى"}
    ])
    st.dataframe(rent_data, use_container_width=True)
    if st.button("إصدار إنذارات أداء"): st.warning("تم تجهيز رسائل الإنذار.")

# --- الوحدة 6: الدورات والمقررات ---
elif menu == "🏛️ الدورات والمقررات":
    st.header("🏛️ أمانة المجلس والدورات")
    st.date_input("تاريخ الدورة القادمة")
    st.text_area("جدول الأعمال")
    if st.button("توليد استدعاءات الأعضاء"): st.success("تم التوليد")

# --- الوحدة 7: مكتب الضبط الرقمي ---
elif menu == "📂 مكتب الضبط الرقمي":
    st.header("📂 تتبع المراسلات")
    st.text_input("بحث برقم الإرسالية...")
    df_mail = pd.DataFrame([
        {"الرقم": "552", "المصدر": "العمالة", "الموضوع": "طلب إحصاء", "الحالة": "تم الرد"},
        {"الرقم": "553", "المصدر": "الخزينة", "الموضوع": "رفض حوالة", "الحالة": "قيد المعالجة"}
    ])
    st.table(df_mail)
