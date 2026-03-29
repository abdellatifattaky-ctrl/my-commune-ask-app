# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
import io
from dataclasses import dataclass
from datetime import date

# بيانات النموذج
@dataclass
class PVInput:
    num_ao: str
    objet: str
    est: float
    president: str
    date_ar: date
    date_fr: date
    date_portal: date

def create_automatic_pv(data: PVInput) -> io.BytesIO:
    doc = Document()
    doc.add_paragraph("المملكة المغربية\nوزارة الداخلية\nعمالة تارودانت\nجماعة أسكاون").alignment = 0

    doc.add_heading(f"محضر فتح الأظرفة رقم {data.num_ao}", 0)

    p = doc.add_paragraph()
    p.add_run("بناءً على الإعلانات المنشورة في:\n").bold = True
    p.add_run(f"- الجريدة العربية بتاريخ: {data.date_ar.strftime('%d/%m/%Y')}\n")
    p.add_run(f"- الجريدة الفرنسية بتاريخ: {data.date_fr.strftime('%d/%m/%Y')}\n")
    p.add_run(f"- بوابة الصفقات بتاريخ: {data.date_portal.strftime('%d/%m/%Y')}\n\n")
    p.add_run("اجتمعت اللجنة برئاسة السيد: ").add_run(f"{data.president}").bold = True
    p.add_run(f"\nبخصوص موضوع: {data.objet}")
    p.add_run(f"\nالتقدير المالي للمشروع: {data.est:,.2f} درهم")

    doc.add_page_break()
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# UI الأساسية
st.set_page_config(page_title="منصة صفقات أسكاون", layout="wide")
st.title("🇲🇦 نظام توليد وثائق الصفقات - جماعة أسكاون")

with st.container():
    st.subheader("🗓️ تواريخ النشر والإعلان (Publicité)")
    c_ar, c_fr, c_web = st.columns(3)
    try:
        d_ar = c_ar.date_input("الجريدة العربية (العلم)", value=date.today())
        d_fr = c_fr.date_input("الجريدة الفرنسية (L'Opinion)", value=date.today())
        d_web = c_web.date_input("بوابة الصفقات العمومية", value=date.today())
    except Exception:
        d_ar = d_fr = d_web = date.today()

    st.subheader("📝 معلومات الصفقة العامة")
    col1, col2 = st.columns(2)
    n_ao = col1.text_input("رقم طلب العروض", "01/ask/2025")
    objet = col1.text_area("موضوع الصفقة الكامل", "موضوع الصفقة القياسي")
    est = col2.number_input("التقدير المالي (درهم)", value=1060020.0)
    pres = col2.text_input("رئيس اللجنة", "ZILALI MOHAMED")

# توليد المحضر
def safe_to_generate():
    return all([n_ao.strip(), objet.strip(), pres.strip()])

st.divider()
if st.button("📄 توليد وتحميل المحضر الأول (1er PV)") and safe_to_generate():
    data_to_fill = PVInput(
        num_ao=n_ao,
        objet=objet,
        est=float(est),
        president=pres,
        date_ar=d_ar,
        date_fr=d_fr,
        date_portal=d_web
    )
    file_buffer = create_automatic_pv(data_to_fill)
    st.download_button(
        label="📥 اضغط هنا لتحميل المحضر بصيغة Word",
        data=file_buffer,
        file_name=f"PV1_{n_ao.replace('/', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
else:
    st.info("يرجى تعبئة الحقول الأساسية ثم الضغط على توليد.")

st.sidebar.success("✅ النظام يعمل الآن بدون الحاجة لرفع قوالب يدويًا")
