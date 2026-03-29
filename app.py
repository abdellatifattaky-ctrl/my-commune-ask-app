import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# إعداد الصفحة وتصميمها
st.set_page_config(page_title="نظام صفقات جماعة أسكاون", layout="wide")

# دالة توليد المستندات مع معالجة الأخطاء
def generate_document(template_name, data):
    # استخدام المسار النسبي الصحيح للمجلد
    template_path = os.path.join("templates", template_name)
    
    if not os.path.exists(template_path):
        st.error(f"⚠️ خطأ: القالب '{template_name}' غير موجود في مجلد templates. يرجى رفعه على GitHub بنفس الاسم تماماً.")
        return None
    try:
        doc = DocxTemplate(template_path)
        doc.render(data)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ خطأ فني أثناء المعالجة: {e}")
        return None

# الواجهة الرئيسية
st.title("🇲🇦 المنصة النهائية لتدبير الصفقات - جماعة أسكاون")
st.markdown("---")

# تبويبات العمل
tab1, tab2, tab3 = st.tabs(["📝 المحاضر والتقارير", "🚀 أوامر الخدمة (OS)", "📂 الأرشفة والتسلم"])

# --- التبويب الأول: المحاضر (PV1, PV2, PV3) ---
with tab1:
    st.header("إعداد محاضر فتح الأظرفة")
    
    with st.expander("🌐 بيانات النشر والإعلان (مهمة جداً)", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            date_ar = st.date_input("النشر بالجريدة العربية")
        with c2:
            date_fr = st.date_input("النشر بالجريدة الفرنسية")
        with c3:
            date_portal = st.date_input("النشر ببوابة الصفقات")

    col1, col2 = st.columns(2)
    with col1:
        num_ao = st.text_input("رقم طلب العروض (N° AO)", value="01/ask/2025")
        objet = st.text_area("موضوع الصفقة الكامل")
    with col2:
        estimation = st.number_input("تقدير الإدارة (Estimation)", value=1060020.00)
        president = st.text_input("رئيس اللجنة", value="ZILALI MOHAMED")

    st.divider()
    
    # أزرار التوليد
    p1, p2, p3 = st.columns(3)
    
    common_data = {
        "num_ao": num_ao,
        "objet": objet,
        "estimation": f"{estimation:,.2f}",
        "president": president,
        "date_ar": date_ar.strftime('%d/%m/%Y'),
        "date_fr": date_fr.strftime('%d/%m/%Y'),
        "date_portal": date_portal.strftime('%d/%m/%Y')
    }

    with p1:
        if st.button("توليد المحضر 1 (فتح الأظرفة)"):
            file = generate_document("1er_PV.docx", common_data)
            if file:
                st.download_button("📥 تحميل PV1", file, f"PV1_{num_ao.replace('/', '_')}.docx")

    with p2:
        if st.button("توليد المحضر 2 (المالي)"):
            # يمكن إضافة منطق حساب ثمن المرجع هنا
            file = generate_document("2eme_pv.docx", common_data)
            if file:
                st.download_button("📥 تحميل PV2", file, f"PV2_{num_ao.replace('/', '_')}.docx")

    with p3:
        if st.button("توليد المحضر 3 (الإرساء)"):
            file = generate_document("3eme_pv.docx", common_data)
            if file:
                st.download_button("📥 تحميل PV3", file, f"PV3_{num_ao.replace('/', '_')}.docx")

# --- التبويب الثاني: أوامر الخدمة ---
with tab2:
    st.header("إصدار أوامر الخدمة")
    os_type = st.radio("نوع الوثيقة", ["تبليغ المصادقة (Notification)", "بداية الأشغال (Commencement)"])
    
    with st.form("os_form"):
        ste = st.text_input("اسم الشركة", value="NOOR SAD TRAVAUX")
        gerant = st.text_input("المسير", value="AIT EL MAALE M HALID")
        registre = st.text_input("رقم السجل/الأمر", value="01/2025")
        
        if st.form_submit_button("توليد أمر الخدمة"):
            tmpl = "os_notification.docx" if "Notification" in os_type else "os_commencement.docx"
            os_data = {
                **common_data,
                "nom_societe": ste,
                "nom_gerant": gerant,
                "num_registre": registre
            }
            file_os = generate_document(tmpl, os_data)
            if file_os:
                st.download_button(f"📥 تحميل {os_type}", file_os, f"OS_{num_ao.replace('/', '_')}.docx")

# --- التبويب الثالث: الأرشفة ---
with tab3:
    st.header("التسلم والأرشفة الذكية")
    st.info("سيتم تخزين جميع الوثائق المولدة في قاعدة بيانات النظام للرجوع إليها.")
    if st.button("توليد محضر التسلم (قالب افتراضي)"):
        st.warning("يرجى التأكد من رفع قالب 'pv_reception.docx' لتفعيل هذه الميزة.")
