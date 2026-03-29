import streamlit as st
from docx import Document
from docx.shared import Inches
import io
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="منصة صفقات أسكاون", layout="wide")

st.title("🇲🇦 نظام توليد وثائق الصفقات - جماعة أسكاون")
st.info("هذا النظام يولد الوثائق آلياً حتى بدون رفع قوالب خارجية")

# --- 1. إدخال البيانات (بما فيها تواريخ النشر) ---
with st.container():
    st.subheader("🗓️ تواريخ النشر والإعلان (Publicité)")
    c_ar, c_fr, c_web = st.columns(3)
    d_ar = c_ar.date_input("الجريدة العربية (العلم)")
    d_fr = c_fr.date_input("الجريدة الفرنسية (L'Opinion)")
    d_web = c_web.date_input("بوابة الصفقات العمومية")

    st.subheader("📝 معلومات الصفقة العامة")
    col1, col2 = st.columns(2)
    n_ao = col1.text_input("رقم طلب العروض", "01/ask/2025")
    objet = col1.text_area("موضوع الصفقة الكامل")
    est = col2.number_input("التقدير المالي (درهم)", value=1060020.00)
    pres = col2.text_input("رئيس اللجنة", "ZILALI MOHAMED")

# --- 2. محرك توليد الملف (بدون قوالب خارجية) ---
def create_automatic_pv(data):
    doc = Document()
    
    # رأس الصفحة
    doc.add_paragraph("المملكة المغربية\nوزارة الداخلية\nعمالة تارودانت\nجماعة أسكاون").alignment = 0
    
    doc.add_heading(f"محضر فتح الأظرفة رقم {data['num_ao']}", 0)
    
    # نص المحضر
    p = doc.add_paragraph()
    p.add_run(f"بناءً على الإعلانات المنشورة في:\n").bold = True
    p.add_run(f"- الجريدة العربية بتاريخ: {data['date_ar']}\n")
    p.add_run(f"- الجريدة الفرنسية بتاريخ: {data['date_fr']}\n")
    p.add_run(f"- بوابة الصفقات بتاريخ: {data['date_portal']}\n\n")
    
    p.add_run("اجتمعت اللجنة برئاسة السيد: ").add_run(f"{data['president']}").bold = True
    p.add_run(f"\nبخصوص موضوع: {data['objet']}")
    p.add_run(f"\nالتقدير المالي للمشروع: {data['estimation']} درهم")
    
    doc.add_page_break()
    
    # حفظ في ذاكرة النظام
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 3. أزرار التحميل ---
st.divider()
if st.button("📄 توليد وتحميل المحضر الأول (1er PV)"):
    data_to_fill = {
        "num_ao": n_ao,
        "objet": objet,
        "estimation": f"{est:,.2f}",
        "president": pres,
        "date_ar": d_ar.strftime('%d/%m/%Y'),
        "date_fr": d_fr.strftime('%d/%m/%Y'),
        "date_portal": d_web.strftime('%d/%m/%Y')
    }
    
    file_buffer = create_automatic_pv(data_to_fill)
    st.download_button(
        label="📥 اضغط هنا لتحميل المحضر بصيغة Word",
        data=file_buffer,
        file_name=f"PV1_{n_ao.replace('/', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.sidebar.success("✅ النظام يعمل الآن بدون الحاجة لرفع قوالب يدويًا")
