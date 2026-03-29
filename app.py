# تأكد أن هذا السطر يبدأ بنفس مستوى إزاحة الدوال السابقة
    init_procurement_smart_tables()

    # --- واجهة المستخدم الرئيسية ---
    # ملاحظة: إذا كان هذا الكود داخل "elif menu == ...", يجب إزاحته بـ 4 مسافات فقط
    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 توليد المحاضر"])

    with tabs[0]:
        st.subheader("إدخال بيانات الصفقة الأساسية")
        with st.form("market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة (N° AO)", placeholder="مثال: 01/2024")
                m_obj = st.text_area("موضوع الصفقة")
            with col2:
                m_date = st.date_input("تاريخ فتح الأظرفة")
                m_amount = st.number_input("التقدير المالي", min_value=0.0)

            submit_btn = st.form_submit_button("حفظ")
            if submit_btn:
                st.success(f"تم حفظ {m_ref}")

    # التبويب الثاني: عرض وإدارة الصفقات
    with tabs[1]:
        st.subheader("قائمة الصفقات المسجلة")
        refs = get_market_refs()
        if refs:
            selected_ref = st.selectbox("اختر صفقة:", refs)
            # ... باقي الكود
