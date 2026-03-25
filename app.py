import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from io import BytesIO
from datetime import date

# --- 1. تنسيق الترويسة الرسمية ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT

# --- 2. إعدادات الواجهة (RTL) ---
st.set_page_config(page_title="نظام أعضاء جماعة أسكاون", layout="wide")
st.markdown("""<style> .main { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

# --- 3. إدارة قاعدة بيانات الأعضاء (تُحفظ في المتصفح) ---
if 'members_list' not in st.session_state:
    # قائمة افتراضية يمكن للمدير تعديلها
    st.session_state.members_list = ["العضو 1", "العضو 2", "العضو 3"]

st.title("🏛️ تدبير دورات مجلس جماعة أسكاون")

tab1, tab2 = st.tabs(["📝 تسجيل حضور الدورة", "👥 إدارة أعضاء المجلس"])

# --- التبويب الثاني: إدارة الأسماء (تعدل مرة واحدة) ---
with tab2:
    st.subheader("⚙️ ضبط لائحة أعضاء المجلس")
    st.write("أدخل أسماء جميع أعضاء المجلس هنا (اسم واحد في كل سطر). ستبقى هذه الأسماء محفوظة.")
    all_names = st.text_area("قائمة أعضاء المجلس الكاملة:", 
                             value="\n".join(st.session_state.members_list), 
                             height=300)
    if st.button("حفظ القائمة الجديدة"):
        st.session_state.members_list = [n.strip() for n in all_names.split('\n') if n.strip()]
        st.success("تم تحديث قائمة المجلس بنجاح!")

# --- التبويب الأول: تسجيل الحضور والمحضر ---
with tab1:
    st.subheader("📍 تسجيل حضور الدورة والقرارات")
    
    col_info, col_attendance = st.columns([1, 2])
    
    with col_info:
        st.write("📅 **معلومات الجلسة**")
        sess_kind = st.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
        sess_date = st.text_input("تاريخ الانعقاد", "الأربعاء 25 مارس 2026")
        pres_name = st.text_input("رئيس الجلسة", "السيد رئيس المجلس")
        auth_name = st.text_input("ممثل السلطة", "السيد قائد قيادة أسكاون")
        sec_name = st.text_input("كاتب المجلس", "السيد كاتب المجلس")

    with col_attendance:
        st.write("✅ **التأشير على الحضور**")
        # جدول تفاعلي لاختيار حالة كل عضو
        attendance_df = pd.DataFrame({
            "اسم العضو": st.session_state.members_list,
            "الحالة": ["حاضر"] * len(st.session_state.members_list)
        })
        
        status_options = ["حاضر", "غائب بعذر", "غائب بدون عذر"]
        edited_attendance = st.data_editor(
            attendance_df,
            column_config={
                "الحالة": st.column_config.SelectboxColumn("الوضعية", options=status_options, required=True),
                "اسم العضو": st.column_config.TextColumn("اسم العضو", disabled=True)
            },
            use_container_width=True,
            key="attendance_editor"
        )

    # فرز الأسماء آلياً للمحضر
    presents = edited_attendance[edited_attendance["الحالة"] == "حاضر"]["اسم العضو"].tolist()
    excused = edited_attendance[edited_attendance["الحالة"] == "غائب بعذر"]["اسم العضو"].tolist()
    absents = edited_attendance[edited_attendance["الحالة"] == "غائب بدون عذر"]["اسم العضو"].tolist()

    st.divider()
    st.write("⚖️ **جدول الأعمال والقرارات**")
    vote_choices = ["صادق بالإجماع", "صادق بالأغلبية", "تأجيل النقطة"]
    
    if 'agenda_data' not in st.session_state:
        st.session_state.agenda_data = [{"النقطة": "نقطة رقم 1", "المقرر": "", "القرار": "صادق بالإجماع"}]

    final_agenda = st.data_editor(pd.DataFrame(st.session_state.agenda_data), num_rows="dynamic",
                                 column_config={"القرار": st.column_config.SelectboxColumn("القرار", options=vote_choices)},
                                 use_container_width=True)

    # --- توليد المحضر ---
    if st.button("📄 توليد المحضر الرسمي"):
        doc = Document(); add_askaouen_header(doc)
        doc.add_paragraph("الكتابة العامة").alignment = WD_ALIGN_PARAGRAPH.CENTER
        title = doc.add_paragraph(f"محضر اجتماع دورة المجلس {sess_kind}")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER; title.runs[0].bold = True
        
        doc.add_paragraph("\nبناءً على مقتضيات القانون التنظيمي رقم 113.14...")
        doc.add_paragraph(f"في يوم {sess_date}، برئاسة السيد {pres_name}، وبحضور السيد {auth_name}...")

        doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
        doc.add_paragraph(f"• الحاضرون ({len(presents)}): " + "، ".join(presents))
        doc.add_paragraph(f"• الغائبون بعذر ({len(excused)}): " + "، ".join(excused))
        doc.add_paragraph(f"• الغائبون بدون عذر ({len(absents)}): " + "، ".join(absents))
        
        doc.add_paragraph("\nثانياً: المداولات والقرارات").bold = True
        for idx, row in final_agenda.iterrows():
            doc.add_paragraph(f"النقطة {idx+1}: {row['النقطة']}").bold = True
            doc.add_paragraph(f"القرار: بعد المناقشة، {row['القرار']} على هذه النقطة.\n")

        doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
        doc.add_paragraph("اختتمت الجلسة بتلاوة برقية الولاء والإخلاص...")
        
        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل ملف Word المكتمل", bio.getvalue(), "PV_Askaouen.docx")
