import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, Cm
from io import BytesIO
from datetime import date
from num2words import num2words

# --- 1. التنسيق الجمالي (Lacoste Style) ---
st.set_page_config(page_title="Commune Askaouen - Système Complet", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #004526 !important; }
    .stButton>button {
        background-color: #004526;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
    }
    </style>
    """, unsafe_allow_html=True)

def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0: text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else: text += " ,00CTS"
        return text
    except: return "________________"

# --- 2. الواجهة الرئيسية ---
st.title("🏛️ المنظومة المتكاملة لسندات الطلب - جماعة أسكاون")

with st.sidebar:
    st.header("👤 أعضاء اللجنة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

with st.expander("📝 المعطيات الإدارية للسند", expanded=True):
    col1, col2 = st.columns(2)
    num_bc = col1.text_input("N° Bon de Commande", "01/ASK/2026")
    date_pub = col2.date_input("Date de Publication (Portail)", date(2026, 3, 25))
    obj_bc = st.text_area("Objet de la prestation", "Location d’une Tractopelle pour les travaux divers.")

st.subheader("📊 لائحة المتنافسين")
df_init = pd.DataFrame([
    {"Rang": 1, "Nom": "STE OUBRAIM SARL", "Montant": "69840.00"},
    {"Rang": 2, "Nom": "DECO GRC", "Montant": "93120.00"},
    {"Rang": 3, "Nom": "AIT MOUMOU REALISATION", "Montant": "102432.00"},
    {"Rang": 4, "Nom": "KADEM SARL", "Montant": "111744.00"},
    {"Rang": 5, "Nom": "TOUZANI 2ZD", "Montant": "114072.00"}
])
data = st.data_editor(df_init, use_container_width=True)

st.divider()

# --- 3. اختيار نوع الوثيقة ---
doc_type = st.selectbox("إختر الوثيقة المراد استخراجها:", 
    ["Procès-verbal (1 à 6)", "Lettre de Notification (التبليغ)", "Procès-verbal de Réception (الاستلام)"])

if doc_type == "Procès-verbal (1 à 6)":
    c_pv, c_date, c_hour = st.columns(3)
    pv_num = c_pv.selectbox("Numéro du PV:", [1, 2, 3, 4, 5, 6])
    reunion_date = c_date.date_input("Date de la séance", date.today())
    reunion_hour = c_hour.text_input("Heure", "10h00mn")
    
    is_infructueux = False
    is_final_attr = False
    if pv_num == 6:
        res_6 = st.radio("Résultat du 6éme PV:", ["Attribution (إسناد)", "B.C Infructueux (غير مثمر)"])
        is_infructueux = (res_6 == "B.C Infructueux (غير مثمر)")
        is_final_attr = not is_infructueux
    else:
        is_final_attr = st.checkbox("✅ PV d'attribution finale")

elif doc_type == "Lettre de Notification (التبليغ)":
    notif_date = st.date_input("Date de Notification", date.today())
    winner_idx = st.selectbox("الشركة النائلة:", range(len(data)), format_func=lambda x: data.iloc[x]['Nom'])

elif doc_type == "Procès-verbal de Réception (الاستلام)":
    reception_date = st.date_input("Date de Réception", date.today())
    winner_idx = st.selectbox("الشركة الموردة:", range(len(data)), format_func=lambda x: data.iloc[x]['Nom'])

# --- 4. توليد الوثائق ---
if st.button("✨ توليد الوثيقة الرسمية"):
    doc = Document()
    # (إعدادات الصفحة والترويسة ثابتة لجميع الوثائق)
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, Inches(6.5))
    htable.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    htable.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    htable.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    if doc_type == "Procès-verbal (1 à 6)":
        # (نفس منطق المحاضر الستة السابق مع الأمانة النصية)
        title = doc.add_heading(f"{pv_num}éme Procès verbal", 1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Objet : {obj_bc}").bold = True
        # ... تكملة كود المحاضر ...

    elif doc_type == "Lettre de Notification (التبليغ)":
        winner = data.iloc[winner_idx]
        doc.add_paragraph(f"\nAskaouen, le {notif_date.strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph(f"À Monsieur le Gérant de la société : {winner['Nom']}")
        title = doc.add_heading("LETTRE DE NOTIFICATION", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nJ’ai l’honneur de vous informer que votre offre concernant le bon de commande n° {num_bc} relatif à : {obj_bc}, pour un montant de {winner['Montant']} Dhs TTC, a été retenue.")
        doc.add_paragraph("\nEn conséquence, vous êtes invité à prendre contact avec nos services pour commencer l'exécution des prestations.")

    elif doc_type == "Procès-verbal de Réception (الاستلام)":
        winner = data.iloc[winner_idx]
        title = doc.add_heading("PROCÈS VERBAL DE RÉCEPTION DÉFINITIVE", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"\nLe {reception_date.strftime('%d/%m/%Y')}, la commission composée de :")
        doc.add_paragraph(f"- M. {p_name}\n- M. {d_name}\n- M. {t_name}")
        doc.add_paragraph(f"S'est réunie pour procéder à la réception des prestations objet du BC n° {num_bc} exécuté par la société {winner['Nom']}.")
        doc.add_paragraph("\nAprès examen, la commission constate que les prestations sont conformes aux spécifications techniques demandées et déclare la RECEPTION DEFINITIVE sans réserve.")

    # (تذييل التوقيعات ثابت)
    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button(f"📥 تحميل {doc_type}", bio.getvalue(), f"{doc_type}.docx")
