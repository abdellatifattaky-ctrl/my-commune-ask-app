import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# دالة التفقيط (الأرقام إلى حروف) بالفرنسية كما في نموذجك
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        # إضافة CTS في النهاية كما طلبت
        text = f"{words} DIRHAMS ,00CTS"
        return text
    except: return "________________"

st.set_page_config(page_title="Système PV - Askaouen", layout="wide")

st.title("🏛️ نظام استخراج المحاضر النهائية - جماعة أسكاون")

# إدخال البيانات للشركة الفائزة
with st.container():
    c1, c2 = st.columns(2)
    winning_company = c1.text_input("اسم الشركة الفائزة (Société):", "DECO GRC")
    final_amount = c2.text_input("المبلغ الإجمالي (Montant TTC):", "93120.00")

if st.button("🚀 توليد محضر الإسناد النهائي"):
    doc = Document()
    # إعدادات الهوامش والترويسة (نفس الكود السابق لضمان الهوية)
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].paragraphs[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].paragraphs[0].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph("\n")
    # النص النهائي المعتمد حرفياً
    amt_in_words = format_to_words_fr(final_amount)
    
    # الفقرة الأولى: التأكد من خطاب التأكيد
    p1 = doc.add_paragraph()
    p1.add_run(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société ").bold = False
    p1.add_run(f"{winning_company} ").bold = True
    p1.add_run(f"a confirmé son offre par lettre de confirmation.").bold = False
    p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # الفقرة الثانية: المصادقة والإسناد (VALIDE et ATTRIBUE)
    p2 = doc.add_paragraph()
    p2.add_run(f"Le président de la commission ").bold = False
    p2.add_run("VALIDE ").bold = True
    p2.add_run("la confirmation et ").bold = False
    p2.add_run("ATTRIBUE ").bold = True
    p2.add_run(f"le bon de commande à la société ").bold = False
    p2.add_run(f"{winning_company} ").bold = True
    p2.add_run(f"pour un montant de : ").bold = False
    p2.add_run(f"{final_amount} ").bold = True
    p2.add_run(f"Dhs TTC ({amt_in_words}).").bold = True
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # التاريخ والتوقيعات
    doc.add_paragraph(f"\nAskaouen le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO(); doc.save(bio)
    st.download_button("📥 تحميل محضر الإسناد النهائي (Word)", bio.getvalue(), "PV_Attribution_Final.docx")
    st.success("تم توليد المحضر بالأمانة النصية المطلوبة.")
