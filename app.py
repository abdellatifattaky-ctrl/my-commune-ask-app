elif doc_type == "Note d'Identification":
    # (الكود السابق الخاص بـ Note d'Identification)
    pass

elif doc_type == "Ordre de Notification": # الإضافة الجديدة هنا
    winner = st.selectbox("Sélectionner l'attributaire (المقاول):", data['Nom'])
    notif_date = st.date_input("Date de Notification", date.today())
    
    if st.button("🚀 Générer Ordre de Notification"):
        doc = Document()
        create_header(doc)
        
        # العنوان
        title = doc.add_heading("LETTRE DE NOTIFICATION", 1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # المرسل إليه
        p_dest = doc.add_paragraph(f"\nÀ Monsieur le Gérant de la société : {winner}")
        p_dest.bold = True
        p_dest.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # الموضوع
        doc.add_paragraph(f"Objet : Notification de l’approbation du Bon de Commande n° {num_bc}")
        doc.add_paragraph(f"Réf : Avis d’achat publié le {date_pub.strftime('%d/%m/%Y')}")

        # نص التبليغ (الأمانة النصية)
        p_body = doc.add_paragraph(f"\nJ’ai l’honneur de vous informer que le bon de commande n° {num_bc} relatif à : « {obj_bc} », a été dûment approuvé et visé par les services de la Commune d’Askaouen.")
        p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        doc.add_paragraph("Par conséquent, je vous invite à prendre attache avec nos services administratifs pour le retrait de votre exemplaire original et pour entamer les procédures d’exécution conformément aux délais réglementaires.")

        doc.add_paragraph("\nVeuillez agréer, Monsieur le Gérant, l’expression de mes salutations distinguées.")

        # التوقيع
        doc.add_paragraph(f"\nFait à Askaouen, le {notif_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph(f"\nLe Président de la Commune d’Askaouen\n{p_name}").alignment = WD_ALIGN_PARAGRAPH.CENTER

        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل Lettre de Notification", bio.getvalue(), "Notification_Askaouen.docx")
