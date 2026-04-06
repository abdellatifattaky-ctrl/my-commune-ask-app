import io
from pathlib import Path
from datetime import date

import streamlit as st
from docxtpl import DocxTemplate


st.set_page_config(page_title="Générateur des marchés", layout="wide")


# =========================================================
# CONFIG
# =========================================================
TEMPLATE_DIR = Path("templates")


# =========================================================
# HELPERS
# =========================================================
def fmt_date(d):
    return d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d)


def init_state():
    defaults = {
        "commune": "COMMUNE ASKAOUEN",
        "province": "PROVINCE DE TAROUDANT",
        "cercle": "CERCLE TALIOUINE",
        "caidat": "CAIDAT ASKAOUEN",
        "reference": "",
        "objet": "",
        "decision_no": "",
        "decision_date": date.today(),
        "session_date": date.today(),
        "session_time": "10:00",
        "session_place": "Salle de réunion de la Commune",
        "estimation": 0.0,
        "president": "",
        "publication_1": "",
        "publication_2": "",
        "portail_publication": "",
        "reprise_date": date.today(),
        "reprise_time": "10:00",
        "complement_limit_days": 7,
        "signature_place": "ASKAOUEN",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "committee" not in st.session_state:
        st.session_state.committee = [
            {"name": "", "quality": "Président de la commune", "role": "PRESIDENT"},
            {"name": "", "quality": "Représentant du percepteur", "role": "MEMBRE"},
            {"name": "", "quality": "Directeur des services", "role": "MEMBRE"},
            {"name": "", "quality": "Technicien", "role": "MEMBRE"},
            {"name": "", "quality": "Service des marchés", "role": "MEMBRE"},
        ]

    if "subcommittee" not in st.session_state:
        st.session_state.subcommittee = [
            {"name": "", "quality": "Technicien à la commune"},
            {"name": "", "quality": "Technicien à la commune"},
            {"name": "", "quality": "Technicien à la commune"},
        ]

    if "bidders" not in st.session_state:
        st.session_state.bidders = [
            {
                "name": "",
                "admin_ok": True,
                "tech_ok": True,
                "tech_score": 70.0,
                "amount": 0.0,
                "amount_rectified": 0.0,
                "excluded_reason_admin": "",
                "excluded_reason_tech": "",
                "complement_sent": "",
                "complement_received": "",
            }
        ]


def committee_lines():
    rows = []
    for m in st.session_state.committee:
        if m["name"].strip():
            rows.append({
                "name": m["name"],
                "quality": m["quality"],
                "role": m["role"],
            })
    return rows


def subcommittee_lines():
    rows = []
    for m in st.session_state.subcommittee:
        if m["name"].strip():
            rows.append({
                "name": m["name"],
                "quality": m["quality"],
            })
    return rows


def bidders_all():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip():
            rows.append({"name": b["name"]})
    return rows


def bidders_admin_excluded():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["excluded_reason_admin"].strip():
            rows.append({
                "name": b["name"],
                "reason": b["excluded_reason_admin"],
            })
    return rows


def bidders_tech_excluded():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["excluded_reason_tech"].strip():
            rows.append({
                "name": b["name"],
                "reason": b["excluded_reason_tech"],
            })
    return rows


def admissible_admin():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["admin_ok"] and not b["excluded_reason_admin"].strip():
            rows.append({"name": b["name"]})
    return rows


def admissible_tech():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70 and not b["excluded_reason_tech"].strip():
            rows.append({"name": b["name"]})
    return rows


def technical_scores():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["admin_ok"]:
            rows.append({
                "name": b["name"],
                "score": b["tech_score"],
            })
    return rows


def financial_offers():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70:
            rows.append({
                "name": b["name"],
                "amount": f"{b['amount']:,.2f} DHS",
            })
    return rows


def rectified_offers():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70:
            rectified = b["amount_rectified"] if b["amount_rectified"] > 0 else b["amount"]
            rows.append({
                "name": b["name"],
                "amount_before": f"{b['amount']:,.2f} DHS",
                "amount_after": f"{rectified:,.2f} DHS",
            })
    return rows


def reference_price_data():
    amounts = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70:
            value = b["amount_rectified"] if b["amount_rectified"] > 0 else b["amount"]
            amounts.append((b["name"], value))

    if not amounts:
        return 0.0, [], None

    ref = (st.session_state.estimation + sum(v for _, v in amounts)) / (len(amounts) + 1)
    ranking = sorted(amounts, key=lambda x: abs(x[1] - ref))
    winner = ranking[0] if ranking else None
    return ref, amounts, winner


def ranking_rows():
    ref, amounts, winner = reference_price_data()
    rows = []
    for i, (name, amount) in enumerate(sorted(amounts, key=lambda x: abs(x[1] - ref)), start=1):
        rows.append({
            "rank": i,
            "name": name,
            "amount": f"{amount:,.2f} DHS",
        })
    return rows


def build_context(company_name=""):
    ref, amounts, winner = reference_price_data()
    winner_name = winner[0] if winner else ""
    winner_amount = f"{winner[1]:,.2f} DHS" if winner else ""

    invited = next((b for b in st.session_state.bidders if b["name"] == winner_name), None)
    complement_sent = invited["complement_sent"] if invited else ""
    complement_received = invited["complement_received"] if invited else ""

    return {
        "commune": st.session_state.commune,
        "province": st.session_state.province,
        "cercle": st.session_state.cercle,
        "caidat": st.session_state.caidat,
        "reference": st.session_state.reference,
        "objet": st.session_state.objet,
        "decision_no": st.session_state.decision_no,
        "decision_date": fmt_date(st.session_state.decision_date),
        "session_date": fmt_date(st.session_state.session_date),
        "session_time": st.session_state.session_time,
        "session_place": st.session_state.session_place,
        "estimation": f"{st.session_state.estimation:,.2f} DHS TTC",
        "president": st.session_state.president,
        "publication_1": st.session_state.publication_1,
        "publication_2": st.session_state.publication_2,
        "portail_publication": st.session_state.portail_publication,
        "reprise_date": fmt_date(st.session_state.reprise_date),
        "reprise_time": st.session_state.reprise_time,
        "signature_place": st.session_state.signature_place,
        "complement_limit_days": st.session_state.complement_limit_days,
        "committee": committee_lines(),
        "subcommittee": subcommittee_lines(),
        "bidders": bidders_all(),
        "excluded_admin": bidders_admin_excluded(),
        "excluded_tech": bidders_tech_excluded(),
        "admissible_admin": admissible_admin(),
        "admissible_tech": admissible_tech(),
        "technical_scores": technical_scores(),
        "financial_offers": financial_offers(),
        "rectified_offers": rectified_offers(),
        "ranking_rows": ranking_rows(),
        "reference_price": f"{ref:,.2f} DHS" if ref else "",
        "winner_name": winner_name,
        "winner_amount": winner_amount,
        "company_name": company_name or winner_name,
        "complement_sent": complement_sent,
        "complement_received": complement_received,
    }


def render_template(template_name, context):
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template introuvable: {template_path}")

    doc = DocxTemplate(template_path)
    doc.render(context)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()


# =========================================================
# UI
# =========================================================
init_state()
st.title("📄 Générateur des PV des marchés publics - Version Templates")

tab1, tab2, tab3, tab4 = st.tabs(["Données générales", "Commission", "Concurrents", "Génération"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.session_state.commune = st.text_input("Commune", st.session_state.commune)
        st.session_state.province = st.text_input("Province", st.session_state.province)
        st.session_state.cercle = st.text_input("Cercle", st.session_state.cercle)
        st.session_state.caidat = st.text_input("Caidat", st.session_state.caidat)
        st.session_state.reference = st.text_input("Référence AO / marché", st.session_state.reference)
        st.session_state.objet = st.text_area("Objet", st.session_state.objet, height=120)
        st.session_state.estimation = st.number_input("Estimation TTC (DHS)", min_value=0.0, value=float(st.session_state.estimation), step=1000.0)

    with c2:
        st.session_state.decision_no = st.text_input("N° décision ordonnateur", st.session_state.decision_no)
        st.session_state.decision_date = st.date_input("Date décision", value=st.session_state.decision_date, key="decision_date_widget")
        st.session_state.session_date = st.date_input("Date séance", value=st.session_state.session_date, key="session_date_widget")
        st.session_state.session_time = st.text_input("Heure séance", st.session_state.session_time)
        st.session_state.session_place = st.text_input("Lieu séance", st.session_state.session_place)
        st.session_state.president = st.text_input("Président maître d’ouvrage", st.session_state.president)
        st.session_state.publication_1 = st.text_input("Publication journal 1", st.session_state.publication_1)
        st.session_state.publication_2 = st.text_input("Publication journal 2", st.session_state.publication_2)
        st.session_state.portail_publication = st.text_input("Publication portail marchés publics", st.session_state.portail_publication)
        st.session_state.reprise_date = st.date_input("Date reprise", value=st.session_state.reprise_date, key="reprise_date_widget")
        st.session_state.reprise_time = st.text_input("Heure reprise", st.session_state.reprise_time)
        st.session_state.signature_place = st.text_input("Lieu signature", st.session_state.signature_place)

with tab2:
    st.subheader("Commission")
    committee_n = st.number_input("Nombre de membres", min_value=1, max_value=10, value=len(st.session_state.committee), step=1)

    while len(st.session_state.committee) < committee_n:
        st.session_state.committee.append({"name": "", "quality": "", "role": "MEMBRE"})
    while len(st.session_state.committee) > committee_n:
        st.session_state.committee.pop()

    for i, m in enumerate(st.session_state.committee):
        a, b, c = st.columns([2, 2, 1])
        m["name"] = a.text_input(f"Nom membre {i+1}", m["name"], key=f"cm_name_{i}")
        m["quality"] = b.text_input(f"Qualité {i+1}", m["quality"], key=f"cm_quality_{i}")
        m["role"] = c.selectbox(f"Rôle {i+1}", ["PRESIDENT", "MEMBRE"], index=0 if m["role"] == "PRESIDENT" else 1, key=f"cm_role_{i}")

    st.subheader("Sous-commission technique")
    sub_n = st.number_input("Nombre membres sous-commission", min_value=1, max_value=5, value=len(st.session_state.subcommittee), step=1)

    while len(st.session_state.subcommittee) < sub_n:
        st.session_state.subcommittee.append({"name": "", "quality": "Technicien à la commune"})
    while len(st.session_state.subcommittee) > sub_n:
        st.session_state.subcommittee.pop()

    for i, m in enumerate(st.session_state.subcommittee):
        a, b = st.columns(2)
        m["name"] = a.text_input(f"Nom sous-commission {i+1}", m["name"], key=f"scm_name_{i}")
        m["quality"] = b.text_input(f"Qualité sous-commission {i+1}", m["quality"], key=f"scm_quality_{i}")

with tab3:
    st.subheader("Concurrents")
    bid_n = st.number_input("Nombre de concurrents", min_value=1, max_value=20, value=len(st.session_state.bidders), step=1)

    while len(st.session_state.bidders) < bid_n:
        st.session_state.bidders.append({
            "name": "",
            "admin_ok": True,
            "tech_ok": True,
            "tech_score": 70.0,
            "amount": 0.0,
            "amount_rectified": 0.0,
            "excluded_reason_admin": "",
            "excluded_reason_tech": "",
            "complement_sent": "",
            "complement_received": "",
        })
    while len(st.session_state.bidders) > bid_n:
        st.session_state.bidders.pop()

    for i, b in enumerate(st.session_state.bidders):
        st.markdown(f"### Concurrent {i+1}")
        c1, c2 = st.columns(2)
        b["name"] = c1.text_input("Nom", b["name"], key=f"bid_name_{i}")
        b["tech_score"] = c2.number_input("Note technique", min_value=0.0, max_value=100.0, value=float(b["tech_score"]), step=1.0, key=f"bid_score_{i}")

        c3, c4 = st.columns(2)
        b["admin_ok"] = c3.checkbox("Admis administratif", value=b["admin_ok"], key=f"bid_admin_{i}")
        b["tech_ok"] = c4.checkbox("Admis technique", value=b["tech_ok"], key=f"bid_tech_{i}")

        c5, c6 = st.columns(2)
        b["amount"] = c5.number_input("Montant engagement", min_value=0.0, value=float(b["amount"]), step=1000.0, key=f"bid_amount_{i}")
        b["amount_rectified"] = c6.number_input("Montant rectifié", min_value=0.0, value=float(b["amount_rectified"]), step=1000.0, key=f"bid_amount_rect_{i}")

        c7, c8 = st.columns(2)
        b["excluded_reason_admin"] = c7.text_input("Motif écartement administratif", b["excluded_reason_admin"], key=f"bid_exc_admin_{i}")
        b["excluded_reason_tech"] = c8.text_input("Motif écartement technique", b["excluded_reason_tech"], key=f"bid_exc_tech_{i}")

        c9, c10 = st.columns(2)
        b["complement_sent"] = c9.text_input("Date envoi invitation complément", b["complement_sent"], key=f"bid_sent_{i}")
        b["complement_received"] = c10.text_input("Date dépôt complément", b["complement_received"], key=f"bid_received_{i}")

with tab4:
    st.subheader("Génération à partir des templates Word originaux")

    doc_type = st.selectbox(
        "Choisir le document",
        [
            "PV 1ère séance",
            "Rapport sous-commission",
            "PV 2ème séance",
            "PV 3ème séance",
            "OS notification",
            "OS commencement",
        ]
    )

    template_map = {
        "PV 1ère séance": "template_pv1.docx",
        "Rapport sous-commission": "template_rapport.docx",
        "PV 2ème séance": "template_pv2.docx",
        "PV 3ème séance": "template_pv3.docx",
        "OS notification": "template_os_notification.docx",
        "OS commencement": "template_os_commencement.docx",
    }

    ref, _, winner = reference_price_data()
    if winner:
        st.info(f"Offre la plus proche du prix de référence ({ref:,.2f} DHS) : {winner[0]} - {winner[1]:,.2f} DHS")

    winner_name = winner[0] if winner else ""
    company_name = st.text_input("Entreprise concernée", value=winner_name)

    template_file = template_map[doc_type]
    st.write(f"Template utilisé : `templates/{template_file}`")

    if st.button("Générer Word depuis le template"):
        try:
            context = build_context(company_name)
            docx_bytes = render_template(template_file, context)

            safe_name = doc_type.lower().replace(" ", "_").replace("è", "e").replace("é", "e")
            st.success("Document généré avec succès à partir du template original.")
            st.download_button(
                "Télécharger Word (.docx)",
                docx_bytes,
                file_name=f"{safe_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Erreur : {e}")
