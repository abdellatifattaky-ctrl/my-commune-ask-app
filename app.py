import streamlit as st
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from io import BytesIO
from datetime import date
from num2words import num2words

# دالة تحويل المبالغ إلى حروف (بالفرنسية)
def format_to_words_fr(amount_str):
    try:
        val = float(str(amount_str).replace(' ', '').replace(',', ''))
        words = num2words(val, lang='fr').upper()
        cents = int(round((val - int(val)) * 100))
        text = f"{words} DIRHAMS"
        if cents > 0:
            text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
        else:
            text += " ,00CTS"
        return text
    except: return "________________"

st.set_page_config(page_title="Askaouen - Attribution Pro", layout="wide")

# --- الواجهة الجانبية ---
with st.sidebar:
    st.header("👥 لجنة فتح الأظرفة")
    p_name = st.text_input("Président", "MOHAMED ZILALI")
    d_name = st.text_input("Directeur", "M BAREK BAK")
    t_name = st.text_input("Technicien", "ABDELLATIF ATTAKY")

# --- المعطيات التقنية ---
st.title("🏛️ محضر الإسناد النهائي - جماعة أسكاون")
with st.expander("📝 تفاصيل سند الطلب (Bon de Commande)", expanded=True):
    c1, c2, c3 = st.columns(3)
    num_bc = c1.text_input("N° BC", "03/ASK/2025")
    date_pub = c2.date_input("Date de Publication", date(2025, 4, 17))
    reunion_date = c3.date_input("Date de la Réunion", date(2025, 4, 22))
    obj_bc = st.text_area("Objet", "LEVÉ TOPOGRAPHIQUE")

with st.expander("🏆 الشركة الفائزة (Attributaire)", expanded=True):
    col_a, col_b = st.columns(2)
    winner_name = col_a.text_input("Nom de la société", "MAPTOPO")
    winner_amount = col_b.text_input("Montant TTC (Ex: 15348.00)", "15348.00")

# --- التنفيذ واستخراج الوثيقة ---
if st.button("🚀 توليد محضر الإسناد النهائي"):
    doc = Document()
    
    # الترويسة الرسمية
    section = doc.sections[0]
    ht = section.header.add_table(1, 2, Inches(6.5))
    ht.rows[0].cells[0].text = "ROYAUME DU MAROC\nMINISTERE DE L'INTERIEUR\nCOMMUNE D'ASKAOUN"
    ht.rows[0].cells[1].text = "المملكة المغربية\nوزارة الداخلية\nجماعة أسكاون"
    ht.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # العنوان والموضوع
    doc.add_paragraph("\n")
    doc.add_heading("Procès-verbal d'attribution", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Objet : {obj_bc}").bold = True
    
    # النص الحرفي الذي أرسلته (مع تعويض المتغيرات)
    p1 = doc.add_paragraph()
    p1.add_run(f"Le {reunion_date.strftime('%d %B %Y')} à 13h00mn, la commission d’ouverture des plis composée Comme suit :\n")
    p1.add_run(f"  -  {p_name} : Président de la commission\n")
    p1.add_run(f"  -  {d_name} : Directeur du service\n")
    p1.add_run(f"  -  {t_name} : Technicien de la commune\n")
    
    p2 = doc.add_paragraph()
    p2.add_run(f"S’est réunie dans la salle de la réunion de la commune sur invitation du président de la commission d’ouverture des plis concernant l’avis d’achat du bon de commande n° {num_bc} publié le : {date_pub.strftime('%d/%m/%Y')} sur le portail des marchés publics, en application des dispositions de l'article 91 du décret n° 2-22-431 (8 mars 2023) relatif aux marchés publics, ayant pour objet : {obj_bc}.\n")
    
    p3 = doc.add_paragraph()
    p3.add_run(f"Après vérification du portail des marchés publics, la commission d’ouverture des plis constate que la société : {winner_name} a confirmé son offre par lettre de confirmation.\n")
    
    # جملة الإسناد النهائية (بالتنسيق العريض)
    amt_words = format_to_words_fr(winner_amount)
    p4 = doc.add_paragraph()
    run_final = p4.add_run(f"Le président de la commission valide la confirmation et attribue le bon de commande à la société {winner_name} pour un montant de : {winner_amount} Dhs TTC ({amt_words}).")
    run_final.bold = True

    # الخاتمة والتوقيعات
    doc.add_paragraph(f"\nFait à Askaouen, le {date.today().strftime('%d/%m/%Y')}").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 تحميل المحضر النهائي", bio.getvalue(), f"PV_Attribution_{winner_name}.docx")

st.success("✅ تم تحديث النظام ليطابق النص المرجعي لإسناد 'LEVÉ TOPOGRAPHIQUE'.")
