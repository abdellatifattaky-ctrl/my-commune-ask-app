if st.button("🚀 إنشاء المحضر"):
    if data.empty:
        st.error("الرجاء إدخال بيانات الشركات!")
    else:
        doc = Document()
        section = doc.sections[0]
        
        # تأكد أن هذا السطر والأسطر التالية تبدأ بنفس عدد المسافات (4 مسافات عادة)
        header = section.header 
        htable = header.add_table(1, 3, Inches(7))
        # استمر في كتابة بقية الكود بنفس مستوى الإزاحة...
