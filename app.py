elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية SMART PRO+</div>', unsafe_allow_html=True)

    # 1. تعريف الدوال (Functions)
    def init_procurement_smart_tables():
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS market_master_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                market_object TEXT,
                estimate_amount REAL,
                created_at TEXT
            )
        """)
        # ... يمكنك إضافة باقي الجداول هنا بنفس النمط ...
        conn.commit()
        conn.close()

    def get_market_refs():
        rows = fetch_all("SELECT DISTINCT market_ref FROM market_master_data WHERE market_ref IS NOT NULL")
        return [r["market_ref"] for r in rows]

    def get_market_data(market_ref):
        rows = fetch_all("SELECT * FROM market_master_data WHERE market_ref = ? LIMIT 1", (market_ref,))
        return rows[0] if rows else None

    # 2. تشغيل التأسيس (Execution)
    # تأكد أن هذا السطر على نفس مستوى 'def'
    init_procurement_smart_tables()

    # 3. واجهة المستخدم (UI)
    # تأكد أن 'tabs' تبدأ بنفس مستوى 'init_procurement...'
    tabs = st.tabs(["➕ صفقة جديدة", "📄 إصدار الوثائق"])

    with tabs[0]:
        st.subheader("تسجيل بيانات الصفقة")
        with st.form("new_market"):
            m_ref = st.text_input("رقم الصفقة")
            m_obj = st.text_area("الموضوع")
            m_est = st.number_input("التقدير المالي", min_value=0.0)
            btn = st.form_submit_button("حفظ")
            if btn:
                # استدعاء دالة الحفظ هنا
                st.success(f"تم تسجيل الصفقة {m_ref}")

    with tabs[1]:
        st.subheader("تحميل الملفات")
        refs = get_market_refs()
        if refs:
            selected = st.selectbox("اختر رقم الصفقة", refs)
            if st.button("توليد ملف PV1"):
                # هنا تستدعي دالة generate_pv1_docx التي كتبناها سابقاً
                st.info("جاري تحضير الملف...")
        else:
            st.warning("لا توجد صفقات مسجلة.")
