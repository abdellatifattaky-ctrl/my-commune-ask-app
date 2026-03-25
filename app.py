import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, Inches
from io import BytesIO
from datetime import date

# --- 1. تنسيق الترويسة الرسمية ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- 2. إعدادات الواجهة ---
st.set_page_config(page_title="نظام محاضر دورات أسكاون", layout="wide")
st.title("🏛️ المنصة الرقمية لتدوين محاضر المجلس - جماعة أسكاون")

# القائمة الجانبية للمعلومات الأساسية
st.sidebar.header("📋 معطيات الدورة")
sess_kind = st.sidebar.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
sess_month = st.sidebar.text_input("الشهر والسنة", "مارس 2026")
sess_date = st.sidebar.text_input("التاريخ الكامل", "الأربعاء 25 مارس 2026")
sess_time = st.sidebar.text_input("التوقيت", "10:00 صباحاً")

st.sidebar.divider()
st.sidebar.subheader("👥 النصاب القانوني")
total_m = st.sidebar.number_input("الأعضاء المزاولون", value=15)
present_m = st.sidebar.number_input("الحاضرون", value=10)
excused_m = st.sidebar.number_input("غائبون بعذر", value=2)
absent_m = st.sidebar.number_input("غائبون بدون عذر", value=3)

st.sidebar.divider()
pres_name = st.sidebar.text_input("رئيس الجلسة", "السيد رئيس المجلس")
auth_name = st.sidebar.text_input("ممثل السلطة المحلية", "السيد قائد قيادة أسكاون")
sec_name = st.sidebar.text_input("كاتب المجلس", "السيد كاتب المجلس")

# --- 3. جدول الأعمال والمداولات (التصويت والمقررون) ---
st.subheader("📍 جدول الأعمال والمداولات")
st.info("أدخل نقاط الجدول، حدد المقرر، واختر نتيجة التصويت لكل نقطة:")

if 'session_data' not in st.session_state:
    st.session_state.session_data = pd.DataFrame([
        {"النقطة": "المصادقة على اتفاقية الشراكة لقطاع الماء", "المقرر": "أدخل اسم المقرر", "التصويت": "بالإجماع"},
        {"النقطة": "دراسة تحويل اعتمادات ميزانية التسيير", "المقرر": "", "التصويت": "بالأغلبية"},
    ])

vote_options = ["بالإجماع", "بالأغلبية المطلقة", "بالأغلبية النسبية", "رفض التصويت", "تأجيل النقطة"]
edited_df = st.data_editor(
    st.session_state.session_data,
    num_rows="dynamic",
    column_config={
        "التصويت": st.column_config.SelectboxColumn("نتيجة التصويت", options=vote_options, required=True)
    },
    use_container_width=True
)

# --- 4. توليد المحضر الحرفي الكامل ---
if st.button("📄 توليد المحضر الرسمي الكامل"):
    doc = Document(); add_askaouen_header(doc)
    
    # نموذج المحضر الحرفي (كلمة بكلمة كما أعطيتني إياه)
    doc.add_paragraph("الكتابة العامة").alignment = WD_ALIGN_PARAGRAPH.CENTER
    t = doc.add_paragraph(f"محضر اجتماع دورة المجلس {sess_kind}\nلشهر {sess_month}")
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True
    
    doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات، ولاسيما المواد المتعلقة بعقد دورات المجلس وتدوين محاضرها.")
    
    doc.add_paragraph(f"في يوم {sess_date}، على الساعة {sess_time}، عقد مجلس جماعة أسكاون دورته {sess_kind} برسم شهر {sess_month}، وذلك بقاعة الاجتماعات بمقر الجماعة، برئاسة السيد {pres_name}، رئيس المجلس، وبحضور السيد {auth_name} بصفته ممثلاً للسلطة المحلية.")
    
    doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
    doc.add_paragraph("بعد التأكد من توفر النصاب القانوني لعقد الجلسة، افتتح السيد الرئيس الجلسة مرحباً بالحضور، حيث سجل ما يلي:")
    doc.add_paragraph(f"• عدد الأعضاء المزاولين مهامهم: {total_m} عضو(ة).")
    doc.add_paragraph(f"• عدد الأعضاء الحاضرين: {present_m} عضو(ة).")
    doc.add_paragraph(f"• عدد الأعضاء الغائبين بعذر: {excused_m} عضو(ة).")
    doc.add_paragraph(f"• عدد الأعضاء الغائبين بدون عذر: {absent_m} عضو(ة).")
    doc.add_paragraph(f"(تم تكليف السيد {sec_name}، كاتب المجلس، بتدوين وقائع المحضر).")
    
    doc.add_paragraph("\nثانياً: جدول الأعمال").bold = True
    for idx, row in edited_df.iterrows():
        doc.add_paragraph(f"{idx+1}. {row['النقطة']}")

    doc.add_paragraph("\nثالثاً: المداولات والقرارات").bold = True
    for idx, row in edited_df.iterrows():
        p = doc.add_paragraph()
        p.add_run(f"النقطة {idx+1}: {row['النقطة']}").bold = True
        doc.add_paragraph(f"العرض: قدم السيد(ة) {row['المقرر']}، بصفته مقرراً لهذه النقطة، عرضاً مفصلاً حول الحيثيات والأهداف.")
        doc.add_paragraph(f"المناقشة: بعد فتح باب النقاش، أبدى السادة الأعضاء ملاحظاتهم وتوصياتهم.")
        doc.add_paragraph(f"القرار: صادق المجلس {row['التصويت']} على هذه النقطة.\n")

    doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
    doc.add_paragraph("وعند الانتهاء من دراسة ومناقشة كافة النقاط المدرجة بجدول الأعمال، رفعت الجلسة واختتمت بتلاوة برقية الولاء والإخلاص المرفوعة إلى السدة العالية بالله جلالة الملك محمد السادس نصره الله وأيده.")
    
    doc.add_paragraph(f"\nحُرر بأسكاون في: {date.today()}")
    doc.add_paragraph("توقيع كاتب المجلس                      توقيع رئيس المجلس").bold = True

    bio = BytesIO(); doc.save(bio)
    st.download_button("📥 تحميل المحضر الرسمي المكتمل", bio.getvalue(), "PV_Askaouen_Final.docx")
