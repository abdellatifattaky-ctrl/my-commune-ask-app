import streamlit as st
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة دورات المجالس - القانون المغربي", layout="wide")

# تصميم الواجهة بالعربية
st.markdown("""
    <style>
    .report-font { font-family: 'Arial'; text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ نظام إدارة دورات المجالس (وفق القانون المغربي)")
st.sidebar.header("لوحة التحكم")

menu = ["توليد استدعاء الأعضاء", "تحرير محضر الدورة", "حول النظام القانوني"]
choice = st.sidebar.selectbox("اختر المهمة", menu)

# --- القسم الأول: استدعاء الأعضاء ---
if choice == "توليد استدعاء الأعضاء":
    st.header("✉️ إرسال استدعاءات رسمية")
    with st.form("invitation_form"):
        council_name = st.text_input("اسم المجلس الجماعي/الإقليمي")
        session_type = st.selectbox("نوع الدورة", ["دورة عادية", "دورة استثنائية"])
        session_date = st.date_input("تاريخ الانعقاد")
        session_time = st.time_input("ساعة الانعقاد")
        agenda = st.text_area("جدول الأعمال (نقطة لكل سطر)")
        members_list = st.text_area("قائمة الأعضاء (فصل بفاصلة)")
        
        submit = st.form_submit_button("توليد الاستدعاءات")
        
        if submit:
            members = [m.strip() for m in members_list.split(",")]
            st.success(f"تم توليد {len(members)} استدعاء بنجاح.")
            for member in members:
                invitation_text = f"""
                المملكة المغربية
                وزارة الداخلية
                مجلس: {council_name}
                
                إلى السيد(ة): {member}
                الموضوع: استدعاء لحضور {session_type}.
                
                بناءً على القانون التنظيمي 113.14، يتشرف رئيس المجلس بدعوتكم لحضور أشغال الدورة 
                المقرر عقدها بتاريخ {session_date} على الساعة {session_time} بمقر الجماعة.
                
                جدول الأعمال:
                {agenda}
                """
                st.text_area(f"استدعاء: {member}", invitation_text, height=200)

# --- القسم الثاني: تحرير المحضر ---
elif choice == "تحرير محضر الدورة":
    st.header("📝 صياغة محضر الدورة القانوني")
    
    col1, col2 = st.columns(2)
    with col1:
        quorum = st.number_input("عدد الأعضاء المزاولين للمهام", min_value=1)
        present = st.number_input("عدد الحاضرين", min_value=0)
    
    with col2:
        is_public = st.checkbox("جلسة علنية", value=True)
        chairman = st.text_input("رئيس الجلسة")

    decisions = st.text_area("المقررات المتخذة ونتائج التصويت")

    if st.button("توليد المحضر النهائي"):
        # التحقق من النصاب القانوني (تبسيط للمادة 42)
        status = "قانوني" if present > (quorum / 2) else "غير مكتمل النصاب (يؤجل وفق المادة 43)"
        
        full_report = f"""
        محضر {datetime.now().strftime('%Y/%m/%d')}
        بناءً على القانون التنظيمي المتعلق بالجماعات، انعقدت الجلسة برئاسة {chairman}.
        حالة النصاب: {status} ({present}/{quorum})
        طبيعة الجلسة: {"علنية" if is_public else "سرية"}
        
        المقررات:
        {decisions}
        
        توقيع الرئيس: _______________    توقيع كاتب المجلس: _______________
        """
        st.download_button("تحميل المحضر كملف نصي", full_report, file_name="minutes.txt")
        st.code(full_report)

# --- القسم الثالث: معلومات قانونية ---
else:
    st.info("هذا البرنامج مصمم وفق مقتضيات القانون التنظيمي 113.14 المغربي، خاصة المواد المتعلقة بآجال الاستدعاء (7 أيام للدورات العادية) وقواعد النصاب القانوني.")
