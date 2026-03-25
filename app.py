# --- إضافة الشعار في الهيدر ---
        header = section.header
        htable = header.add_table(1, 3, Inches(7)) # جعلنا الجدول 3 أعمدة (يمين، وسط، يسار)
        htable.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # العمود الأول: النص الفرنسي
        htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
        htable.rows[0].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # العمود الثاني: الشعار (Logo)
        try:
            logo_cell = htable.rows[0].cells[1]
            logo_path = "logo.png" # تأكد من وجود ملف الصورة في نفس مجلد الكود
            paragraph = logo_cell.paragraphs[0]
            run = paragraph.add_run()
            run.add_picture(logo_path, width=Cm(1.8)) # تحجيم الشعار بـ 1.8 سم
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            st.warning("⚠️ لم يتم العثور على ملف logo.png، سيتم إنشاء المحضر بدون شعار.")

        # العمود الثالث: النص العربي
        cell_ar = htable.rows[0].cells[2]
        p_ar = cell_ar.paragraphs[0]
        p_ar.text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
        p_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
