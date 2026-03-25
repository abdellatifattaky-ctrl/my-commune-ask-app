import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة التفقيط المالي بالفرنسية ---
def format_money_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(int(val), lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        return text
    except: return "________________"

# --- دالة الترويسة المزدوجة ---
def add_official_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- واجهة التطبيق ---
st.set_page_config(page_title="منصة جماعة أسكاون", layout="wide")
st.sidebar.title("🏛️ الإدارة الرقمية")
category = st.sidebar.radio("القسم:", ["الصفقات العمومية", "أشغال المجلس"])

# ---------------------------------------------------------
# 1. قسم الصفقات (بنمادجك الحرفية)
# ---------------------------------------------------------
if category == "الصفقات العمومية":
    st.header("📦 إدارة الصفقات (BC / AO)")
    mode = st.radio("النوع:", ["**Bon de Commande**", "**Appel d'Offres (A.O)**"], horizontal=True)
    
    action = st.selectbox("المستند المطلوب:", 
                          ["Order de Notification", "Order de Commencement", "Les PVs"])

    col1, col2 = st.columns(2)
    ref = col1.text_input("رقم الصفقة/السند", "01/ASK/2026")
    company = col2.text_input("اسم المقاولة", "STE EXAMPLE SARL")
    addr = col2.text_input("عنوان الشركة", "CASABLANCA")
    amt = col1.text_input("المبلغ TTC", "140000.00")
    obj = st.text_area("موضوع المشروع")

    if st.button(f"توليد {action}"):
        doc = Document(); add_official_header(doc)
        
        if action == "Order de Notification":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE N° : {ref}\nOBJET : NOTIFICATION DE L’APPROBATION DU MARCHÉ")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}")
            doc.add_paragraph(f"Adresse : {addr}")
            doc.add_paragraph(f"RÉFÉRENCES : * Marché n° : {ref}")
            doc.add_paragraph(f"Objet du Marché : {obj}")
            
            doc.add_paragraph(f"\nMonsieur le Directeur,\nJ'ai l'honneur de vous notifier par la présente, l'approbation du marché n° {ref} cité en référence...")
            doc.add_paragraph(f"Ledit marché a été approuvé... pour un montant total de {amt} DH (TTC), soit en toutes lettres : {format_money_fr(amt)}.")
            doc.add_paragraph("\nConformément aux dispositions du décret n° 2-22-431...")

        elif action == "Order de Commencement":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE DE COMMENCEMENT DES TRAVAUX N° : {ref}\n(O.S de Commencement)")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}")
            doc.add_paragraph(f"OBJET : Marché n° {ref}")
            doc.add_paragraph(f"INTITULÉ DU PROJET : {obj}")
            doc.add_paragraph("\nMonsieur le Directeur,\nConformément aux clauses du CPS... جئت أخبركم ببدء الأشغال...")

        doc.add_paragraph(f"\nFait à Askaouen, le {date.today()}\nLe Président du Conseil Communal")
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المستند", bio.getvalue(), f"{action}.docx")

# ---------------------------------------------------------
# 2. قسم أشغال المجلس (نموذج المحضر الحرفي)
# ---------------------------------------------------------
elif category == "أشغال المجلس":
    st.header("📝 دورات المجلس")
    sess_type = st.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
    sess_month = st.text_input("شهر الدورة")
    sess_year = st.text_input("السنة", "2026")
    
    st.subheader("👥 الحضور والغياب")
    c1, c2, c3 = st.columns(3)
    presents = c1.text_area("الحاضرون")
    abs_exc = c2.text_area("غائبون بعذر")
    abs_no = c3.text_area("غائبون بدون عذر")
    
    points = st.text_area("جدول الأعمال (نقطة في كل سطر)")

    if st.button("توليد محضر الدورة الحرفي"):
        doc = Document(); add_official_header(doc)
        doc.add_paragraph("الكتابة العامة").alignment = WD_ALIGN_PARAGRAPH.CENTER
        t = doc.add_paragraph(f"محضر اجتماع دورة المجلس {sess_type}\nلشهر {sess_month} سنة {sess_year}")
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True
        
        doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات...")
        doc.add_paragraph("أولاً: الحضور والغياب").bold = True
        # (هنا يتم دمج جدول الحضور الذي أرسلته)
        
        doc.add_paragraph("\nثانياً: جدول الأعمال").bold = True
        for p in points.split('\n'): doc.add_paragraph(f"- {p}")
        
        doc.add_paragraph("\nثالثاً: المداولات والقرارات").bold = True
        doc.add_paragraph("صادق المجلس بالإجماع/الأغلبية...")
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر", bio.getvalue(), "PV_Session.docx")
