import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
from datetime import date

st.set_page_config(page_title="نظام تدبير الصفقات - جماعة أسكاون", layout="wide")

st.title("🏛️ منظومة تدبير سندات الطلب والمحاضر")
st.markdown("---")

# قائمة الخيارات
option = st.sidebar.selectbox(
    "اختر نوع الوثيقة:",
    ["سند طلب (Bon de Commande)", "محضر فتح الأظرفة (PV)"]
)

if option == "سند طلب (Bon de Commande)":
    st.subheader("إعداد سند طلب جديد")
    with st.form("bc_form"):
        col1, col2 = st.columns(2)
        with col1:
            num_bc = st.text_input("رقم سند الطلب", "01/ASK/2025")
            date_bc = st.date_input("التاريخ", date.today())
            provider = st.text_input("اسم المورد")
        with col2:
            subject = st.text_input("الموضوع", "اقتناء معدات...")
            amount_ht = st.number_input("المبلغ الخام (HT)", min_value=0.0)
            tva = st.selectbox("الضريبة", [0.20, 0.10, 0.0])
        
        submitted = st.form_submit_button("توليد الوثيقة")
        # (كود توليد Word لسند الطلب كما في السابق...)

elif option == "محضر فتح الأظرفة (PV)":
    st.subheader("إعداد محضر لجنة فتح الأظرفة")
    with st.form("pv_form"):
        col1, col2 = st.columns(2)
        with col1:
            pv_type = st.selectbox("ترتيب المحضر", ["الأول", "الثاني", "الثالث", "الرابع"])
            num_ask = st.text_input("رقم السند", "01/ASK/2025")
            meeting_date = st.date_input("تاريخ الاجتماع")
            meeting_time = st.time_input("ساعة الاجتماع")
        with col2:
            subject_pv = st.text_area("موضوع الطلب", "كراء جرافة للأشغال المختلفة")
            winner = st.text_input("المتنافس (المقبول/المقصى)")
            amount_pv = st.number_input("المبلغ TTC", min_value=0.0)

        st.markdown("**أعضاء اللجنة:**")
        member1 = st.text_input("رئيس اللجنة", "محمد زيلالي")
        member2 = st.text_input("العضو 1", "مبارك باك")
        member3 = st.text_input("العضو 2", "عبد اللطيف أتقي")

        generate_pv = st.form_submit_button("توليد المحضر بصيغة Word")

    if generate_pv:
        doc = Document()
        # تنسيق المحضر بناءً على النموذج المرفوع
        doc.add_heading(f"المحضر رقم {pv_type}", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_heading("لجنة فتح الأظرفة - مسطرة سند الطلب", 2).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.add_run(f"الموضوع: {subject_pv}\n").bold = True
        p.add_run(f"بتاريخ {meeting_date} على الساعة {meeting_time}، اجتمعت اللجنة المكونة من:\n")
        p.add_run(f"- {member1} (رئيس اللجنة)\n- {member2}\n- {member3}\n")
        
        p.add_run(f"\nبناءً على مقتضيات المادة 91 من المرسوم رقم 2-22-431 المتعلق بالصفقات العمومية، تم فحص العروض المقدمة لطلب السند رقم {num_ask}.\n")
        
        if pv_type == "الرابع":
            p.add_run(f"وبعد التأكد من تأكيد العرض، تم إرساء سند الطلب على شركة: {winner} بمبلغ {amount_pv:.2f} درهم مع احتساب الرسوم.")
        else:
            p.add_run(f"تقرر استدعاء شركة {winner} لتقديم إيضاحات أو تأكيد عرضها المالي البالغ {amount_pv:.2f} درهم.")

        bio = BytesIO()
        doc.save(bio)
        st.success(f"✅ تم إعداد المحضر {pv_type} بنجاح")
        st.download_button("📥 تحميل المحضر", bio.getvalue(), f"PV_{pv_type}_{num_ask}.docx")
