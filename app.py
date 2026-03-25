import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- 1. دالة التفقيط المالي ---
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

# --- 2. دالة الترويسة الرسمية ---
def add_askaouen_header(doc):
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
category = st.sidebar.radio("اختر القسم العملياتي:", ["📦 قسم الصفقات العمومية", "📝 قسم أشغال المجلس"])

# ---------------------------------------------------------
# القسم الأول: الصفقات العمومية (بنمادجك الحرفية)
# ---------------------------------------------------------
if category == "📦 قسم الصفقات العمومية":
    st.header("إدارة الطلبيات والصفقات")
    doc_type = st.selectbox("المستند المطلوب:", ["Order de Notification", "Order de Commencement"])
    
    col1, col2 = st.columns(2)
    ref = col1.text_input("رقم الصفقة/السند", "01/ASK/2026")
    company = col2.text_input("اسم المقاولة المستفيدة", "STE XXXXX SARL")
    amt = col1.text_input("المبلغ الإجمالي (TTC)", "140000.00")
    obj = st.text_area("موضوع المشروع بدقة (Désignation)")

    if st.button(f"توليد مستند {doc_type}"):
        doc = Document(); add_askaouen_header(doc)
        
        if doc_type == "Order de Notification":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE N° : {ref}\nOBJET : NOTIFICATION DE L’APPROBATION DU MARCHÉ")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}")
            doc.add_paragraph(f"RÉFÉRENCES : * Marché n° : {ref}")
            doc.add_paragraph(f"Objet du Marché : {obj}")
            doc.add_paragraph(f"\nMonsieur le Directeur,\nJ'ai l'honneur de vous notifier l'approbation du marché n° {ref}...")
            doc.add_paragraph(f"Montant total : {amt} DH (TTC), soit : {format_money_fr(amt)}.")
        
        elif doc_type == "Order de Commencement":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE DE COMMENCEMENT DES TRAVAUX N° : {ref}")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}")
            doc.add_paragraph(f"INTITULÉ DU PROJET : {obj}")
            doc.add_paragraph("\nMonsieur le Directeur,\nConformément aux clauses du CPS... جئت أخبركم ببدء الأشغال...")

        doc.add_paragraph(f"\nFait à Askaouen, le {date.today()}\nLe Président du Conseil Communal")
        bio = BytesIO(); doc.save(bio); st.download_button("📥 تحميل ملف الصفقات", bio.getvalue(), f"{doc_type}.docx")

# ---------------------------------------------------------
# القسم الثاني: أشغال المجلس (واجهة المقررين والنقاط)
# ---------------------------------------------------------
elif category == "📝 قسم أشغال المجلس":
    st.header("إدارة دورات المجلس واللجان")
    
    st.subheader("📍 جدول الأعمال والمقررون")
    if 'agenda_table' not in st.session_state:
        st.session_state.agenda_table = pd.DataFrame([
            {"رقم": 1, "النقطة": "المصادقة على ميزانية الجماعة", "المقرر": "أدخل اسم المقرر الأول"},
            {"رقم": 2, "النقطة": "إعادة تخصيص اعتمادات", "المقرر": ""},
        ])
    
    edited_agenda = st.data_editor(st.session_state.agenda_table, num_rows="dynamic", use_container_width=True)
    
    st.divider()
    st.subheader("👥 الحضور والغياب")
    c1, c2, c3 = st.columns(3)
    presents = c1.text_area("الحاضرون (الاسم والصفة)")
    abs_exc = c2.text_area("غائبون بعذر")
    abs_no = c3.text_area("غائبون بدون عذر")

    if st.button("📄 توليد محضر الدورة الشامل"):
        doc = Document(); add_askaouen_header(doc)
        title = doc.add_paragraph("محضر اجتماع دورة المجلس الجماعي")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER; title.runs[0].bold = True
        
        doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14...")
        doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
        # جدول الحضور
        tab = doc.add_table(1, 3); tab.style = 'Table Grid'
        h = tab.rows[0].cells
        h[0].text, h[1].text, h[2].text = 'الحاضرون', 'غائبون بعذر', 'غائبون بدون عذر'
        r = tab.add_row().cells
        r[0].text, r[1].text, r[2].text = presents, abs_exc, abs_no

        doc.add_paragraph("\nثانياً: المداولات والقرارات").bold = True
        for idx, row in edited_agenda.iterrows():
            doc.add_paragraph(f"النقطة {row['رقم']}: {row['النقطة']}").bold = True
            doc.add_paragraph(f"العرض: قدم السيد(ة) {row['المقرر']} بصفته مقرراً لهذه النقطة عرضاً...")
            doc.add_paragraph("المصادقة: تمت المصادقة بالإجماع/بالأغلبية.\n")

        doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
        doc.add_paragraph("اختتمت الجلسة بتلاوة برقية الولاء والإخلاص...")
        
        bio = BytesIO(); doc.save(bio); st.download_button("📥 تحميل المحضر النهائي", bio.getvalue(), "PV_Final.docx")
