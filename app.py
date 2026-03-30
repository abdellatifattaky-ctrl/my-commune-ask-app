import sqlite3
from datetime import date
from io import BytesIO

import streamlit as st
from docx import Document

st.set_page_config(page_title="تدبير الصفقات والمحاضر", layout="wide")

DB_PATH = "tenders.db"

PHASES = [
    "الإعداد",
    "الإعلان",
    "فتح الأظرفة",
    "فحص الملف الإداري",
    "فحص الملف التقني",
    "تقييم العروض المالية",
    "الإسناد",
    "التبليغ",
    "التنفيذ",
]

PV_TYPES = {
    "فتح الأظرفة": [
        "محضر فتح الأظرفة",
        "لائحة المتنافسين",
        "محضر فحص الملف الإداري",
        "محضر فحص الملف التقني",
        "محضر قبول أو إقصاء المتنافسين",
    ],
    "فحص الملف الإداري": [
        "محضر الفحص الإداري",
        "محضر طلب استكمال الوثائق",
        "محضر الإقصاء الإداري",
    ],
    "فحص الملف التقني": [
        "محضر التقييم التقني",
        "محضر القبول التقني",
        "محضر الإقصاء التقني",
    ],
    "تقييم العروض المالية": [
        "محضر فتح العروض المالية",
        "محضر تقييم العروض المالية",
        "محضر ترتيب المتنافسين",
    ],
    "الإسناد": [
        "محضر اقتراح الإسناد",
        "تقرير تقديم الصفقة",
        "قرار الإسناد",
    ],
}

DOCUMENT_CHECKLIST = [
    "دفتر الشروط الخاصة CPS",
    "نظام الاستشارة RC",
    "التقدير المالي",
    "إعلان طلب المنافسة",
    "محضر فتح الأظرفة",
    "محضر التحليل",
    "تقرير التقديم",
    "الأمر بالخدمة",
]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tenders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT,
            objet TEXT,
            service TEXT,
            maitre_ouvrage TEXT,
            type_marche TEXT,
            budget_estime TEXT,
            date_annonce TEXT,
            date_ouverture TEXT,
            attributaire TEXT,
            statut TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tender_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tender_id INTEGER NOT NULL,
            doc_name TEXT NOT NULL,
            is_checked INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (tender_id) REFERENCES tenders(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS minutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tender_id INTEGER NOT NULL,
            phase TEXT,
            minute_type TEXT,
            minute_date TEXT,
            lieu TEXT,
            commission TEXT,
            participants TEXT,
            observations TEXT,
            decision_text TEXT,
            FOREIGN KEY (tender_id) REFERENCES tenders(id)
        )
        """
    )
    conn.commit()
    conn.close()


def create_tender(data, docs_map):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tenders (
            reference, objet, service, maitre_ouvrage, type_marche,
            budget_estime, date_annonce, date_ouverture, attributaire, statut
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["reference"],
            data["objet"],
            data["service"],
            data["maitre_ouvrage"],
            data["type_marche"],
            data["budget_estime"],
            data["date_annonce"],
            data["date_ouverture"],
            data["attributaire"],
            data["statut"],
        ),
    )
    tender_id = cur.lastrowid
    for doc_name, checked in docs_map.items():
        cur.execute(
            "INSERT INTO tender_documents (tender_id, doc_name, is_checked) VALUES (?, ?, ?)",
            (tender_id, doc_name, 1 if checked else 0),
        )
    conn.commit()
    conn.close()
    return tender_id


def list_tenders():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tenders ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_tender(tender_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tenders WHERE id = ?", (tender_id,)).fetchone()
    conn.close()
    return row


def get_tender_documents(tender_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT doc_name, is_checked FROM tender_documents WHERE tender_id = ? ORDER BY id",
        (tender_id,),
    ).fetchall()
    conn.close()
    return rows


def add_minute(tender_id, payload):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO minutes (
            tender_id, phase, minute_type, minute_date, lieu,
            commission, participants, observations, decision_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tender_id,
            payload["phase"],
            payload["minute_type"],
            payload["minute_date"],
            payload["lieu"],
            payload["commission"],
            payload["participants"],
            payload["observations"],
            payload["decision_text"],
        ),
    )
    conn.commit()
    conn.close()


def get_minutes(tender_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM minutes WHERE tender_id = ? ORDER BY id DESC",
        (tender_id,),
    ).fetchall()
    conn.close()
    return rows


def update_tender(tender_id, data):
    conn = get_conn()
    conn.execute(
        """
        UPDATE tenders
        SET reference = ?, objet = ?, service = ?, maitre_ouvrage = ?,
            type_marche = ?, budget_estime = ?, date_annonce = ?, date_ouverture = ?,
            attributaire = ?, statut = ?
        WHERE id = ?
        """,
        (
            data["reference"],
            data["objet"],
            data["service"],
            data["maitre_ouvrage"],
            data["type_marche"],
            data["budget_estime"],
            data["date_annonce"],
            data["date_ouverture"],
            data["attributaire"],
            data["statut"],
            tender_id,
        ),
    )
    conn.commit()
    conn.close()


def replace_tender_documents(tender_id, docs_map):
    conn = get_conn()
    conn.execute("DELETE FROM tender_documents WHERE tender_id = ?", (tender_id,))
    for doc_name, checked in docs_map.items():
        conn.execute(
            "INSERT INTO tender_documents (tender_id, doc_name, is_checked) VALUES (?, ?, ?)",
            (tender_id, doc_name, 1 if checked else 0),
        )
    conn.commit()
    conn.close()


def delete_tender(tender_id):
    conn = get_conn()
    conn.execute("DELETE FROM minutes WHERE tender_id = ?", (tender_id,))
    conn.execute("DELETE FROM tender_documents WHERE tender_id = ?", (tender_id,))
    conn.execute("DELETE FROM tenders WHERE id = ?", (tender_id,))
    conn.commit()
    conn.close()


def get_minute(minute_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM minutes WHERE id = ?", (minute_id,)).fetchone()
    conn.close()
    return row


def update_minute(minute_id, payload):
    conn = get_conn()
    conn.execute(
        """
        UPDATE minutes
        SET phase = ?, minute_type = ?, minute_date = ?, lieu = ?,
            commission = ?, participants = ?, observations = ?, decision_text = ?
        WHERE id = ?
        """,
        (
            payload["phase"],
            payload["minute_type"],
            payload["minute_date"],
            payload["lieu"],
            payload["commission"],
            payload["participants"],
            payload["observations"],
            payload["decision_text"],
            minute_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_minute(minute_id):
    conn = get_conn()
    conn.execute("DELETE FROM minutes WHERE id = ?", (minute_id,))
    conn.commit()
    conn.close()


def count_minutes():
    conn = get_conn()
    value = conn.execute("SELECT COUNT(*) AS total FROM minutes").fetchone()["total"]
    conn.close()
    return value


def count_awarded():
    conn = get_conn()
    value = conn.execute(
        "SELECT COUNT(*) AS total FROM tenders WHERE attributaire IS NOT NULL AND TRIM(attributaire) <> ''"
    ).fetchone()["total"]
    conn.close()
    return value


def render_minute_text(tender, minute):
    minute_type = minute["minute_type"] or ""
    reference = tender["reference"] or ""
    objet = tender["objet"] or ""
    service = tender["service"] or ""
    maitre_ouvrage = tender["maitre_ouvrage"] or ""
    type_marche = tender["type_marche"] or ""
    minute_date = minute["minute_date"] or ""
    lieu = minute["lieu"] or ""
    commission = minute["commission"] or ""
    participants = minute["participants"] or ""
    observations = minute["observations"] or ""
    decision_text = minute["decision_text"] or ""
    phase = minute["phase"] or ""

    header = """ROYAUME DU MAROC
MINISTERE DE L’INTERIEUR
PROVINCE DE TAROUDANT
CERCLE TALIOUINE
CAIDAT ASKAOUEN
COMMUNE ASKAOUEN
"""

    if minute_type == "محضر فتح الأظرفة":
        return f"""{header}

PROCES VERBAL D'APPEL D'OFFRES OUVERT NATIONAL
1ère séance
SUR OFFRE DE PRIX N° : {reference}

Le {minute_date}, à {lieu}, une commission d’appel d’offres, conformément à la décision de l’ordonnateur, est composée comme suit :
{commission}

S’est réunie en séance publique en vue de procéder à l’ouverture des plis concernant l’appel d’offres ouvert sur offre de prix N° : {reference}, relatif à : {objet}.

Le président rappelle les références de publication, les modalités de publicité ainsi que la liste des concurrents ayant déposé ou transmis leurs plis :
{participants}

Le président s’assure de la présence des membres dont la présence est obligatoire.
Le président remet le support écrit contenant l’estimation des coûts détaillés des prestations.
Les membres de la commission paraphent le support de l’estimation.
Le président invite ensuite les membres à formuler, le cas échéant, leurs réserves ou observations sur les vices éventuels susceptibles d’entacher la procédure.

Observations consignées :
{observations}

Le président ouvre les enveloppes contenant les dossiers des concurrents, cite dans chacun d’eux la présence des enveloppes exigées, puis ouvre l’enveloppe portant la mention dossier administratif et énonce les pièces contenues dans chaque dossier administratif et technique.

Cette formalité accomplie, la séance publique est suspendue, les concurrents et le public se retirent de la salle, et la commission se réunit à huis clos pour examiner les dossiers administratifs et techniques.

Résultats et décisions de la commission :
{decision_text}

La séance publique est ensuite reprise. Le président donne lecture de la liste des soumissionnaires admissibles et suspend la séance en vue de la transmission des dossiers admissibles à la sous-commission technique compétente.

Fait à {lieu}, le {minute_date}

LE PRESIDENT
LES MEMBRES
"""

    if minute_type == "لائحة المتنافسين":
        return f"""{header}

LISTE DES CONCURRENTS

Appel d’offres ouvert sur offre de prix N° : {reference}
Objet : {objet}
Date : {minute_date}
Lieu : {lieu}

La présente liste récapitule les concurrents ayant déposé ou transmis leurs plis dans le cadre de la procédure précitée :
{participants}

Observations :
{observations}

La présente liste est établie pour être jointe au dossier de l’appel d’offres.
"""

    if minute_type in ["محضر فحص الملف الإداري", "محضر الفحص الإداري"]:
        return f"""{header}

PROCES VERBAL D’EXAMEN DU DOSSIER ADMINISTRATIF

Appel d’offres ouvert sur offre de prix N° : {reference}
Objet : {objet}

Le {minute_date}, la commission compétente, composée comme suit :
{commission}

s’est réunie à {lieu} afin de procéder à l’examen des dossiers administratifs des concurrents ci-après :
{participants}

Après vérification des pièces produites au regard des exigences du règlement de consultation, la commission a relevé les observations suivantes :
{observations}

En conséquence, la commission arrête la décision suivante :
{decision_text}

Le présent procès-verbal est établi pour servir et valoir ce que de droit.
"""

    if minute_type == "محضر طلب استكمال الوثائق":
        return f"""{header}

PROCES VERBAL DE DEMANDE DE COMPLEMENT DU DOSSIER ADMINISTRATIF

Appel d’offres ouvert sur offre de prix N° : {reference}
Objet : {objet}

Le {minute_date}, la commission compétente s’est réunie à {lieu} pour examiner la situation administrative du concurrent concerné dans le cadre de la procédure susvisée.

Concurrents concernés :
{participants}

Après examen, la commission a constaté les insuffisances ou pièces complémentaires suivantes :
{observations}

En conséquence, il est décidé d’inviter le concurrent concerné à produire les compléments requis dans le délai réglementaire.

Décision détaillée :
{decision_text}

Le présent procès-verbal est établi pour servir et valoir ce que de droit.
"""

    if minute_type in ["محضر الإقصاء الإداري", "محضر قبول أو إقصاء المتنافسين", "محضر الإقصاء التقني"]:
        return f"""{header}

{minute_type.upper()}

Appel d’offres ouvert sur offre de prix N° : {reference}
Objet : {objet}

Le {minute_date}, la commission compétente, réunie à {lieu}, a examiné la situation des concurrents suivants :
{participants}

Après examen des éléments du dossier, les motifs et observations retenus sont les suivants :
{observations}

Par conséquent, la commission décide ce qui suit :
{decision_text}

Le présent procès-verbal est établi pour servir et valoir ce que de droit.
"""

    if minute_type in ["محضر فحص الملف التقني", "محضر التقييم التقني", "محضر القبول التقني"]:
        return f"""{header}

RAPPORT DE LA SOUS-COMMISSION TECHNIQUE

Appel d’offres ouvert national {reference}
Objet : {objet}
EXAMEN DES OFFRES TECHNIQUES

Le {minute_date}, faisant suite à la séance d’ouverture des plis et à la décision du président de la commission d’ouverture des plis de désigner une sous-commission technique, conformément aux dispositions réglementaires applicables, la sous-commission technique s’est réunie à {lieu} pour examiner et analyser les offres techniques produites par les concurrents admis après étude des dossiers administratifs.

Composition de la sous-commission technique :
{commission}

Liste des concurrents soumis à l’examen technique :
{participants}

Constatations et observations :
{observations}

Conclusion de la sous-commission :
{decision_text}

Le présent rapport est établi pour être joint au dossier de l’appel d’offres.
"""

    if minute_type in ["محضر فتح العروض المالية", "محضر تقييم العروض المالية", "محضر ترتيب المتنافسين"]:
        return f"""{header}

PROCES VERBAL D'APPEL D'OFFRES OUVERT NATIONAL
2ème Séance Publique
SUR OFFRE DE PRIX N° : {reference}

Le {minute_date}, la commission d’appel d’offres, composée comme suit :
{commission}

s’est réunie à {lieu} pour examiner le rapport de la sous-commission technique et procéder à l’ouverture des offres financières des concurrents déclarés admissibles dans le cadre de l’appel d’offres relatif à : {objet}.

Concurrents admissibles et éléments soumis à lecture :
{participants}

La commission procède à la lecture des notes techniques, à l’ouverture des enveloppes financières, à la vérification des opérations arithmétiques et, le cas échéant, à la rectification des erreurs de calcul relevées.

Observations, calcul du prix de référence et classement :
{observations}

Après délibération, la commission arrête la décision suivante :
{decision_text}

Le président suspend, le cas échéant, la séance en vue de la production du complément du dossier administratif ou de la reprise des travaux à la date fixée.

Le présent procès-verbal est établi pour servir et valoir ce que de droit.
"""

    if minute_type in ["محضر اقتراح الإسناد", "قرار الإسناد"]:
        return f"""{header}

{minute_type.upper()}

Appel d’offres ouvert sur offre de prix N° : {reference}
Objet : {objet}

Le {minute_date}, la commission compétente, réunie à {lieu}, après examen de l’ensemble des résultats des différentes phases de la procédure, a constaté ce qui suit :
{observations}

Au vu des éléments examinés, il est décidé / proposé ce qui suit :
{decision_text}

Concurrents concernés :
{participants}

Le présent acte est établi pour servir et valoir ce que de droit.
"""

    if minute_type == "تقرير تقديم الصفقة":
        return f"""{header}

RAPPORT DE PRESENTATION

Le présent rapport concerne l’appel d’offres / la consultation N° : {reference}
Objet : {objet}
Maître d’ouvrage : {maitre_ouvrage}
Service concerné : {service}
Type de marché : {type_marche}
Date : {minute_date}

Présentation générale de l’opération :
{observations}

Résultats de la procédure et suite proposée :
{decision_text}

Concurrents ou intervenants concernés :
{participants}

Le présent rapport est établi pour être versé au dossier correspondant.
"""

    if minute_type == "PV 3ème séance publique":
        return f"""{header}

PROCES VERBAL D'APPEL D'OFFRES OUVERT NATIONAL
3ème Séance Publique
SUR OFFRE DE PRIX N° : {reference}

Le {minute_date}, la commission d’appel d’offres, composée comme suit :
{commission}

s’est réunie en séance publique à {lieu}, en vue de procéder à l’ouverture et à l’examen des pièces complémentaires du dossier administratif du concurrent concerné dans le cadre de l’appel d’offres relatif à : {objet}.

Concurrents concernés :
{participants}

La commission s’assure du support ayant servi de moyen d’invitation, vérifie les pièces et la réponse reçue, puis examine les compléments produits.

Observations :
{observations}

Après examen, la commission décide ce qui suit :
{decision_text}

Le présent procès-verbal est établi pour servir et valoir ce que de droit.
"""

    return f"""{header}

{minute_type}

Référence : {reference}
Objet : {objet}
Service concerné : {service}
Maître d’ouvrage : {maitre_ouvrage}
Type de marché : {type_marche}
Phase : {phase}
Date : {minute_date}
Lieu : {lieu}
Commission :
{commission}

Participants / Concurrents :
{participants}

Observations :
{observations}

Décision / Résultat :
{decision_text}

Le présent document est établi pour servir et valoir ce que de droit.
"""


def generate_docx_bytes(tender, minute):
    document = Document()
    document.add_heading("المملكة المغربية", level=1)
    document.add_paragraph("الجماعة ................................")
    document.add_paragraph("")
    document.add_heading(minute["minute_type"], level=2)

    items = [
        ("مرجع الصفقة / الاستشارة", tender["reference"]),
        ("موضوع الصفقة", tender["objet"]),
        ("المصلحة المعنية", tender["service"]),
        ("صاحب المشروع", tender["maitre_ouvrage"]),
        ("نوع الصفقة", tender["type_marche"]),
        ("المرحلة", minute["phase"]),
        ("التاريخ", minute["minute_date"]),
        ("المكان", minute["lieu"]),
        ("اللجنة", minute["commission"]),
    ]
    for label, value in items:
        document.add_paragraph(f"{label}: {value or ''}")

    document.add_paragraph("المشاركون / المتنافسون:")
    document.add_paragraph(minute["participants"] or "")

    document.add_paragraph("الملاحظات:")
    document.add_paragraph(minute["observations"] or "")

    document.add_paragraph("القرار / النتيجة:")
    document.add_paragraph(minute["decision_text"] or "")

    document.add_paragraph("حرر هذا المحضر للإدلاء به عند الحاجة.")

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


init_db()

if "edit_minute_id" not in st.session_state:
    st.session_state.edit_minute_id = None

st.sidebar.title("تطبيق تدبير الصفقات")
page = st.sidebar.radio(
    "التنقل",
    ["لوحة التحكم", "إضافة صفقة", "بطاقة صفقة", "حول التطبيق"],
)

if page == "لوحة التحكم":
    st.title("لوحة التحكم")
    tenders = list_tenders()

    c1, c2, c3 = st.columns(3)
    c1.metric("عدد الصفقات", len(tenders))
    c2.metric("عدد المحاضر", count_minutes())
    c3.metric("الصفقات المسندة", count_awarded())

    st.subheader("آخر الصفقات")
    if not tenders:
        st.info("لا توجد صفقات محفوظة بعد.")
    else:
        for tender in tenders:
            with st.container(border=True):
                a, b, c = st.columns([2, 4, 2])
                a.write(f"**المرجع:** {tender['reference'] or '-'}")
                b.write(f"**الموضوع:** {tender['objet'] or '-'}")
                c.write(f"**الحالة:** {tender['statut'] or '-'}")
                st.caption(
                    f"المصلحة: {tender['service'] or '-'} | فتح الأظرفة: {tender['date_ouverture'] or '-'}"
                )

elif page == "إضافة صفقة":
    st.title("إضافة صفقة / استشارة")
    with st.form("add_tender_form"):
        c1, c2 = st.columns(2)
        reference = c1.text_input("مرجع الصفقة")
        objet = c2.text_input("موضوع الصفقة")
        service = c1.text_input("المصلحة المعنية")
        maitre_ouvrage = c2.text_input("صاحب المشروع")
        type_marche = c1.selectbox("نوع الصفقة", ["أشغال", "توريدات", "خدمات"])
        budget_estime = c2.text_input("التقدير المالي")
        date_annonce = c1.date_input("تاريخ الإعلان", value=date.today())
        date_ouverture = c2.date_input("تاريخ فتح الأظرفة", value=date.today())
        attributaire = c1.text_input("المتعهد الفائز")
        statut = c2.selectbox("الحالة", ["مسودة", "جارية", "مسندة", "منجزة"])

        st.markdown("### لائحة الوثائق")
        docs_cols = st.columns(2)
        docs_map = {}
        for idx, doc_name in enumerate(DOCUMENT_CHECKLIST):
            docs_map[doc_name] = docs_cols[idx % 2].checkbox(doc_name)

        submitted = st.form_submit_button("حفظ الصفقة")
        if submitted:
            payload = {
                "reference": reference,
                "objet": objet,
                "service": service,
                "maitre_ouvrage": maitre_ouvrage,
                "type_marche": type_marche,
                "budget_estime": budget_estime,
                "date_annonce": str(date_annonce),
                "date_ouverture": str(date_ouverture),
                "attributaire": attributaire,
                "statut": statut,
            }
            tender_id = create_tender(payload, docs_map)
            st.success(f"تم حفظ الصفقة بنجاح. رقمها الداخلي: {tender_id}")

elif page == "بطاقة صفقة":
    st.title("بطاقة صفقة")
    tenders = list_tenders()
    if not tenders:
        st.warning("أضف صفقة أولًا.")
        st.stop()

    labels = {
        f"#{t['id']} - {t['reference'] or 'بدون مرجع'} - {t['objet'] or 'بدون موضوع'}": t["id"]
        for t in tenders
    }
    selected_label = st.selectbox("اختر صفقة", list(labels.keys()))
    tender_id = labels[selected_label]
    tender = get_tender(tender_id)
    docs = get_tender_documents(tender_id)
    minutes = get_minutes(tender_id)

    info1, info2, info3 = st.columns(3)
    info1.write(f"**المرجع:** {tender['reference'] or '-'}")
    info2.write(f"**الموضوع:** {tender['objet'] or '-'}")
    info3.write(f"**الحالة:** {tender['statut'] or '-'}")
    st.write(f"**المصلحة:** {tender['service'] or '-'}")
    st.write(f"**صاحب المشروع:** {tender['maitre_ouvrage'] or '-'}")
    st.write(f"**تاريخ فتح الأظرفة:** {tender['date_ouverture'] or '-'}")
    st.write(f"**الفائز:** {tender['attributaire'] or '-'}")

    st.markdown("### تعديل بيانات الصفقة")
    with st.form(f"edit_tender_{tender_id}"):
        c1, c2 = st.columns(2)
        reference = c1.text_input("مرجع الصفقة", value=tender["reference"] or "")
        objet = c2.text_input("موضوع الصفقة", value=tender["objet"] or "")
        service = c1.text_input("المصلحة المعنية", value=tender["service"] or "")
        maitre_ouvrage = c2.text_input("صاحب المشروع", value=tender["maitre_ouvrage"] or "")
        type_options = ["أشغال", "توريدات", "خدمات"]
        type_index = type_options.index(tender["type_marche"]) if tender["type_marche"] in type_options else 0
        type_marche = c1.selectbox("نوع الصفقة", type_options, index=type_index)
        budget_estime = c2.text_input("التقدير المالي", value=tender["budget_estime"] or "")
        date_annonce = c1.text_input("تاريخ الإعلان", value=tender["date_annonce"] or "")
        date_ouverture = c2.text_input("تاريخ فتح الأظرفة", value=tender["date_ouverture"] or "")
        attributaire = c1.text_input("المتعهد الفائز", value=tender["attributaire"] or "")
        status_options = ["مسودة", "جارية", "مسندة", "منجزة"]
        status_index = status_options.index(tender["statut"]) if tender["statut"] in status_options else 0
        statut = c2.selectbox("الحالة", status_options, index=status_index)

        st.markdown("#### تحديث لائحة الوثائق")
        current_docs = {doc["doc_name"]: bool(doc["is_checked"]) for doc in docs}
        docs_cols = st.columns(2)
        docs_map = {}
        for idx, doc_name in enumerate(DOCUMENT_CHECKLIST):
            docs_map[doc_name] = docs_cols[idx % 2].checkbox(
                doc_name,
                value=current_docs.get(doc_name, False),
                key=f"edit_doc_{tender_id}_{idx}",
            )

        s1, s2 = st.columns(2)
        save_tender = s1.form_submit_button("حفظ التعديلات")
        remove_tender = s2.form_submit_button("حذف الصفقة")

        if save_tender:
            update_tender(
                tender_id,
                {
                    "reference": reference,
                    "objet": objet,
                    "service": service,
                    "maitre_ouvrage": maitre_ouvrage,
                    "type_marche": type_marche,
                    "budget_estime": budget_estime,
                    "date_annonce": date_annonce,
                    "date_ouverture": date_ouverture,
                    "attributaire": attributaire,
                    "statut": statut,
                },
            )
            replace_tender_documents(tender_id, docs_map)
            st.success("تم تحديث الصفقة.")
            st.rerun()

        if remove_tender:
            delete_tender(tender_id)
            st.success("تم حذف الصفقة وكل المحاضر المرتبطة بها.")
            st.rerun()

    st.markdown("### الوثائق")
    d1, d2 = st.columns(2)
    for idx, doc in enumerate(get_tender_documents(tender_id)):
        marker = "✅" if doc["is_checked"] else "⬜"
        (d1 if idx % 2 == 0 else d2).write(f"{marker} {doc['doc_name']}")

    st.markdown("---")
    st.subheader("إضافة محضر جديد")
    with st.form("add_minute_form"):
        c1, c2 = st.columns(2)
        phase = c1.selectbox("المرحلة", PHASES)
        minute_type = c2.selectbox("نوع المحضر", PV_TYPES.get(phase, ["محضر عام"]))
        minute_date = c1.date_input("تاريخ المحضر", value=date.today())
        lieu = c2.text_input("مكان الاجتماع / الجلسة")
        commission = c1.text_input("اللجنة")
        participants = st.text_area("المشاركون / المتنافسون")
        observations = st.text_area("الملاحظات")
        decision_text = st.text_area("القرار / النتيجة")
        save_minute = st.form_submit_button("حفظ المحضر")
        if save_minute:
            add_minute(
                tender_id,
                {
                    "phase": phase,
                    "minute_type": minute_type,
                    "minute_date": str(minute_date),
                    "lieu": lieu,
                    "commission": commission,
                    "participants": participants,
                    "observations": observations,
                    "decision_text": decision_text,
                },
            )
            st.success("تم حفظ المحضر.")
            st.rerun()

    if st.session_state.edit_minute_id is not None:
        editable_minute = get_minute(st.session_state.edit_minute_id)
        if editable_minute and editable_minute["tender_id"] == tender_id:
            st.markdown("---")
            st.subheader("تعديل المحضر")
            with st.form(f"edit_minute_{editable_minute['id']}"):
                c1, c2 = st.columns(2)
                phase_options = PHASES
                phase_index = phase_options.index(editable_minute["phase"]) if editable_minute["phase"] in phase_options else 0
                edit_phase = c1.selectbox("المرحلة", phase_options, index=phase_index)
                minute_options = PV_TYPES.get(edit_phase, ["محضر عام"])
                minute_index = minute_options.index(editable_minute["minute_type"]) if editable_minute["minute_type"] in minute_options else 0
                edit_type = c2.selectbox("نوع المحضر", minute_options, index=minute_index)
                edit_date = c1.text_input("تاريخ المحضر", value=editable_minute["minute_date"] or "")
                edit_lieu = c2.text_input("مكان الاجتماع / الجلسة", value=editable_minute["lieu"] or "")
                edit_commission = c1.text_input("اللجنة", value=editable_minute["commission"] or "")
                edit_participants = st.text_area("المشاركون / المتنافسون", value=editable_minute["participants"] or "")
                edit_observations = st.text_area("الملاحظات", value=editable_minute["observations"] or "")
                edit_decision = st.text_area("القرار / النتيجة", value=editable_minute["decision_text"] or "")
                e1, e2 = st.columns(2)
                submit_edit = e1.form_submit_button("حفظ تعديل المحضر")
                cancel_edit = e2.form_submit_button("إلغاء التعديل")
                if submit_edit:
                    update_minute(
                        editable_minute["id"],
                        {
                            "phase": edit_phase,
                            "minute_type": edit_type,
                            "minute_date": edit_date,
                            "lieu": edit_lieu,
                            "commission": edit_commission,
                            "participants": edit_participants,
                            "observations": edit_observations,
                            "decision_text": edit_decision,
                        },
                    )
                    st.session_state.edit_minute_id = None
                    st.success("تم تعديل المحضر.")
                    st.rerun()
                if cancel_edit:
                    st.session_state.edit_minute_id = None
                    st.rerun()

    st.markdown("---")
    st.subheader("المحاضر المسجلة")
    if not minutes:
        st.info("لا توجد محاضر لهذه الصفقة.")
    else:
        for idx, minute in enumerate(minutes, start=1):
            with st.expander(f"{idx}. {minute['minute_type']} - {minute['minute_date']}"):
                st.write(f"**المرحلة:** {minute['phase'] or '-'}")
                st.write(f"**المكان:** {minute['lieu'] or '-'}")
                st.write(f"**اللجنة:** {minute['commission'] or '-'}")

                generated_text = render_minute_text(tender, minute)
                st.text_area(
                    "نص المحضر",
                    value=generated_text,
                    height=320,
                    key=f"minute_preview_{minute['id']}",
                )

                txt_name = f"PV_{tender['reference'] or tender['id']}_{minute['id']}.txt"
                docx_name = f"PV_{tender['reference'] or tender['id']}_{minute['id']}.docx"

                b1, b2, b3, b4 = st.columns(4)
                b1.download_button(
                    "تحميل TXT",
                    data=generated_text,
                    file_name=txt_name,
                    mime="text/plain",
                    key=f"txt_{minute['id']}",
                )
                b2.download_button(
                    "تحميل Word",
                    data=generate_docx_bytes(tender, minute),
                    file_name=docx_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"docx_{minute['id']}",
                )
                if b3.button("تعديل", key=f"edit_btn_{minute['id']}"):
                    st.session_state.edit_minute_id = minute["id"]
                    st.rerun()
                if b4.button("حذف", key=f"delete_btn_{minute['id']}"):
                    delete_minute(minute["id"])
                    if st.session_state.edit_minute_id == minute["id"]:
                        st.session_state.edit_minute_id = None
                    st.success("تم حذف المحضر.")
                    st.rerun()

else:
    st.title("حول التطبيق")
    st.markdown(
        """
        هذا الإصدار هو نسخة أولية عملية مبنية بـ Streamlit ومناسبة للبداية على GitHub.

        **المزايا الحالية:**
        - حفظ البيانات في SQLite
        - إنشاء صفقات متعددة
        - إضافة عدة محاضر داخل كل صفقة
        - تصدير المحاضر بصيغتي TXT و Word
        - واجهة عربية بسيطة

        **التطويرات القادمة المقترحة:**
        - تعديل المحاضر بعد الحفظ
        - حذف محضر أو صفقة
        - قوالب محاضر قانونية أكثر دقة
        - تسجيل المستخدمين
        - رفع المرفقات والوثائق
        """
    )
