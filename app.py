import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- 1. المحرك المالي (تحويل المبالغ لحروف فرنسية) ---
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

# --- 2. محرك التنسيق الرسمي (الهوية البصرية) ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    # الجانب الفرنسي (يسار)
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.style.font.size = Pt(9)
    # الجانب العربي (يمين)
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_ar.style.font.size = Pt(10)

# --- 3. إعدادات الواجهة الرئيسية ---
st.set_page_config(page_title="نظام جماعة أسكاون المتكامل", layout="wide")
st.sidebar.title("🏛️ بوابة التدبير الرقمي")
st.sidebar.info("جماعة أسكاون - إقليم تارودانت")

# اختيار القسم الرئيسي
main_choice = st.sidebar.radio("اختر القسم العملياتي:", 
                               ["📦 قسم الصفقات العمومية", "📝 قسم أشغال المجلس واللجان"])

# -------------------------------------------------------------------
# القسم الأول: الصفقات العمومية (بنمادجك الحرفية الكاملة)
# -------------------------------------------------------------------
if main_choice == "📦 قسم الصفقات العمومية":
    st.header("إدارة ملفات الصفقات وسندات الطلب")
    doc_type = st.selectbox("المستند المطلوب توليده:", ["Order de Notification", "Order de Commencement"])
    
    col1, col2 = st.columns(2)
    ref = col1.text_input("رقم الصفقة/السند (N° Marché)", "01/ASK/2026")
    company = col2.text_input("اسم المقاولة المستفيدة", "STE EXAMPLE SARL")
    company_addr = col2.text_input("عنوان الشركة", "CASABLANCA")
    amt_ttc = col1.text_input("المبلغ الإجمالي (TTC)", "140000.00")
    proj_desc = st.text_area("موضوع المشروع (Désignation كاملة كما في CPS)")

    if st.button(f"توليد مستند {doc_type} الآن"):
        doc = Document(); add_askaouen_header(doc)
        
        if doc_type == "Order de Notification":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE N° : {ref}\nOBJET : NOTIFICATION DE L’APPROBATION DU MARCHÉ")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}\nAdresse : {company_addr}")
            doc.add_paragraph(f"RÉFÉRENCES : * Marché n° : {ref}\nObjet du Marché : {proj_desc}")
            doc.add_paragraph(f"\nMonsieur le Directeur,\nJ'ai l'honneur de vous notifier l'approbation du marché n° {ref} cité en référence...")
            doc.add_paragraph(f"Montant : {amt_ttc} DH (TTC), soit : {format_money_fr(amt_ttc)}.")
            doc.add_paragraph("\nConformément au décret n° 2-22-431...")

        elif doc_type == "Order de Commencement":
            p = doc.add_paragraph(f"\nORDRE DE SERVICE DE COMMENCEMENT DES TRAVAUX N° : {ref}")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {company}")
            doc.add_paragraph(f"OBJET : Marché n° {ref}\nINTITULÉ DU PROJET : {proj_desc}")
            doc.add_paragraph("\nMonsieur le Directeur,\nConformément aux clauses du CPS... جئت أخبركم ببدء الأشغال...")

        doc.add_paragraph(f"\nFait à Askaouen, le {date.today()}\nLe Président du Conseil Communal").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل ملف الصفقة (Word)", bio.getvalue(), f"{doc_type}.docx")

# -------------------------------------------------------------------
# القسم الثاني: أشغال المجلس (المحضر الحرفي + واجهة المقررين)
# -------------------------------------------------------------------
elif main_choice == "📝 قسم أشغال المجلس واللجان":
    st.header("إدارة دورات المجلس (نموذج 113.14)")
    
    # 1. واجهة جدول الأعمال والمقررين
    st.subheader("📍 جدول الأعمال وتعيين المقررين")
    if 'agenda_df' not in st.session_state:
        st.session_state.agenda_df = pd.DataFrame([
            {"رقم": 1, "النقطة": "المصادقة على ميزانية الجماعة", "المقرر": "أدخل اسم المقرر"},
            {"رقم": 2, "النقطة": "إعادة تخصيص اعتمادات بميزانية التسيير", "المقرر": ""},
        ])
    
    # جدول تفاعلي يسمح للمدير بتعديل النقاط والمقررين مباشرة
    edited_agenda = st.data_editor(st.session_state.agenda_df, num_rows="dynamic", use_container_width=True)
    
    # 2. واجهة الحضور
    st.divider()
    st.subheader("👥 الحضور والغياب")
    c1, c2, c3 = st.columns(3)
    presents_text = c1.text_area("الأعضاء الحاضرون (الاسم والصفة)")
    abs_exc_text = c2.text_area("غائبون بعذر")
    abs_no_text = c3.text_area("غائبون بدون عذر")

    if st.button("📄 توليد المحضر النهائي الشامل"):
        doc = Document(); add_askaouen_header(doc)
        t = doc.add_paragraph("محضر اجتماع دورة المجلس الجماعي")
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True
        
        doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات...")
        
        doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
        # بناء جدول الحضور
        tab_h = doc.add_table(rows=1, cols=3); tab_h.style = 'Table Grid'
        h_cells = tab_h.rows[0].cells
        h_cells[0].text, h_cells[1].text, h_cells[2].text = 'الحاضرون', 'غائبون بعذر', 'غائبون بدون عذر'
        r_cells = tab_h.add_row().cells
        r_cells[0].text, r_cells[1].text, r_cells[2].text = presents_text, abs_exc_text, abs_no_text

        doc.add_paragraph("\nثانياً: المداولات والقرارات (حسب ترتيب المقررين)").bold = True
        # دمج النقاط مع المقررين من الجدول التفاعلي
        for index, row in edited_agenda.iterrows():
            doc.add_paragraph(f"النقطة {row['رقم']}: {row['النقطة']}").bold = True
            doc.add_paragraph(f"العرض: قدم السيد(ة) {row['المقرر']} بصفته مقرراً لهذه النقطة، تقريراً مفصلاً...")
            doc.add_paragraph("المصادقة: تمت المصادقة [بالإجماع/بالأغلبية] على النقطة.\n")

        doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
        doc.add_paragraph("اختتمت الجلسة بتلاوة برقية الولاء والإخلاص...")
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر المنسق (Word)", bio.getvalue(), "PV_Askaouen_Full.docx")

st.sidebar.divider()
st.sidebar.caption("نظام أسكاون الذكي v1.0 - 2026")
