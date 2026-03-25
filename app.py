import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor
from io import BytesIO
from datetime import date

# --- 1. ترويسة رسمية مفصلة ---
def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(7.0))
    # اليمين (عربي) - الكتابة الرسمية
    c_ar = htable.rows[0].cells[1].paragraphs[0]
    c_ar.text = "المملكة المغربية\nوزارة الداخلية\nإقليم تارودانت\nدائرة تاليون\nجماعة أسكاون\nالكتابة العامة"
    c_ar.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # اليسار (فرنسي)
    c_fr = htable.rows[0].cells[0].paragraphs[0]
    c_fr.text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nPROVINCE DE TAROUDANT\nCOMMUNE D'ASKAOUN"
    c_fr.alignment = WD_ALIGN_PARAGRAPH.LEFT

# --- 2. واجهة الإدارة (RTL) ---
st.set_page_config(page_title="منظومة تسيير دورات أسكاون", layout="wide")
st.markdown("""<style> .main { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

if 'members_list' not in st.session_state:
    st.session_state.members_list = ["السيد(ة) العضو الأول", "السيد(ة) العضو الثاني"]

st.title("🏛️ منصة صياغة المحاضر الكبرى والتقارير المالية")

tab1, tab2 = st.tabs(["📝 تحرير المحضر التفصيلي", "👥 قاعدة بيانات المجلس"])

with tab2:
    st.subheader("⚙️ إدارة أعضاء المجلس الجماعي")
    all_names = st.text_area("أدخل اللائحة (اسم في كل سطر):", value="\n".join(st.session_state.members_list), height=200)
    if st.button("حفظ اللائحة"):
        st.session_state.members_list = [n.strip() for n in all_names.split('\n') if n.strip()]
        st.success("تم التحيين.")

with tab1:
    # معلومات الجلسة
    col_info, col_attendance = st.columns([1, 2])
    with col_info:
        sess_kind = st.selectbox("نوع الدورة", ["العادية", "الاستثنائية"])
        sess_month = st.text_input("برسم شهر/سنة", "مارس 2026")
        sess_date = st.text_input("تاريخ الدورة", "الأربعاء 25 مارس 2026")
        pres_name = st.text_input("رئيس المجلس", "أدخل الاسم")
        auth_name = st.text_input("ممثل السلطة", "السيد القائد")
        sec_name = st.text_input("كاتب المجلس", "أدخل الاسم")

    with col_attendance:
        st.write("✅ **حالة الحضور والغياب**")
        attendance_df = pd.DataFrame({"اسم العضو": st.session_state.members_list, "الوضعية": ["حاضر"] * len(st.session_state.members_list)})
        edited_attendance = st.data_editor(attendance_df, use_container_width=True)

    presents = edited_attendance[edited_attendance["الوضعية"] == "حاضر"]["اسم العضو"].tolist()
    excused = edited_attendance[edited_attendance["الوضعية"] == "غائب بعذر"]["اسم العضو"].tolist()
    absents = edited_attendance[edited_attendance["الوضعية"] == "غائب بدون عذر"]["اسم العضو"].tolist()

    st.divider()
    st.subheader("📊 تفاصيل النقط المدرجة (المناقشات والبيانات المالية)")
    
    # هيكل البيانات لزيادة عدد الصفحات
    if 'agenda_data' not in st.session_state:
        st.session_state.agenda_data = pd.DataFrame([
            {
                "النقطة": "المصادقة على تحويل اعتمادات بميزانية التسيير", 
                "المقرر": "رئيس لجنة الميزانية", 
                "تقرير_اللجنة": "تلاوة التقرير المفصل للجنة المالية الذي أكد على ضرورة تحويل مبلغ (...) لتغطية مصاريف (...)", 
                "المناقشة_الموسعة": "عرفت القاعة نقاشاً حاداً حول أوجه الصرف، حيث تساءل العضو فلان عن الجدوى من هذا التحويل، ليرد السيد الرئيس موضحاً أن...", 
                "بيانات_مالية": "البرنامج 10: 50.000 درهم | المشروع 20: 30.000 درهم",
                "القرار": "صادق المجلس بالإجماع"
            }
        ])

    final_agenda = st.data_editor(st.session_state.agenda_data, num_rows="dynamic", use_container_width=True)

    # --- محرك التوليد "الطويل" ---
    if st.button("📄 توليد المحضر الإداري المطول (Word)"):
        doc = Document()
        # تنسيق الفقرة للعربية
        def write_ar(text, bold=False, size=12, align='right'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if align == 'right' else WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            run.font.name = 'Arial'
            run.font.size = Pt(size)
            run.bold = bold
            return p

        add_askaouen_header(doc)

        # ديباجة المحضر (الصفحة 1)
        write_ar("محضر اجتماع دورة المجلس الجماعي لأسكاون", bold=True, size=16, align='center')
        write_ar(f"الدورة {sess_kind} لبرسم شهر {sess_month}", bold=True, size=14, align='center')
        
        write_ar("\nبناء على مقتضيات القانون التنظيمي رقم 113.14 المتعلق بالجماعات الصادر بتنفيذه الظهير الشريف رقم 1.15.85 بتاريخ 20 من رمضان 1436 (7 يوليو 2015)؛")
        write_ar("وبناء على مقتضيات النظام الداخلي للمجلس الجماعي لأسكاون الذي يحدد كيفيات تسيير أشغال المجلس وتدوين محاضر الجلسات؛")
        
        write_ar(f"\nفي يوم {sess_date}، على الساعة العاشرة صباحاً، انعقدت بقاعة الاجتماعات بمقر الجماعة جلسة عمومية في إطار الدورة {sess_kind}، ترأس أشغالها السيد {pres_name} رئيس المجلس، وبحضور السيد {auth_name} ممثلاً للسلطة المحلية.")

        write_ar("\nأولاً: التحقق من النصاب القانوني", bold=True, size=13)
        write_ar(f"افتتح السيد الرئيس الجلسة بكلمة ترحيبية، وبعد التأكد من توفر النصاب القانوني طبقاً للمادة 42 من القانون التنظيمي (حضور {len(presents)} أعضاء من أصل {len(st.session_state.members_list)})، أعلن عن انطلاق المداولات.")
        
        # تفصيل الحضور
        write_ar("قائمة الأعضاء الحاضرين:", bold=True)
        write_ar("، ".join(presents), size=11)

        # جدول الأعمال (الصفحة 2)
        doc.add_page_break()
        write_ar("\nثانياً: جدول أعمال الدورة", bold=True, size=13)
        for idx, row in final_agenda.iterrows():
            write_ar(f"النقطة {idx+1}: {row['النقطة']}")

        # المداولات (الصفحات 3 إلى 7)
        doc.add_page_break()
        write_ar("\nثالثاً: تفاصيل المداولات والقرارات المتخذة", bold=True, size=13)
        
        for idx, row in final_agenda.iterrows():
            write_ar(f"دراسة ومناقشة النقطة {idx+1}: {row['النقطة']}", bold=True, size=12)
            
            # عرض التقرير
            write_ar("1. عرض تقرير اللجنة المختصة:", bold=True)
            write_ar(str(row['تقرير_اللجنة']), size=11)
            
            # البيانات المالية (إذا وجدت)
            if row['بيانات_مالية']:
                write_ar("2. المعطيات المالية والتقنية المرتبطة بالنقطة:", bold=True)
                # إنشاء جدول داخل الـ Word لزيادة الطول والاحترافية
                table = doc.add_table(rows=1, cols=2)
                table.style = 'Table Grid'
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'البيان / المشروع'
                hdr_cells[1].text = 'المعطيات المالية (درهم)'
                # إضافة البيانات
                for item in str(row['بيانات_مالية']).split('|'):
                    row_cells = table.add_row().cells
                    parts = item.split(':')
                    if len(parts) == 2:
                        row_cells[0].text = parts[0].strip()
                        row_cells[1].text = parts[1].strip()

            # المناقشة
            write_ar("\n3. ملخص المناقشة والمداخلات:", bold=True)
            write_ar(str(row['المناقشة_الموسعة']), size=11)
            
            # التصويت
            write_ar(f"النتيجة النهائية: وبعد عرض النقطة للتصويت العلني، {row['القرار']}.\n")
            doc.add_paragraph("-" * 80).alignment = WD_ALIGN_PARAGRAPH.CENTER

        # الختام
        doc.add_page_break()
        write_ar("\nرابعاً: ختام أشغال الدورة وبرقية الولاء", bold=True, size=13)
        write_ar(f"واختتمت الدورة بتلاوة برقية الولاء والإخلاص المرفوعة إلى السدة العالية بالله جلالة الملك محمد السادس نصره الله، والتي تلاها السيد {sec_name} بصفته كاتباً للمجلس.")

        write_ar(f"\nحُرر بأسكاون في: {date.today()}", align='center')
        write_ar("\nتوقيع كاتب المجلس                          توقيع رئيس المجلس", bold=True)

        bio = BytesIO(); doc.save(bio)
        st.download_button("📥 تحميل المحضر الإداري والمالي المطول", bio.getvalue(), "PV_Askaouen_Full_Report.docx")
