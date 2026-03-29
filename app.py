import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منصة صفقات جماعة أسكاون", layout="wide")

# --- دالة توليد الوثائق ---
def generate_doc(template_name, data):
    try:
        doc = DocxTemplate(f"templates/{template_name}")
        doc.render(data)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"خطأ في القالب {template_name}: {e}")
        return None

# --- واجهة التطبيق ---
st.title("🇲🇦 المنصة المتكاملة لإدارة الصفقات العمومية - جماعة أسكاون")

tabs = st.tabs([
    "📂 إعداد وفتح الأظرفة (PV1)", 
    "📊 العروض المالية (PV2)", 
    "🏆 الإرساء النهائي (PV3)", 
    "✉️ أوامر الخدمة (OS)", 
    "🏁 التسلم والأرشفة"
])

# --- TAB 1: المحضر الأول ---
with tabs[0]:
    st.header("المحضر رقم 1: فتح الأظرفة")
    col1, col2 = st.columns(2)
    with col1:
        n_ao = st.text_input("رقم طلب العروض", value="01/ask/2026")
        date_seance = st.date_input("تاريخ الجلسة الأولى")
    with col2:
        objet = st.text_area("موضوع الصفقة")
    
    if st.button("توليد PV1"):
        data = {"n_ao": n_ao, "date": str(date_seance), "objet": objet}
        file = generate_doc("1er_PV.docx", data)
        if file:
            st.download_button("تحميل المحضر الأول", file, f"PV1_{n_ao}.docx")

# --- TAB 2: المحضر الثاني وحساب الأثمان ---
with tabs[1]:
    st.header("المحضر رقم 2: تحليل الأثمان")
    estimation = st.number_input("تقدير الإدارة (Estimation)", min_value=0.0)
    
    st.subheader("إدخال عروض المتنافسين")
    df_offers = pd.DataFrame([{"شركة": "", "العرض": 0.0}])
    edited_df = st.data_editor(df_offers, num_rows="dynamic")
    
    if st.button("حساب ثمن المرجع وتوليد PV2"):
        offers = edited_df["العرض"].tolist()
        valid_offers = [o for o in offers if o > 0]
        if valid_offers:
            ref_price = (estimation + (sum(valid_offers)/len(valid_offers))) / 2
            st.success(f"ثمن المرجع: {ref_price:,.2f} درهم")
            
            data_pv2 = {"estimation": estimation, "ref_price": ref_price, "n_ao": n_ao}
            file_pv2 = generate_doc("2eme_pv.docx", data_pv2)
            st.download_button("تحميل المحضر الثاني", file_pv2, f"PV2_{n_ao}.docx")

# --- TAB 3: المحضر الثالث ---
with tabs[2]:
    st.header("المحضر رقم 3: الإرساء النهائي")
    winner = st.text_input("الشركة الفائزة")
    final_amount = st.number_input("المبلغ النهائي")
    
    if st.button("توليد PV3"):
        data_pv3 = {"winner": winner, "amount": final_amount, "n_ao": n_ao}
        file_pv3 = generate_doc("3eme_pv.docx", data_pv3)
        st.download_button("تحميل المحضر النهائي", file_pv3, f"PV3_{n_ao}.docx")

# --- TAB 4: أوامر الخدمة (OS) ---
with tabs[3]:
    st.header("توليد أوامر الخدمة")
    type_os = st.selectbox("نوع الأمر", ["تبليغ المصادقة (Notification)", "بداية الأشغال (Commencement)"])
    
    with st.expander("بيانات المقاول"):
        nom_ste = st.text_input("اسم الشركة", key="os_ste")
        gerant = st.text_input("المسير")
        registre = st.text_input("رقم السجل")

    if st.button("توليد أمر الخدمة"):
        os_template = "os_notification.docx" if "Notification" in type_os else "os_commencement.docx"
        data_os = {"nom_societe": nom_ste, "nom_gerant": gerant, "num_registre": registre, "num_marche": n_ao}
        file_os = generate_doc(os_template, data_os)
        st.download_button(f"تحميل {type_os}", file_os, f"OS_{n_ao}.docx")

# --- TAB 5: التسلم والأرشفة ---
with tabs[4]:
    st.header("المحاضر النهائية والتخزين")
    type_rec = st.radio("نوع المحضر", ["تسلم مؤقت (Provisoire)", "تسلم نهائي (Définitif)"])
    date_rec = st.date_input("تاريخ التسلم")
    
    if st.button("توليد محضر التسلم"):
        data_rec = {"type": type_rec, "date": str(date_rec), "n_ao": n_ao}
        file_rec = generate_doc("pv_reception.docx", data_rec)
        st.download_button("تحميل محضر التسلم", file_rec, f"PV_Reception_{n_ao}.docx")
    
    st.divider()
    st.subheader("📁 نظام الأرشفة")
    # محاكاة مكان التخزين
    st.info("يتم تنظيم الملفات آلياً في مجلد الصفقات حسب السنة ورقم الصفقة.")
