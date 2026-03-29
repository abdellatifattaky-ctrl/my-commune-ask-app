import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os

# إعداد واجهة التطبيق
st.set_page_config(page_title="منصة صفقات أسكاون", layout="wide")

def generate_document(template_name, data):
    template_path = os.path.join("templates", template_name)
    if not os.path.exists(template_path):
        st.error(f"⚠️ الملف {template_name} غير موجود في مجلد templates")
        return None
    try:
        doc = DocxTemplate(template_path)
        doc.render(data)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ خطأ أثناء التوليد: {e}")
        return None

st.title("🇲🇦 نظام تدبير الصفقات العمومية - نسخة مطورة")

# تبويبات النظام
tab1, tab2, tab3 = st.tabs(["إعداد المحاضر (PV)", "أوامر الخدمة (OS)", "التسلم والأرشفة"])

with tab1:
    st.header("بيانات النشر والمحاضر")
    
    with st.expander("📅 تواريخ النشر القانونية (Publicité)"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            date_ar = st.date_input("النشر بالجريدة العربية")
        with col_b:
            date_fr = st.date_input("النشر بالجريدة الفرنسية")
        with col_c:
            date_portal = st.date_input("النشر ببوابة الصفقات")

    col1, col2 = st.columns(2)
    with col1:
        num_ao = st.text_input("رقم طلب العروض (N° AO)", value="01/ask/2025")
        objet = st.text_area("موضوع الصفقة")
    with col2:
        estimation = st.number_input("تقدير الإدارة (HT/TTC)", value=1060020.00)
        presidents = st.text_input("رئيس اللجنة", value="ZILALI MOHAMED")

    if st.button("توليد المحضر الأول (1er PV)"):
        data_pv1 = {
            "num_ao": num_ao,
            "objet": objet,
            "estimation": f"{estimation:,.2f}",
            "date_ar": date_ar.strftime('%d/%m/%Y'),
            "date_fr": date_fr.strftime('%d/%m/%Y'),
            "date_portal": date_portal.strftime('%d/%m/%Y'),
            "president": presidents
        }
        file = generate_document("1er_PV.docx", data_pv1)
        if file:
            st.download_button("📥 تحميل PV1", file, f"PV1_{num_ao.replace('/', '_')}.docx")

with tab2:
    st.header("أوامر الخدمة")
    os_option = st.selectbox("اختر نوع الوثيقة", ["Notification d'approbation", "Commencement des travaux"])
    
    with st.form("os_data"):
        ste_name = st.text_input("اسم الشركة", value="NOOR SAD TRAVAUX")
        gerant = st.text_input("المسير", value="AIT EL MAALE M HALID")
        registre_n = st.text_input("رقم السجل", value="01/2025")
        
        if st.form_submit_button("توليد الوثيقة"):
            tmpl = "os_notification.docx" if "Notification" in os_option else "os_commencement.docx"
            data_os = {
                "num_marche": num_ao,
                "nom_societe": ste_name,
                "nom_gerant": gerant,
                "num_registre": registre_n,
                "objet": objet
            }
            file_os = generate_document(tmpl, data_os)
            if file_os:
                st.download_button(f"📥 تحميل {os_option}", file_os, f"OS_{num_ao.replace('/', '_')}.docx")

with tab3:
    st.header("التسلم النهائي والمؤقت")
    # هنا يمكنك إضافة واجهة التسلم التي شرحناها سابقاً
    st.info("قم برفع قالب pv_reception.docx لتفعيل هذا القسم.")
