import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from io import BytesIO
from datetime import date
from num2words import num2words

# 1. دالة تحويل المبالغ إلى حروف بالفرنسية
def format_to_words_fr(amount_str):
    """تحويل الرقم إلى نص فرنسي كبير (UPPERCASE) مع إضافة السنتيمات"""
    try:
        # تنظيف النص من الفراغات أو الفواصل
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        
        # استخراج السنتيمات
        cents = int(round((val - int(val)) * 100))
        
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ET ZERO CENTIMES"
        return text
    except Exception as e:
        return "________________"

# إعدادات الصفحة
st.set_page_config(page_title="Askaouen - Attribution Pro", layout="wide")

# --- الواجهة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("👥 لجنة فتح الأظرفة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")
    st.info("قم بتعديل أسماء أعضاء اللجنة هنا لتظهر في المحضر.")

# --- واجهة البيانات الرئيسية ---
st.title("🏛️ محضر الإسناد النهائي - جماعة أسكاون")

with st.expander("📝 تفاصيل سند الطلب (Bon de Commande)", expanded=True):
    c1, c2, c3 = st.columns(3)
    num_bc = c1.text_input("N° BC", "03/ASK/2025")
    date_pub = c2.date_input("Date de Publication", date(2025, 4, 17))
    reunion_date = c3.date_input("Date de la Réunion", date(2025, 4, 22))
    obj_bc = st.text_area("Objet", "LEVÉ TOPOGRAPHIQUE")

with st.expander("🏆 الشركة الفائزة (Attributaire)", expanded=True):
    col_a, col_b = st.columns(2)
    winner_name = col_a.text_input("Nom de la société", "MAPTOPO")
    winner_amount = col_b.text_input("Montant TTC (Ex: 15348.00)", "15348.00")

# --- توليد المستند ---
if st.button("🚀 توليد محضر الإسناد النهائي"):
    doc = Document()
    
    # تحسين إعدادات الخط الافتراضي للمستند
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)

    # أ. الترويسة الرسمية (Header) باستخدام جدول مخفي
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6))
    
    # الجهة اليمنى (بالفرنسية)
    c_fr = htable.rows[0].cells[0]
    p_fr = c_fr.paragraphs[0]
    p_fr.add_run("ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN").bold = True
    
    # الجهة اليسرى (بالعربية)
    c_ar = htable.rows[0].cells[1]
    p_ar = c_ar.paragraphs[0]
    p_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ar.add_run("المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون").bold = True

    # ب. العنوان الرئيسي
    doc.add_paragraph("\n")
    title = doc.add_heading("Procès-verbal d'attribution", 1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # ج. نص الموضوع
    obj_p = doc.add_paragraph()
    obj_p.add_run("Objet : ").bold = True
    obj_p.add_run(obj_bc)
    
    # د. نص المحضر (Paragraph 1: الأعضاء)
    p1 = doc.add_paragraph()
    p1.add_run(f"Le {reunion_date.strftime('%d/%m/%Y')} à 13h00mn, la commission d’ouverture des plis composée comme suit :\n").italic = True
    p1.add_run(f"  -  {p_name} : Président de la commission\n")
    p1.add_run(f"  -  {d_name} : Directeur du service\n")
    p1.add_run(f"  -  {t_name} : Technicien de la commune\n")
    
    # هـ. نص المحضر (Paragraph 2: المرجع القانوني)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    text_2 = (f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission "
              f"d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : "
              f"{date_pub.strftime('%d/%m/%Y')} sur le portail des marchés publics, en application des dispositions "
              f"de l'article 91 du décret n° 2-22-431 (8 mars 2023) relatif aux marchés publics.")
    p2.add_run(text_2)
    
    # و. قرار الإسناد
    amt_words = format_to_words_fr(winner_amount)
    p3 = doc.add_paragraph()
    p3.add_run(f"\nAprès vérification, la commission d’ouverture des plis constate que la société : {winner_name} "
               f"a confirmé son offre par lettre de confirmation.\n")
    
    # الإسناد النهائي بخط عريض
    p4 = doc.add_paragraph()
    final_text = (f"Le président de la commission valide la confirmation et attribue le bon de commande à la société "
                  f"{winner_name} pour un montant de : {winner_amount} Dhs TTC ({amt_words}).")
    run_final = p4.add_run(final_text)
    run_final.bold = True
    run_final.font.size = Pt(13)

    # ز. التوقيعات (بشكل مبسط)
    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # تصدير الملف
    bio = BytesIO()
    doc.save(bio)
    st.download_button(
        label="📥 تحميل المحضر النهائي (Word)",
        data=bio.getvalue(),
        file_name=f"PV_Attribution_{winner_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    st.success("✅ تم إنشاء المستند بنجاح!")
