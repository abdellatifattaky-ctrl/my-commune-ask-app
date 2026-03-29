import streamlit as st
from docxtpl import DocxTemplate
import json
import os
from datetime import datetime

# إعداد واجهة التطبيق
st.set_page_config(page_title="منصة تدبير الصفقات العمومية", layout="wide")
st.title("🇲🇦 نظام إدارة وتوليد وثائق الصفقات العمومية")

# وظيفة لحفظ البيانات
def save_deal(data):
    if not os.path.exists('database.json'):
        with open('database.json', 'w') as f: json.dump([], f)
    
    with open('database.json', 'r+') as f:
        deals = json.load(f)
        deals.append(data)
        f.seek(0)
        json.dump(deals, f, indent=4)

# --- واجهة إدخال صفقة جديدة ---
with st.sidebar:
    st.header("إضافة صفقة جديدة")
    ref = st.text_input("رقم الصفقة (N° AO)", placeholder="مثال: 05/2026/INDH")
    objet = st.text_area("موضوع الصفقة")
    budget = st.number_input("الميزانية التقديرية (TTC)", min_value=0.0)
    stage = st.selectbox("المرحلة الحالية", [
        "الإعداد (Préparation)", 
        "النشر (Publication)", 
        "افتتاح الأظرفة (Ouverture)", 
        "الأمر بالخدمة (OS)"
    ])
    
    if st.button("حفظ الصفقة"):
        new_deal = {
            "ref": ref, "objet": objet, "budget": budget, 
            "stage": stage, "date_creation": str(datetime.now().date())
        }
        save_deal(new_deal)
        st.success("تم تسجيل الصفقة بنجاح!")

# --- عرض الصفقات وتوليد الوثائق ---
st.header("📋 لائحة الصفقات الجارية")
if os.path.exists('database.json'):
    with open('database.json', 'r') as f:
        deals = json.load(f)
        
    for deal in deals:
        with st.expander(f"الصفقة رقم: {deal['ref']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**الموضوع:** {deal['objet']}")
                st.write(f"**المرحلة:** {deal['stage']}")
            
            with col2:
                st.write("**توليد الوثائق القانونية:**")
                
                # زر توليد وثيقة بناءً على المرحلة
                if deal['stage'] == "الأمر بالخدمة (OS)":
                    if st.button(f"تحميل OS لـ {deal['ref']}", key=deal['ref']):
                        # ملاحظة: يجب توفر ملف os_template.docx في مجلد templates
                        st.info("جاري تحضير وثيقة Ordre de Service...")
                        # هنا نضع كود docxtpl الذي شرحناه سابقاً
                
                elif deal['stage'] == "افتتاح الأظرفة (Ouverture)":
                    st.button(f"توليد PV d'ouverture")
