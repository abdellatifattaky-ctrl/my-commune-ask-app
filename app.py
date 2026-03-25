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
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nدائرة تاليون\nجماعة أسكاون"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT

# --- 2. إعدادات الواجهة (RTL) ---
st.set_page_config(page_title="منظومة تدبير محاضر الدورات", layout="wide")
st.markdown("""<style> .main { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

if 'members_list' not in st.session_state:
    st.session_state.members_list = ["العضو 1", "العضو 2"]

st.title("🏛️ النظام المعلوماتي لتدوين وقائع جلسات المجلس")

tab1, tab2 = st.tabs(["📝 تحرير محضر الدورة", "👥 تحيين لائحة أعضاء المجلس"])

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
        st.session_state.agenda_data = [{"النقطة": "موضوع النقطة الأولى", "المقرر": "", "القرار": "صادق المجلس بالإجماع", "ملخص_المناقشة": ""}]

    final_agenda = st.data_editor(pd.DataFrame(st.session_state.agenda_data), num_rows="dynamic", use_container_width=True,
                                 column_config={"القرار": st.column_config.SelectboxColumn("مآل النقطة", options=vote_choices),
                                               "ملخص_المناقشة": st.column_config.TextColumn("خلاصة المداولة (اختياري)")})

    # --- توليد المحضر بأسلوب إداري رفيع ---
    if st.button("📄 توليد المحضر الرسمي النهائي"):
        doc = Document(); add_askaouen_header(doc)
        
        # تنسيق الفقرات
        def set_arabic_style(p, bold=False, size=12):
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run = p.runs[0]
            run.bold = bold
            run.font.size = Pt(size)
            run.font.name = 'Arial'

        # العنوان الرئيسي
        t = doc.add_paragraph(f"محضر اجتماع دورة المجلس الجماعي لأسكاون\nالدورة {sess_kind} برسم شهر {sess_month}")
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.runs[0].bold = True; t.runs[0].font.size = Pt(14)

        doc.add_paragraph("\nبناءً على الظهير الشريف رقم 1.15.85 الصادر في 20 من رمضان 1436 (7 يوليو 2015) بتنفيذ القانون التنظيمي رقم 113.14 المتعلق بالجماعات.")
        
        doc.add_paragraph(f"وعملاً بمقتضيات النظام الداخلي للمجلس الجماعي لأسكاون، انعقدت بقاعة الاجتماعات بمقر الجماعة، يوم {sess_date} على الساعة العاشرة صباحاً، جلسة عمومية في إطار الدورة {sess_kind}، وذلك تحت رئاسة السيد {pres_name}، وبحضور السيد {auth_name} بصفته ممثلاً للسلطة المحلية.")

        doc.add_paragraph("\nأولاً: الحضور والغياب والنصاب القانوني").bold = True
        doc.add_paragraph(f"في مستهل الجلسة، تفضل السيد الرئيس بالترحيب بكافة السادة الأعضاء وبالسيد ممثل السلطة المحلية، معلناً بعد ذلك عن توفر النصاب القانوني لمداولة المجلس بشكل صحيح، طبقاً للمادة 42 من القانون التنظيمي 113.14، حيث سجل ما يلي:")
        
        doc.add_paragraph(f"• السادة الأعضاء الحاضرون ({len(presents)}): ").bold = True
        doc.add_paragraph("، ".join(presents))
        
        if excused:
            doc.add_paragraph(f"• السادة الأعضاء الغائبون بعذر ({len(excused)}): ").bold = True
            doc.add_paragraph("، ".join(excused))
        
        if absents:
            doc.add_paragraph(f"• السادة الأعضاء الغائبون بدون عذر ({len(absents)}): ").bold = True
            doc.add_paragraph("، ".join(absents))

        doc.add_paragraph(f"\nوقد عُهد بمهمة كتابة الجلسة وتدوين وقائعها للسيد {sec_name} بصفته كاتباً للمجلس.")

        doc.add_paragraph("\nثانياً: جدول الأعمال وعرض النقاط").bold = True
        doc.add_paragraph("انتقل المجلس بعد ذلك لتدارس النقاط المدرجة في جدول أعمال هذه الدورة، وهي كالتالي:")
        for idx, row in final_agenda.iterrows():
            doc.add_paragraph(f"{idx+1}. {row['النقطة']}")

        doc.add_paragraph("\nثالثاً: تفاصيل المداولات والقرارات المتخذة").bold = True
        for idx, row in final_agenda.iterrows():
            p = doc.add_paragraph()
            p.add_run(f"النقطة {idx+1}: {row['النقطة']}").bold = True
            
            doc.add_paragraph(f"استهلت مناقشة هذه النقطة بعرض قدمه السيد(ة) {row['المقرر']}، استعرض فيه السياق العام للموضوع وأهدافه التنموية.")
            
            if row['ملخص_المناقشة']:
                doc.add_paragraph(f"وعقب ذلك، فُتح باب المناقشة حيث سجل السادة الأعضاء الملاحظات التالية: {row['ملخص_المناقشة']}")
            else:
                doc.add_paragraph("وبعد مناقشة مستفيضة وعميقة شارك فيها السادة الأعضاء بإبداء ملاحظاتهم وتوصياتهم، تبين للمجلس أهمية المصادقة على هذا المقترح.")
            
            doc.add_paragraph(f"وعند عرض النقطة للتصويت العلني، {row['قرار']}.\n")

        doc.add_paragraph("\nرابعاً: ختام الجلسة").bold = True
        doc.add_paragraph("وبعد استنفاذ كافة النقط المدرجة بجدول الأعمال، اختتمت الجلسة في جو من المسؤولية والتعاون، حيث تلا السيد كاتب المجلس برقية الولاء والإخلاص المرفوعة للسدة العالية بالله جلالة الملك محمد السادس نصره الله وأيده، والتمس فيها من الله عز وجل أن يحفظ جلالته والأسرة الملكية الشريفة.")
        
        doc.add_paragraph(f"\nحُرر بأسكاون في: {date.today()}")
        doc.add_paragraph("توقيع كاتب المجلس:                          توقيع رئيس المجلس:").bold = True

        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر الإداري الرفيع", bio.getvalue(), "PV_Official_Askaouen.docx")
