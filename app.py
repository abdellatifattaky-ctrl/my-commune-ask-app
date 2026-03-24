import streamlit as st
from datetime import date

# إعدادات واجهة التطبيق
st.set_page_config(page_title="نظام المراسلات الإدارية - الجماعة", layout="centered")

st.title("📂 نظام تدبير سندات الطلب")
st.markdown("---")

# قسم إدخال البيانات
with st.form("bc_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        num_bc = st.text_input("رقم سند الطلب", "01/2026")
        date_bc = st.date_input("تاريخ السند", date.today())
        provider = st.text_input("اسم المورد / الشركة")
        
    with col2:
        subject = st.text_input("موضوع الطلبية (Désignation)")
        amount_ht = st.number_input("المبلغ الخام (HT)", min_value=0.0)
        tva = st.selectbox("نسبة الضريبة (TVA)", [0.20, 0.10, 0.0])

    # حساب المبالغ تلقائياً
    total_ttc = amount_ht * (1 + tva)
    
    submitted = st.form_submit_button("توليد سند الطلب")

if submitted:
    st.success(f"✅ تم إعداد بيانات سند الطلب رقم {num_bc}")
    
    # نص سند الطلب المنسق
    bc_content = f"""
    المملكة المغربية
    جماعة: [اسم الجماعة]
    
    سند طلب رقم: {num_bc}
    بتاريخ: {date_bc}
    
    إلى السيد: {provider}
    الموضوع: {subject}
    
    المبلغ الخام: {amount_ht} درهم
    الضريبة: {tva * 100}%
    المبلغ الإجمالي (TTC): {total_ttc:.2f} درهم
    
    توقيع رئيس الجماعة: ............................
    """
    
    # زر لتحميل السند كملف نصي (كمرحلة أولى للتجربة)
    st.download_button(
        label="📥 تحميل سند الطلب (Text)",
        data=bc_content,
        file_name=f"BC_{num_bc.replace('/', '_')}.txt",
        mime="text/plain"
    )
