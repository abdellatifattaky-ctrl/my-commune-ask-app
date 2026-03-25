import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date
from num2words import num2words

# --- دالة تحويل المبالغ المالية إلى حروف فرنسية ---
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

# --- دالة الترويسة الرسمية للجماعة ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(1.5), Cm(1.5)
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- واجهة التطبيق الرئيسية ---
st.set_page_config(page_title="منصة تدبير جماعة أسكاون", layout="wide")
st.title("🏛️ نظام التدبير الإداري الرقمي - جماعة أسكاون")

menu = st.sidebar.radio("القائمة الرئيسية:", ["📦 الصفقات العمومية", "📝 أشغال المجلس واللجان"])

# ---------------------------------------------------------
# 1. قسم الصفقات العمومية (BC / AO)
# ---------------------------------------------------------
if menu == "📦 الصفقات العمومية":
    st.subheader("إدارة المساطر العمومية")
    mode = st.radio("نوع المسطرة:", ["**Bon de Commande**", "**Appel d'Offres (A.O)**"], horizontal=True)
    
    if "**Bon de Commande**" in mode:
        action = st.selectbox("المستند المطلوب:", ["Les PVs (1-5)", "Notification d'Approbation"])
    else:
        action = st.selectbox("المستند المطلوب:", ["Notification d'Approbation", "O.S de Commencement", "PV d'Implantation", "PV de Réception"])

    col1, col2 = st.columns(2)
    ref_num = col1.text_input("رقم الصفقة/السند", "01/ASK/2026")
    comp_name = col2.text_input("اسم المقاولة المستفيدة", "STE XXXXXX SARL")
    amt_num = col1.text_input("المبلغ (TTC)", "140000.00")
    obj_proj = st.text_area("موضوع المشروع (Désignation)", "أدخل موضوع المشروع بدقة...")

    if st.button(f"توليد مستند {action}"):
        doc = Document(); add_askaouen_header(doc)
        
        # --- نموذج Notification (نموذجك الحرفي) ---
        if "Notification" in action:
            p = doc.add_paragraph(f"\nORDRE DE SERVICE N° : {ref_num}\nOBJET : NOTIFICATION DE L’APPROBATION DU MARCHÉ")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {comp_name}")
            doc.add_paragraph(f"RÉFÉRENCES : Marché n° {ref_num}")
            doc.add_paragraph(f"Objet du Marché : {obj_proj}")
            
            txt = f"\nJ'ai l'honneur de vous notifier l'approbation du marché cité في المرجع، بمبلغ إجمالي قدره {amt_num} DH (TTC)، أي بالفرنسية: {format_money_fr(amt_num)}."
            doc.add_paragraph(txt)
            doc.add_paragraph("\nConformément au décret n° 2-22-431...")

        # --- نموذج Commencement (نموذجك الحرفي) ---
        elif "Commencement" in action:
            p = doc.add_paragraph(f"\nORDRE DE SERVICE DE COMMENCEMENT DES TRAVAUX N° : {ref_num}")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].bold = True
            doc.add_paragraph(f"\nÀ Monsieur le Directeur de l’entreprise : {comp_name}")
            doc.add_paragraph(f"OBJET : {obj_proj}")
            doc.add_paragraph(f"En ma qualité de Maître d’Ouvrage, j'ai l'honneur de vous notifier l'ordre de commencer l’exécution des travaux...")

        # تذييل التوقيع
        doc.add_paragraph(f"\nFait à ASKAOUN, le {date.today()}")
        doc.add_paragraph("Le Président du Conseil Communal").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المستند (Word)", bio.getvalue(), f"{action}.docx")

# ---------------------------------------------------------
# 2. قسم أشغال المجلس (نموذجك الحرفي)
# ---------------------------------------------------------
elif menu == "📝 أشغال المجلس واللجان":
    st.subheader("محاضر الدورات واللجان")
    doc_type = st.selectbox("نوع الوثيقة:", ["محضر دورة المجلس", "استدعاء عضو", "محضر لجنة"])
    
    if doc_type == "محضر دورة المجلس":
        sess_type = st.selectbox("نوع الدورة:", ["عادية", "استثنائية"])
        sess_month = st.text_input("شهر الدورة", "فبراير 2026")
        
        st.info("👥 تسجيل الحضور")
        c1, c2, c3 = st.columns(3)
        pres_list = c1.text_area("الحاضرون (اسم في كل سطر)")
        exc_list = c2.text_area("الغائبون بعذر")
        no_exc_list = c3.text_area("الغائبون بدون عذر")
        
        st.info("📍 جدول الأعمال والمداولات")
        points_input = st.text_area("أدخل النقاط (نقطة في كل سطر)")
        
        if st.button("توليد المحضر الكامل"):
            doc = Document(); add_askaouen_header(doc)
            title = doc.add_paragraph(f"محضر اجتماع دورة المجلس {sess_type}\nلشهر {sess_month}")
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER; title.runs[0].bold = True
            
            doc.add_paragraph(f"\nبناءً على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات...")
            
            # جدول الحضور (كما طلبت)
            doc.add_paragraph("أولاً: الحضور والغياب").bold = True
            table = doc.add_table(rows=1, cols=3); table.style = 'Table Grid'
            hdr = table.rows[0].cells
            hdr[0].text = 'الحاضرون'; hdr[1].text = 'غائبون بعذر'; hdr[2].text = 'غائبون بدون عذر'
            r = table.add_row().cells
            r[0].text = pres_list; r[1].text = exc_list; r[2].text = no_exc_list
            
            # جدول الأعمال
            doc.add_paragraph("\nثانياً: جدول الأعمال").bold = True
            for i, p in enumerate(points_input.split('\n')):
                doc.add_paragraph(f"{i+1}. {p}")
            
            # المداولات (نظام التصويت)
            doc.add_paragraph("\nثالثاً: المداولات والقرارات").bold = True
            doc.add_paragraph("تمت المصادقة بالإجماع/الأغلبية على النقاط المذكورة...")
            
            doc.add_paragraph(f"\nحُرر بأسكاون في: {date.today()}")
            doc.add_paragraph("توقيع رئيس المجلس الجماعي").alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            bio = BytesIO(); doc.save(bio)
            st.download_button("📥 تحميل محضر الدورة", bio.getvalue(), "PV_Session_Askaouen.docx")

st.sidebar.divider()
st.sidebar.caption("جماعة أسكاون - 2026")
