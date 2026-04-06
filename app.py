import streamlit as st
from datetime import date

st.set_page_config(page_title="مولد محاضر الصفقات", layout="wide")

st.title("مولد محاضر الصفقات العمومية")
st.caption("نسخة أولية لتوليد محاضر الصفقات بصيغة إدارية عربية")

# ----------------------------
# Helpers
# ----------------------------
def build_opening_minutes(data):
    members_text = "، ".join(
        [f"{m['name']} ({m['role']})" for m in data["committee"] if m["name"].strip()]
    )

    bidders_lines = []
    for i, b in enumerate(data["bidders"], start=1):
        if not b["company_name"].strip():
            continue

        admin_status = "أدلى بالملف الإداري" if b["admin_file"] else "لم يدل بالملف الإداري"
        tech_status = "أدلى بالملف التقني" if b["technical_file"] else "لم يدل بالملف التقني"
        fin_status = "أدلى بالعرض المالي" if b["financial_file"] else "لم يدل بالعرض المالي"

        bidders_lines.append(
            f"{i}- {b['company_name']}، ممثله: {b['representative']}، "
            f"{admin_status}، {tech_status}، {fin_status}."
        )

    bidders_text = "\n".join(bidders_lines) if bidders_lines else "لم يتم تسجيل أي متنافس."

    minutes = f"""
محضر فتح الأظرفة

في يوم {data['session_date']} على الساعة {data['session_time']}، اجتمعت لجنة فتح الأظرفة بمقر {data['session_place']}،
وذلك من أجل فتح الأظرفة المتعلقة بـ "{data['title']}" تحت رقم "{data['reference_number']}"،
لفائدة {data['owner_entity']}، برئاسة {data['president']}، وبحضور السادة أعضاء اللجنة: {members_text}.

وبعد افتتاح الجلسة، تم تسجيل المتنافسين والملفات المودعة كما يلي:
{bidders_text}

وبناءً عليه، تم تحرير هذا المحضر في التاريخ أعلاه لاتخاذ المتعين.

الإمضاءات:
الرئيس: {data['president']}
"""
    return minutes.strip()


# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.header("القائمة")
page = st.sidebar.radio(
    "اختر الصفحة",
    ["البيانات الأساسية", "أعضاء اللجنة", "المتنافسون", "توليد المحضر"]
)

# ----------------------------
# Session State Initialization
# ----------------------------
if "committee" not in st.session_state:
    st.session_state.committee = [
        {"name": "", "role": "عضو"},
        {"name": "", "role": "عضو"},
        {"name": "", "role": "مقرر"},
    ]

if "bidders" not in st.session_state:
    st.session_state.bidders = [
        {
            "company_name": "",
            "representative": "",
            "admin_file": True,
            "technical_file": True,
            "financial_file": True,
            "offer_amount": 0.0,
        }
    ]

if "base_data" not in st.session_state:
    st.session_state.base_data = {
        "reference_number": "",
        "title": "",
        "owner_entity": "",
        "procedure_type": "طلب عروض مفتوح",
        "procurement_type": "أشغال",
        "session_date": str(date.today()),
        "session_time": "10:00",
        "session_place": "",
        "president": "",
    }

# ----------------------------
# Page 1: Basic data
# ----------------------------
if page == "البيانات الأساسية":
    st.subheader("البيانات الأساسية للصفقة")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.base_data["reference_number"] = st.text_input(
            "رقم الصفقة / الاستشارة",
            value=st.session_state.base_data["reference_number"]
        )
        st.session_state.base_data["title"] = st.text_input(
            "موضوع الصفقة",
            value=st.session_state.base_data["title"]
        )
        st.session_state.base_data["owner_entity"] = st.text_input(
            "صاحب المشروع / الإدارة",
            value=st.session_state.base_data["owner_entity"]
        )
        st.session_state.base_data["president"] = st.text_input(
            "اسم رئيس اللجنة",
            value=st.session_state.base_data["president"]
        )

    with col2:
        st.session_state.base_data["procedure_type"] = st.selectbox(
            "نوع المسطرة",
            ["طلب عروض مفتوح", "طلب عروض محدود", "تفاوض", "استشارة", "مسطرة أخرى"],
            index=["طلب عروض مفتوح", "طلب عروض محدود", "تفاوض", "استشارة", "مسطرة أخرى"].index(
                st.session_state.base_data["procedure_type"]
            ) if st.session_state.base_data["procedure_type"] in ["طلب عروض مفتوح", "طلب عروض محدود", "تفاوض", "استشارة", "مسطرة أخرى"] else 0
        )
        st.session_state.base_data["procurement_type"] = st.selectbox(
            "نوع العملية",
            ["أشغال", "توريدات", "خدمات"],
            index=["أشغال", "توريدات", "خدمات"].index(
                st.session_state.base_data["procurement_type"]
            ) if st.session_state.base_data["procurement_type"] in ["أشغال", "توريدات", "خدمات"] else 0
        )
        st.session_state.base_data["session_date"] = str(
            st.date_input(
                "تاريخ الجلسة",
                value=date.fromisoformat(st.session_state.base_data["session_date"])
            )
        )
        st.session_state.base_data["session_time"] = st.text_input(
            "ساعة الجلسة",
            value=st.session_state.base_data["session_time"]
        )
        st.session_state.base_data["session_place"] = st.text_input(
            "مكان الجلسة",
            value=st.session_state.base_data["session_place"]
        )

    st.success("تم حفظ البيانات الأساسية داخل الجلسة الحالية.")

# ----------------------------
# Page 2: Committee
# ----------------------------
elif page == "أعضاء اللجنة":
    st.subheader("أعضاء اللجنة")

    num_members = st.number_input(
        "عدد أعضاء اللجنة",
        min_value=1,
        max_value=20,
        value=len(st.session_state.committee),
        step=1
    )

    while len(st.session_state.committee) < num_members:
        st.session_state.committee.append({"name": "", "role": "عضو"})

    while len(st.session_state.committee) > num_members:
        st.session_state.committee.pop()

    for i, member in enumerate(st.session_state.committee):
        st.markdown(f"### العضو {i+1}")
        c1, c2 = st.columns([2, 1])
        member["name"] = c1.text_input(
            f"اسم العضو {i+1}",
            value=member["name"],
            key=f"member_name_{i}"
        )
        member["role"] = c2.selectbox(
            f"صفة العضو {i+1}",
            ["عضو", "مقرر", "رئيس", "ملاحظ"],
            index=["عضو", "مقرر", "رئيس", "ملاحظ"].index(member["role"]) if member["role"] in ["عضو", "مقرر", "رئيس", "ملاحظ"] else 0,
            key=f"member_role_{i}"
        )

    st.success("تم تحديث أعضاء اللجنة.")

# ----------------------------
# Page 3: Bidders
# ----------------------------
elif page == "المتنافسون":
    st.subheader("المتنافسون")

    num_bidders = st.number_input(
        "عدد المتنافسين",
        min_value=1,
        max_value=50,
        value=len(st.session_state.bidders),
        step=1
    )

    while len(st.session_state.bidders) < num_bidders:
        st.session_state.bidders.append({
            "company_name": "",
            "representative": "",
            "admin_file": True,
            "technical_file": True,
            "financial_file": True,
            "offer_amount": 0.0,
        })

    while len(st.session_state.bidders) > num_bidders:
        st.session_state.bidders.pop()

    for i, bidder in enumerate(st.session_state.bidders):
        st.markdown(f"### المتنافس {i+1}")
        c1, c2 = st.columns(2)
        bidder["company_name"] = c1.text_input(
            "اسم الشركة / المتنافس",
            value=bidder["company_name"],
            key=f"company_name_{i}"
        )
        bidder["representative"] = c2.text_input(
            "اسم الممثل",
            value=bidder["representative"],
            key=f"representative_{i}"
        )

        c3, c4, c5 = st.columns(3)
        bidder["admin_file"] = c3.checkbox(
            "ملف إداري",
            value=bidder["admin_file"],
            key=f"admin_file_{i}"
        )
        bidder["technical_file"] = c4.checkbox(
            "ملف تقني",
            value=bidder["technical_file"],
            key=f"technical_file_{i}"
        )
        bidder["financial_file"] = c5.checkbox(
            "عرض مالي",
            value=bidder["financial_file"],
            key=f"financial_file_{i}"
        )

        bidder["offer_amount"] = st.number_input(
            "مبلغ العرض",
            min_value=0.0,
            value=float(bidder["offer_amount"]),
            step=1000.0,
            key=f"offer_amount_{i}"
        )

    st.success("تم تحديث بيانات المتنافسين.")

# ----------------------------
# Page 4: Generate minutes
# ----------------------------
elif page == "توليد المحضر":
    st.subheader("توليد محضر فتح الأظرفة")

    data = {
        **st.session_state.base_data,
        "committee": st.session_state.committee,
        "bidders": st.session_state.bidders,
    }

    if st.button("إنشاء المحضر"):
        required_fields = [
            data["reference_number"],
            data["title"],
            data["owner_entity"],
            data["session_place"],
            data["president"],
        ]

        if any(not str(x).strip() for x in required_fields):
            st.error("يرجى ملء جميع الحقول الأساسية قبل توليد المحضر.")
        else:
            minutes_text = build_opening_minutes(data)

            st.success("تم إنشاء المحضر بنجاح.")
            st.text_area("نص المحضر", minutes_text, height=400)

            st.download_button(
                label="تحميل المحضر بصيغة TXT",
                data=minutes_text,
                file_name="minutes_opening.txt",
                mime="text/plain"
            )
