# --- واجهة المستخدم الرئيسية ---
    tabs = st.tabs(["➕ تسجيل صفقة جديدة", "📊 إدارة الصفقات", "📄 توليد المحاضر"])

    # التبويب الأول: إدخال البيانات
    with tabs[0]:
        st.subheader("إدخال بيانات الصفقة الأساسية")
        with st.form("market_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_ref = st.text_input("مرجع الصفقة (N° AO)", placeholder="مثال: 01/2024")
                m_obj = st.text_area("موضوع الصفقة", placeholder="أشغال بناء...")
                m_owner = st.text_input("صاحب المشروع", value="رئيس جماعة اسكاون")
            with col2:
                m_date = st.date_input("تاريخ فتح الأظرفة")
                m_time = st.time_input("ساعة فتح الأظرفة")
                m_amount = st.number_input("التقدير المالي (Estimation)", min_value=0.0)

            submit_btn = st.form_submit_button("حفظ البيانات الأساسية")
            
            if submit_btn:
                # هنا يتم استدعاء دالة insert_record لحفظ البيانات في قاعدة البيانات
                # مثال: insert_record("INSERT INTO market_master_data ...")
                st.success(f"تم حفظ الصفقة رقم {m_ref} بنجاح!")

    # التبويب الثاني: عرض وإدارة الصفقات
    with tabs[1]:
        st.subheader("قائمة الصفقات المسجلة")
        refs = get_market_refs()
        if refs:
            selected_ref = st.selectbox("اختر صفقة لمعاينتها:", refs)
            data = get_market_data(selected_ref)
            if data:
                st.json(data) # عرض البيانات بشكل سريع للتأكد
        else:
            st.info("لا توجد صفقات مسجلة حالياً.")

    # التبويب الثالث: توليد وتحميل الملفات
    with tabs[2]:
        st.subheader("تحميل المحاضر والوثائق (Docx)")
        all_refs = get_market_refs()
        
        if all_refs:
            target_ref = st.selectbox("اختر الصفقة لإصدار وثائقها:", all_refs, key="gen_docs")
            
            col_a, col_b, col_c = st.columns(3)
            
            # زر تحميل PV1
            with col_a:
                if st.button("إنشاء PV1"):
                    doc, num = generate_pv1_docx(target_ref)
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.download_button(
                        label="تحميل PV1 (Word)",
                        data=bio.getvalue(),
                        file_name=f"PV1_{target_ref}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            # زر تحميل تقرير التقني
            with col_b:
                if st.button("إنشاء التقرير التقني"):
                    doc, num = generate_rapport_technique_docx(target_ref)
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.download_button(
                        label="تحميل Rapport Technique",
                        data=bio.getvalue(),
                        file_name=f"Rapport_{target_ref}.docx"
                    )
            
            # زر تحميل الإشعار بالتبليغ (OS)
            with col_c:
                if st.button("إنشاء OS Notification"):
                    doc, num = generate_os_notification_docx(target_ref)
                    if doc:
                        bio = io.BytesIO()
                        doc.save(bio)
                        st.download_button(
                            label="تحميل OS Notification",
                            data=bio.getvalue(),
                            file_name=f"OS_{target_ref}.docx"
                        )
        else:
            st.warning("يجب إضافة صفقة أولاً لتتمكن من إنشاء الوثائق.")
