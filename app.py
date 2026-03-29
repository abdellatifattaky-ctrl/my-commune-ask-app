import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os

# 1. إعداد المكتبات (تأكد من وجود docxtpl في requirements.txt)
try:
    from docxtpl import DocxTemplate
except:
    st.error("الرجاء إضافة docxtpl إلى ملف requirements.txt")

st.set_page_config(page_title="مصلحة الصفقات - أسكاون", layout="wide")

# 2. وظيفة إنشاء الملفات
def create_document(data, type_doc):
    # إنشاء ملف Word فارغ وبرمجته برمجياً (حل مؤقت لعدم وجود قوالب)
    # في حالة وجود قوالب في مجلد templates سيستخدمها الكود تلقائياً
    template_path = f"templates/{type_doc}.docx"
    
    if os.path.exists(template_path):
        doc = DocxTemplate(template_path)
        doc.render(data)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    else:
        st.warning(f"⚠️ تنبيه: لم يتم العثور على ملف {type_doc}.docx في مجلد templates. يرجى رفعه ليعمل التصميم الخاص بك.")
        return None

# 3. واجهة المستخدم
st.title("🇲🇦 تدبير صفقات جماعة أسكاون")
st.info("هذه النسخة تدعم تواريخ النشر بالجرائد والبوابة")

# مدخلات النشر
with st.expander("📅 تواريخ النشر والإعلان", expanded=True):
    col_ar, col_fr, col_web = st.columns(3)
    d_ar = col_ar.date_input("الجريدة العربية (العلم)")
    d_fr = col_fr.date_input("الجريدة الفرنسية (L'Opinion)")
    d_web = col_web.date_input("بوابة الصفقات العمومية")

# مدخلات الصفقة
with st.container():
    c1, c2 = st.columns(2)
    n_ao = c1.text_input("رقم طلب العروض", "01/ask/2025")
    objet = c1.text_area("موضوع الصفقة")
    est = c2.number_input("التقدير المالي (درهم)", value=1060020.00)
    pres = c2.text_input("رئيس اللجنة", "ZILALI MOHAMED")

# أزرار التوليد
st.markdown("---")
if st.button("📄 توليد المحضر الأول (1er PV)"):
    data = {
        "num_ao": n_ao,
        "objet": objet,
        "estimation": f"{est:,.2f}",
        "president": pres,
        "date_ar": d_ar.strftime('%d/%m/%Y'),
        "date_fr": d_fr.strftime('%d/%m/%Y'),
        "date_portal": d_web.strftime('%d/%m/%Y')
    }
    
    file = create_document(data, "1er_PV")
    if file:
        st.download_button("📥 اضغط هنا لتحميل المحضر", file, f"PV1_{n_ao.replace('/','_')}.docx")

# تعليمات بسيطة لك
st.sidebar.header("💡 تعليمات بسيطة")
st.sidebar.write("1. ارفع ملفاتك بصيغة .docx")
st.sidebar.write("2. ضعها داخل مجلد اسمه templates")
st.sidebar.write("3. تأكد أن ملف requirements.txt يحتوي على كلمة docxtpl")
