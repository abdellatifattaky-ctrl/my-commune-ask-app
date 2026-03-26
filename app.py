import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from io import BytesIO
from datetime import date, timedelta
from num2words import num2words

# --- 1. الدوال المساعدة (Engine) ---
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        return f"{num2words(val, lang='fr').upper()} DIRHAMS TTC"
    except: return "________________"

def add_askaouen_header(doc):
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --- 2. إعدادات المنصة ---
st.set_page_config(page_title="مدير مصالح أسكاون - النظام المتكامل", layout="wide")

if 'p_name' not in st.session_state: st.session_state.p_name = "MOHAMED ZILALI"
if 'd_name' not in st.session_state: st.session_state.d_name = "M BAREK BAK"
if 't_name' not in st.session_state: st.session_state.t_name = "ABDELLATIF ATTAKY"

# --- 3. القائمة الجانبية (Sidebar Navigation) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d5/Coat_of_arms_of_Morocco.svg", width=80)
    st.title("إدارة مصالح أسكاون")
    st.divider()
    main_menu = st.radio("القائمة الرئيسية:", [
        "🏠 لوحة القيادة والبريد",
        "🏗️ سندات الطلب (BC)",
        "🏗️ الصفقات العمومية (AO)",
        "👥 الموارد البشرية (RH)",
        "🚜 الحظيرة والآليات",
        "💰 المداخيل والممتلكات",
        "🏛️ الدورات والمقررات"
    ])
    st.divider()
    st.caption("إصدار 2026 - نظام التدبير الموحد")

# --- الوحدة 1: لوحة القيادة والبريد المستعجل ---
if main_menu == "🏠 لوحة القيادة والبريد":
    st.header("📬 المكتب الذكي لمدير المصالح")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("مراسلات مستعجلة", "3", "🔴")
    col_m2.metric("صفقات في طور النشر", "2", "🔵")
    col_m3.metric("ميزانية التسيير المتبقية", "45%", "📉")

    st.subheader("⚠️ تنبيهات المراسلات الواردة")
    with st.expander("🔴 مراسلة من العمالة: إحصاء الموظفين (أجل 48 ساعة)"):
        st.write("رقم الإرسالية: 552/ASK - المصدر: قسم الجماعات الترابية")
        st.button("توجيه لمصلحة الموظفين")
    
    with st.expander("🟠 مراسلة من الخزينة: ملاحظات حول سند طلب"):
        st.write("الموضوع: رفض التأشير على طلب توريد المحروقات")
        st.button("توجيه للمصلحة المالية")

# --- الوحدة 2: سندات الطلب (BC) ---
elif main_menu == "🏗️ سندات الطلب (BC)":
    st.header("🏗️ تدبير سندات الطلب (Bons de Commande)")
    t_bc1, t_bc2 = st.tabs(["📑 إعداد المحاضر", "🖼️ ألبوم الصور التقني"])
    
    with t_bc1:
        num_bc = st.text_input("رقم السند", "01/ASK/2026")
        st.info("ملاحظة: بانتظار تصحيحاتك للنصوص الفرنسية لاعتمادها نهائياً هنا.")
        if st.button("توليد محضر فتح الأظرفة (نموذج مؤقت)"):
            st.write("جاري التحضير...")

    with t_bc2:
        up_imgs = st.file_uploader("ارفع صور الأشغال", accept_multiple_files=True)
        if up_imgs:
            if st.button("تحميل الألبوم المنسق"):
                st.success("تم التجهيز")

# --- الوحدة 3: الصفقات العمومية (AO) ---
elif main_menu == "🏗️ الصفقات العمومية (AO)":
    st.header("🏗️ تدبير المشاريع الكبرى (Appels d'Offres)")
    ao_stage = st.select_slider("مرحلة الصفقة:", options=["DCE", "النشر", "فتح الأظرفة", "التقييم", "التنفيذ"])
    st.write(f"الصفقة حالياً في مرحلة: **{ao_stage}**")
    
    col_ao1, col_ao2 = st.columns(2)
    with col_ao1:
        st.subheader("💰 تتبع الضمانات")
        st.table(pd.DataFrame({"الشركة": ["A", "B"], "الضمان": ["مؤقت", "نهائي"], "المبلغ": [20000, 50000]}))
    with col_ao2:
        st.subheader("📑 محاضر اللجنة")
        st.selectbox("اختر نوع المحضر للتحميل", ["PV Ouverture", "Rapport d'analyse", "PV d'attribution"])

# --- الوحدة 4: الموارد البشرية (RH) ---
elif main_menu == "👥 الموارد البشرية (RH)":
    st.header("👥 تدبير الموظفين والتقاعد")
    st.subheader("⏳ تنبيهات التقاعد القريبة")
    ret_df = pd.DataFrame([{"الاسم": "موظف أ", "تاريخ التقاعد": "2026-10-12"}, {"الاسم": "موظف ب", "تاريخ التقاعد": "2027-02-05"}])
    st.table(ret_df)
    st.button("توليد قرار رخصة إدارية")

# --- الوحدة 5: الحظيرة والآليات ---
elif main_menu == "🚜 الحظيرة والآليات":
    st.header("🚜 تتبع حظيرة السيارات والآليات")
    st.error("تنبيه: شاحنة النفايات رقم 1 تحتاج فحصاً تقنياً قبل نهاية الأسبوع!")
    st.bar_chart({"استهلاك الشاحنات": 1500, "سيارات المصلحة": 600, "الإسعاف": 800})
    st.number_input("تسجيل استهلاك كازوال (لتر)", value=0)

# --- الوحدة 6: المداخيل والممتلكات ---
elif main_menu == "💰 المداخيل والممتلكات":
    st.header("💰 تدبير ممتلكات الجماعة")
    st.subheader("🏠 وضعية كراء المحلات والمرافق")
    rent_df = pd.DataFrame([
        {"المرفق": "محل 1", "المستأجر": "أحمد", "السومة": 1200, "الحالة": "🔴 متأخر"},
        {"المرفق": "مقهى", "المستأجر": "سعيد", "السومة": 3000, "الحالة": "🟢 مؤدى"}
    ])
    st.table(rent_df)
    st.button("إرسال إنذار أداء (Mise en demeure)")

# --- الوحدة 7: الدورات والمقررات ---
elif main_menu == "🏛️ الدورات والمقررات":
    st.header("🏛️ أمانة المجلس والدورات")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("📅 التحضير للدورة")
        st.date_input("تاريخ الدورة القادمة")
        st.button("توليد استدعاءات الأعضاء")
    with col_s2:
        st.subheader("📜 أرشيف المقررات")
        st.text_input("بحث في المقررات (مثلاً: بيع، شراكة...)")
