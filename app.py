import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date

# --- دالة التنسيق الرسمي ---
def add_official_header(doc):
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(2), Cm(2)
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.style.font.size = Pt(9)
    
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_ar.style.font.size = Pt(10)

# --- واجهة التطبيق ---
st.set_page_config(page_title="نظام تدبير جماعة أسكاون", layout="wide")

# --- الهيكل التنظيمي ---
st.sidebar.title("🏛️ منصة التدبير الرقمي")
category = st.sidebar.radio("القسم الرئيسي:", ["الصفقات العمومية", "أشغال المجلس"])

# --- 1. قسم الصفقات العمومية ---
if category == "الصفقات العمومية":
    st.header("📦 إدارة الطلبيات والصفقات")
    mode = st.radio("نوع المسطرة:", ["**Bon de Commande**", "**Appel d'Offres (A.O)**"], horizontal=True)
    
    if "**Bon de Commande**" in mode:
        action = st.selectbox("المستند المطلوب (BC):", ["Les PVs", "Notification"])
    else:
        action = st.selectbox("المستند المطلوب (A.O):", 
                              ["Les PV d'ouverture", "PV d'implantation", "OS Notification", 
                               "Commencement", "Arret", "Reprise", "PV de Réception"])

    col1, col2 = st.columns(2)
    ref = col1.text_input("رقم السند/الصفقة", "01/ASK/2026")
    company = col2.text_input("المقاولة المستفيدة", "STE EXAMPLE SARL")
    amt = col1.text_input("المبلغ (TTC)", "140000.00")
    obj = st.text_area("موضوع المشروع", "أدخل تفاصيل المشروع هنا...")

    if st.button(f"توليد مستند {action}"):
        doc = Document(); add_official_header(doc)
        
        # العنوان المركزي
        title = doc.add_paragraph()
        run = title.add_run(f"\n{action.upper()}")
        run.bold = True; run.font.size = Pt(16)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Réf: {ref}").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nObjet : {obj}").bold = True
        
        # نصوص النماذج الذكية
        if action == "Notification":
            doc.add_paragraph(f"\nJ'ai l'honneur de vous informer que votre offre concernant le bon de commande N°{ref} a été retenue pour un montant de {amt} DHS TTC.")
            doc.add_paragraph("\nEn conséquence, vous êtes invité à vous présenter au siège de la commune pour signer les documents nécessaires.")
        
        elif action == "Commencement":
            doc.add_paragraph("\nORDRE DE SERVICE DE COMMENCEMENT DES TRAVAUX")
            doc.add_paragraph(f"Il est ordonné à l'entreprise {company} de commencer l'exécution des travaux objet du marché sus-indiqué à compter de la date de notification du présent ordre de service.")
            doc.add_paragraph(f"Le délai d'exécution commence à courir à partir de cette date.")

        elif action == "Arret":
            doc.add_paragraph("\nORDRE DE SERVICE D'ARRÊT DES TRAVAUX")
            doc.add_paragraph(f"En raison de [Préciser le motif : intempéries / raisons techniques], il est ordonné à l'entreprise {company} d'arrêter les travaux à compter du {date.today()}.")

        elif action == "PV de Réception":
            doc.add_paragraph("\nPROCES-VERBAL DE RECEPTION PROVISOIRE")
            doc.add_paragraph(f"L'an {date.today().year}, le {date.today()}, la commission s'est rendue sur les lieux pour constater l'achèvement des travaux...")
            doc.add_paragraph("Après examen, la commission déclare la réception provisoire sans réserves.")

        # التوقيعات
        p_sign = doc.add_paragraph(f"\nFait à Askaouen, le {date.today()}")
        p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("\nSigné : Le Président de la Commune")

        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل الملف الآن", bio.getvalue(), f"{action}.docx")

# --- 2. قسم أشغال المجلس ---
elif category == "أشغال المجلس":
    st.header("📝 دورات المجلس الجماعي")
    session_type = st.selectbox("نوع الدورة", ["الدورة العادية لشهر فبراير", "الدورة العادية لشهر ماي", "الدورة العادية لشهر أكتوبر", "دورة استثنائية"])
    session_date = st.date_input("تاريخ الاجتماع")
    
    st.subheader("👥 سجل الحضور والغياب")
    c1, c2, c3 = st.columns(3)
    presents = c1.text_area("الأعضاء الحاضرون (اسم في كل سطر)")
    abs_exc = c2.text_area("الغائبون بعذر")
    abs_no_exc = c3.text_area("الغائبون بدون عذر")
    
    points = st.text_area("نقاط جدول الأعمال")

    if st.button("توليد محضر الدورة الكامل"):
        doc = Document(); add_official_header(doc)
        t = doc.add_paragraph(f"محضر اجتماع {session_type}"); t.bold = True
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"\nبناءً على القانون التنظيمي 113.14 المتعلق بالجماعات، اجتمع المجلس الجماعي لأسكاون في دورة {session_type} بتاريخ {session_date}...")
        
        # جدول الحضور
        doc.add_paragraph("\n1. لائحة الحضور :").bold = True
        tab = doc.add_table(rows=1, cols=3); tab.style = 'Table Grid'
        hdr = tab.rows[0].cells
        hdr[0].text = 'الحاضرون'; hdr[1].text = 'غائبون (عذر)'; hdr[2].text = 'غائبون (بدون عذر)'
        row = tab.add_row().cells
        row[0].text = presents; row[1].text = abs_exc; row[2].text = abs_no_exc
        
        doc.add_paragraph("\n2. جدول الأعمال :").bold = True
        for p in points.split('\n'): doc.add_paragraph(f"• {p}")
        
        doc.add_paragraph("\n3. مداولات المجلس :").bold = True
        doc.add_paragraph("بعد المناقشة المستفيضة، صادق المجلس بالإجماع/بالأغلبية على النقاط المذكورة...")

        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر المنسق", bio.getvalue(), "PV_Session_Askaouen.docx")

st.sidebar.divider()
st.sidebar.info("💡 ملاحظة: النصوص مصاغة وفق المعايير الإدارية المغربية.")
