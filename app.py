import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import date

st.set_page_config(page_title="منظومة الجماعة الرقمية", layout="centered")

st.title("🏛️ بوابة التدبير الإداري للجماعة")
st.markdown("---")

# اختيار نوع الوثيقة
option = st.selectbox("اختر نوع الوثيقة التي تريد إصدارها:", 
                     ["سند طلب (Bon de Commande)", "محضر فتح الأظرفة (PV)"])

if option == "سند طلب (Bon de Commande)":
    with st.form("bc_form"):
        num_bc = st.text_input("رقم سند الطلب", "01/2026")
        provider = st.text_input("اسم المورد / الشركة")
        subject = st.text_input("موضوع الطلبية")
        amount = st.number_input("المبلغ الإجمالي (TTC)", min_value=0.0)
        submitted = st.form_submit_button("توليد الوثيقة")

        if submitted:
            doc = Document()
            # إعداد الفقرات لتكون من اليمين لليسار
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(f"جماعة: ...................\nسند طلب رقم: {num_bc}")
            run.bold = True
            
            doc.add_heading("سند طلب", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph(f"إلى السيد: {provider}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_paragraph(f"الموضوع: {subject}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            doc.add_paragraph(f"المبلغ الإجمالي: {amount} درهم").alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            bio = BytesIO()
            doc.save(bio)
            st.success("✅ جاهز للتحميل")
            st.download_button("📥 تحميل الوثيقة", bio.getvalue(), f"BC_{num_bc}.docx")

else:
    st.info("📩 من فضلك أرسل لي نص المحضر الذي تستعملونه الآن، لكي أضيفه لك هنا ويصبح التطبيق يملأ بياناته تلقائياً.")
