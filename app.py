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

    header = "المملكة المغربية
الجماعة ................................
"

    if minute_type == "محضر فتح الأظرفة":
        return f"""{header}
محضر فتح الأظرفة

في يوم {minute_date} وعلى الساعة ..........، بمقر {lieu or 'الجماعة'}، اجتمعت {commission or 'لجنة فتح الأظرفة'} من أجل فتح الأظرفة المتعلقة بالصفقة/الاستشارة ذات المرجع {reference}، المتعلقة بـ: {objet}.

صاحب المشروع: {maitre_ouvrage}
المصلحة المعنية: {service}
نوع الصفقة: {type_marche}

افتتحت الجلسة بحضور الأعضاء والمتنافسين أو من يمثلهم، كما يلي:
{participants}

بعد التأكد من سلامة الأظرفة والتصريحات المتعلقة بها، تم الشروع في فتحها وفحص الوثائق المدرجة بها وفق المسطرة المعمول بها.

ملاحظات اللجنة:
{observations}

وبعد الانتهاء من عملية فتح الأظرفة، خلصت اللجنة إلى ما يلي:
{decision_text}

وحرر هذا المحضر للإدلاء به عند الاقتضاء.
"""

    if minute_type == "لائحة المتنافسين":
        return f"""{header}
لائحة المتنافسين

تتعلق هذه اللائحة بالصفقة/الاستشارة ذات المرجع {reference}، موضوعها: {objet}.
تاريخ الجلسة: {minute_date}
مكان الجلسة: {lieu}

لائحة المتنافسين المشاركين أو الحاضرين:
{participants}

ملاحظات إضافية:
{observations}

حررت هذه اللائحة قصد إرفاقها بملف الصفقة.
"""

    if minute_type in ["محضر فحص الملف الإداري", "محضر الفحص الإداري"]:
        return f"""{header}
محضر فحص الملف الإداري

اجتمعت {commission or 'اللجنة المختصة'} بتاريخ {minute_date} بمقر {lieu or 'الجماعة'} لدراسة الملفات الإدارية المتعلقة بالصفقة/الاستشارة رقم {reference}، موضوعها: {objet}.

بعد استعراض الوثائق المدلى بها من طرف المتنافسين الآتية أسماؤهم:
{participants}

قامت اللجنة بفحص الملفات الإدارية والتأكد من الوثائق المطلوبة ومدى مطابقتها.

نتائج الفحص والملاحظات:
{observations}

قرار اللجنة:
{decision_text}

حرر هذا المحضر قصد اعتماده ضمن وثائق الصفقة.
"""

    if minute_type == "محضر طلب استكمال الوثائق":
        return f"""{header}
محضر طلب استكمال الوثائق

بتاريخ {minute_date} اجتمعت {commission or 'اللجنة المختصة'} بمقر {lieu or 'الجماعة'} بخصوص الصفقة/الاستشارة رقم {reference} المتعلقة بـ: {objet}.

بعد دراسة الملفات المدلى بها من طرف المتنافسين التالي ذكرهم:
{participants}

تبين للجنة وجود نواقص أو وثائق تحتاج إلى استكمال أو توضيح كما يلي:
{observations}

وعليه تقرر مطالبة المعنيين بالأمر باستكمال الوثائق أو تقديم التوضيحات اللازمة داخل الآجال المحددة.

تفاصيل القرار:
{decision_text}

حرر هذا المحضر للإدلاء به عند الحاجة.
"""

    if minute_type in ["محضر الإقصاء الإداري", "محضر قبول أو إقصاء المتنافسين", "محضر الإقصاء التقني"]:
        return f"""{header}
{minute_type}

بتاريخ {minute_date} اجتمعت {commission or 'اللجنة المختصة'} بمقر {lieu or 'الجماعة'} لدراسة وضعية المتنافسين في إطار الصفقة/الاستشارة رقم {reference}، موضوعها: {objet}.

المتنافسون المعنيون:
{participants}

الأسباب والملاحظات المعتمدة من طرف اللجنة:
{observations}

وبناءً عليه قررت اللجنة ما يلي:
{decision_text}

حرر هذا المحضر لتوثيق قرارات القبول أو الإقصاء.
"""

    if minute_type in ["محضر فحص الملف التقني", "محضر التقييم التقني", "محضر القبول التقني"]:
        return f"""{header}
{minute_type}

في يوم {minute_date} اجتمعت {commission or 'اللجنة التقنية'} بمقر {lieu or 'الجماعة'} لدراسة الملفات التقنية المتعلقة بالصفقة/الاستشارة رقم {reference} الخاصة بـ: {objet}.

لائحة المتنافسين المعنيين:
{participants}

بعد فحص العروض التقنية ومقارنتها بالمتطلبات التقنية المنصوص عليها، سجلت اللجنة الملاحظات التالية:
{observations}

واستقرت اللجنة على القرار التالي:
{decision_text}

حرر هذا المحضر للإدلاء به عند الاقتضاء.
"""

    if minute_type in ["محضر فتح العروض المالية", "محضر تقييم العروض المالية", "محضر ترتيب المتنافسين"]:
        return f"""{header}
{minute_type}

اجتمعت {commission or 'اللجنة المختصة'} بتاريخ {minute_date} بمقر {lieu or 'الجماعة'} بخصوص الصفقة/الاستشارة رقم {reference}، موضوعها: {objet}.

وقد تمت دراسة العروض المالية المقدمة من طرف المتنافسين التالية أسماؤهم:
{participants}

ملخص الدراسة والمقارنة:
{observations}

وبعد المداولة تقرر ما يلي:
{decision_text}

حرر هذا المحضر قصد اعتماده ضمن ملف الصفقة.
"""

    if minute_type in ["محضر اقتراح الإسناد", "قرار الإسناد"]:
        return f"""{header}
{minute_type}

اجتمعت {commission or 'اللجنة المختصة'} بتاريخ {minute_date} بمقر {lieu or 'الجماعة'} لدراسة النتائج النهائية المتعلقة بالصفقة/الاستشارة رقم {reference}، موضوعها: {objet}.

وبعد استعراض مختلف مراحل الدراسة والتقييم، وتبعا للمعطيات التالية:
{observations}

فإن اللجنة تقترح/تقرر إسناد الصفقة إلى:
{decision_text}

المتدخلون أو المتنافسون المعنيون:
{participants}

حرر هذا المحضر لاتخاذ المتعين قانونًا وإداريًا.
"""

    if minute_type == "تقرير تقديم الصفقة":
        return f"""{header}
تقرير تقديم الصفقة

يتعلق هذا التقرير بالصفقة/الاستشارة رقم {reference}، موضوعها: {objet}.

صاحب المشروع: {maitre_ouvrage}
المصلحة المعنية: {service}
نوع الصفقة: {type_marche}
تاريخ التحرير: {minute_date}

تقديم عام:
{observations}

المعطيات الأساسية والنتائج:
{decision_text}

المتدخلون أو المتنافسون:
{participants}

وحرر هذا التقرير لتقديم خلاصات المسطرة المعتمدة بخصوص هذه الصفقة.
"""

    return f"""{header}
{minute_type}

مرجع الصفقة / الاستشارة: {reference}
موضوع الصفقة: {objet}
المصلحة المعنية: {service}
صاحب المشروع: {maitre_ouvrage}
نوع الصفقة: {type_marche}
المرحلة: {phase}
التاريخ: {minute_date}
المكان: {lieu}
اللجنة: {commission}

المشاركون / المتنافسون:
{participants}

الملاحظات:
{observations}

القرار / النتيجة:
{decision_text}

حرر هذا المحضر للإدلاء به عند الحاجة.
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
