import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from io import BytesIO
from datetime import date

# --- 1. الترويسة الرسمية ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nدائرة تاليون\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT

# --- 2. إعدادات الواجهة ---
st.set_page_config(page_title="منظومة تدبير محاضر الدورات", layout="wide")
st.markdown("""<style> .main { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

if 'members_list' not in st.session_state:
    st.session_state.members_list = ["العضو 1", "العضو 2", "العضو 3"]

st.title("🏛️ النظام المعلوماتي لتدوين وقائع جلسات المجلس")

tab1, tab2 = st.tabs(["📝 تحرير محضر الدورة", "👥 إدارة أعضاء المجلس"])

with tab2:
    st.subheader("⚙️ إدارة الهيئة الناخبة للمجلس")
    all_names = st.text_area("أدخل أسماء أعضاء المجلس (اسم واحد في كل سطر):", 
                             value="\n".join(st.session_state.members_list), height=250)
    if st.button("حفظ وتحيين اللائحة"):
        st.session_state.members_list = [n.strip() for n in all_names.split('\n') if n.strip()]
        st.success("تم تحيين قاعدة بيانات الأعضاء بنجاح.")

with tab1:
    st.subheader("📍 ضبط وقائع الجلسة")
    col_info, col_attendance = st.columns([1, 2])
    
    with col_info:
        sess_kind = st.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
        sess_month = st.text_input("برسم شهر/سنة", "مارس 2026")
        sess_date = st.text_input("تاريخ انعقاد الجلسة", "الأربعاء 25 مارس 2026")
        pres_name = st.text_input("رئيس الجلسة", "السيد رئيس المجلس الجماعي")
        auth_name = st.text_input("ممثل السلطة", "السيد قائد قيادة أسكاون")
        sec_name = st.text_input("كاتب المجلس", "السيد كاتب المجلس")

    with col_attendance:
        st.write("✅ **حالة الحضور والغياب**")
        attendance_df = pd.DataFrame({"اسم العضو": st.session_state.members_list, "الوضعية": ["حاضر"] * len(st.session_state.members_list)})
        edited_attendance = st.data_editor(attendance_df, use_container_width=True,
                                          column_config={"الوضعية": st.column_config.SelectboxColumn("الوضعية", options=["حاضر", "غائب بعذر", "غائب بدون عذر"])})

    presents = edited_attendance[edited_attendance["الوضعية"] == "حاضر"]["اسم العضو"].tolist()
    excused = edited_attendance[edited_attendance["الوضعية"] == "غائب بعذر"]["اسم العضو"].tolist()
    absents = edited_attendance[edited_attendance["الوضعية"] == "غائب بدون عذر"]["اسم العضو"].tolist()

    st.divider()
    st.write("⚖️ **جدول الأعمال ومسار المداولات**")
    vote_choices = ["صادق المجلس بالإجماع", "صادق المجلس بالأغلبية", "قرر المجلس تأجيل البت في النقطة"]
    
    if 'agenda_data' not in st.session_state:
        st.session_state.agenda_data = pd.DataFrame([{"النقطة": "موضوع النقطة الأولى", "المقرر": "", "النتيجة": "صادق المجلس بالإجماع", "ملخص_المناقشة": ""}])

    final_agenda = st.data_editor(st.session_state.agenda_data, num_rows="dynamic", use_container_width=True,
                                 column_config={"النتيجة": st.column_config.SelectboxColumn("مآل النقطة", options=vote_choices)})

    # --- 3. توليد المحضر (تم تصحيح الأخطاء البرمجية هنا) ---
    if st.button("📄 توليد المحضر الرسمي النهائي"):
        try:
            doc = Document(); add_askaouen_header(doc)
            
            # العنوان
            t = doc.add_paragraph(f"محضر اجتماع دورة المجلس الجماعي لأسكاون\nالدورة {sess_kind} برسم شهر {sess_month}")
            t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True

            doc.add_paragraph("\nبناءً على القانون التنظيمي رقم 113.14 المتعلق بالجماعات.")
            doc.add_paragraph(f"انعقدت بقاعة الاجتماعات بمقر الجماعة، يوم {sess_date}، جلسة عمومية تحت رئاسة السيد {pres_name}، وبحضور السيد {auth_name} بصفته ممثلاً للسلطة المحلية.")

            doc.add_paragraph("\nأولاً: الحضور والغياب").bold = True
            doc.add_paragraph(f"• الحاضرون ({len(presents)}): " + "، ".join(presents))
            if excused: doc.add_paragraph(f"• الغائبون بعذر ({len(excused)}): " + "، ".join(excused))
            if absents: doc.add_paragraph(f"• الغائبون بدون عذر ({len(absents)}): " + "، ".join(absents))

            doc.add_paragraph("\nثانياً: المداولات والقرارات المتخذة").bold = True
            for idx, row in final_agenda.iterrows():
                doc.add_paragraph(f"النقطة {idx+1}: {row['النقطة']}").bold = True
                doc.add_paragraph(f"العرض: قدم السيد(ة) {row['المقرر']} عرضاً حول الموضوع.")
                if row['ملخص_المناقشة']:
                    doc.add_paragraph(f"المناقشة: {row['ملخص_المناقشة']}")
                doc.add_paragraph(f"القرار: {row['النتيجة']}.\n")

            doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
            doc.add_paragraph("اختتمت الجلسة بتلاوة برقية الولاء والإخلاص المرفوعة للسدة العالية بالله جلالة الملك محمد السادس نصره الله وأيده.")
            
            doc.add_paragraph(f"\nحُرر بأسكاون في: {date.today()}")

            bio = BytesIO(); doc.save(bio)
            st.download_button("📥 اضغط هنا لتحميل المحضر (Word)", bio.getvalue(), "PV_Official_Askaouen.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            st.success("تم تجهيز المحضر بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء التوليد: {e}")
