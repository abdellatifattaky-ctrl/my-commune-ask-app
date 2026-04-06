import io
from datetime import date

import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


st.set_page_config(page_title="Générateur des marchés publics", layout="wide")


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
        "signature_place": "ASKAOUEN",
        "company_name": "",
        "complement_limit_days": 7,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "committee" not in st.session_state:
        st.session_state.committee = [
            {"name": "", "quality": "Président de la commune", "role": "PRESIDENT"},
            {"name": "", "quality": "Représentant du percepteur", "role": "MEMBRE"},
            {"name": "", "quality": "Directeur des services", "role": "MEMBRE"},
            {"name": "", "quality": "Technicien à la commune", "role": "MEMBRE"},
            {"name": "", "quality": "Service des marchés", "role": "MEMBRE"},
        ]

    if "subcommittee" not in st.session_state:
        st.session_state.subcommittee = [
            {"name": "", "quality": "technicien à la commune"},
            {"name": "", "quality": "technicien à la commune"},
            {"name": "", "quality": "technicien à la commune"},
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
    lines = []
    for m in st.session_state.committee:
        if m["name"].strip():
            lines.append(f"· {m['name']} : {m['quality']} --------------------------- {m['role']}")
    return "\n".join(lines) if lines else "NEANT"


def subcommittee_lines():
    lines = []
    for m in st.session_state.subcommittee:
        if m["name"].strip():
            lines.append(f"· {m['name']} : {m['quality']}")
    return "\n".join(lines) if lines else "NEANT"


def bidder_lines():
    lines = []
    for i, b in enumerate([x for x in st.session_state.bidders if x["name"].strip()], start=1):
        lines.append(f"{i}) {b['name']}")
    return "\n".join(lines) if lines else "NEANT"


def excluded_admin_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["excluded_reason_admin"].strip():
            rows.append(f"{b['name']} | {b['excluded_reason_admin']}")
    return "\n".join(rows) if rows else "NEANT | NEANT"


def excluded_tech_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["excluded_reason_tech"].strip():
            rows.append(f"{b['name']} | {b['excluded_reason_tech']}")
    return "\n".join(rows) if rows else "NEANT | NEANT"


def admissible_admin_lines():
    rows = []
    idx = 1
    for b in st.session_state.bidders:
        if b["name"].strip() and b["admin_ok"] and not b["excluded_reason_admin"].strip():
            rows.append(f"{idx}) {b['name']}")
            idx += 1
    return "\n".join(rows) if rows else "NEANT"


def admissible_tech_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70 and not b["excluded_reason_tech"].strip():
            rows.append(f"· {b['name']}")
    return "\n".join(rows) if rows else "NEANT"


def technical_scores_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["admin_ok"]:
            rows.append(f"{b['name']} | {b['tech_score']}")
    return "\n".join(rows) if rows else "NEANT | 0"


def financial_offers_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70:
            rows.append(f"{b['name']} | {b['amount']:,.2f} DHS")
    return "\n".join(rows) if rows else "NEANT | 0 DHS"


def rectified_offers_lines():
    rows = []
    for b in st.session_state.bidders:
        if b["name"].strip() and b["tech_ok"] and b["tech_score"] >= 70:
            rectified = b["amount_rectified"] if b["amount_rectified"] > 0 else b["amount"]
            rows.append(f"{b['name']} | {b['amount']:,.2f} DHS | {rectified:,.2f} DHS")
    return "\n".join(rows) if rows else "NEANT | 0 DHS | 0 DHS"


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


def ranking_lines():
    ref, amounts, _ = reference_price_data()
    rows = []
    for i, (name, amount) in enumerate(sorted(amounts, key=lambda x: abs(x[1] - ref)), start=1):
        rows.append(f"{i}. Offre financier {name} = {amount:,.2f} DHS")
    return "\n".join(rows) if rows else "NEANT"


def current_winner():
    _, _, winner = reference_price_data()
    if winner:
        return winner[0], f"{winner[1]:,.2f} DHS"
    return "", ""


# =========================================================
# TEXT TEMPLATES
# =========================================================
def render_pv1():
    return f"""ROYAUME DU MAROC

MINISTERE DE L’INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

PROCES VERBAL D'APPEL D'OFFRES OUVERT

SUR OFFRE DE PRIX N° : {st.session_state.reference}
1ère Séance Publique

Le {fmt_date(st.session_state.session_date)} à {st.session_state.session_time}, une commission d’appel d’offres, conformément à la décision de l’ordonnateur n° {st.session_state.decision_no} du {fmt_date(st.session_state.decision_date)}, est composée comme suit :

{committee_lines()}

S’est réunie en séance publique dans {st.session_state.session_place}, en vue de procéder à l’ouverture des plis concernant l’appel d’offres ouvert national sur offre de prix N°: {st.session_state.reference}, relatif à : {st.session_state.objet}.

Conformément à l’avis publié dans les journaux suivants :
· {st.session_state.publication_1 or '................................'}
· {st.session_state.publication_2 or '................................'}
La mise en ligne au portail des marchés publics : {st.session_state.portail_publication or '................................'}

Le président cite les concurrents ayant envoyé leurs plis :
{bidder_lines()}

Le président s’assure de la présence des membres dont la présence est obligatoire.
Le président remet le support écrit contenant l’estimation des coûts détaillés des prestations dont le montant est fixé à {st.session_state.estimation:,.2f} DHS TTC.
Les membres de la commission paraphent le support de l’estimation des coûts des prestations.

Le président demande aux membres de la commission de formuler leurs réserves ou observations sur les vices éventuels qui entachent la procédure.
Le président ouvre les enveloppes extérieures des plis contenant les dossiers des concurrents, cite dans chacun la présence des enveloppes exigées. Il ouvre ensuite l’enveloppe portant la mention « dossiers administratif et technique ».

Cette formalité accomplie, la séance publique est suspendue, les concurrents et le public se retirent de la salle.

Ensuite, la commission se réunit à huis clos pour examiner les dossiers administratifs et techniques des concurrents, elle écarte les concurrents ci-après pour les motifs suivants :
Concurrents | MOTIF D’ECARTEMENT
{excluded_admin_lines()}

Elle arrête ensuite la liste des concurrents admissibles :
A- Liste des concurrents admissibles sans réserves :
{admissible_admin_lines()}
B- Liste des concurrents admissibles avec réserves :
Néant

La séance publique est alors reprise et le président donne lecture de la liste des soumissionnaires admissibles.
Le président procède ensuite à l’ouverture des enveloppes des soumissionnaires retenus portant la mention « offres Technique ».

Cette formalité accomplie, la séance publique est suspendue, les concurrents et le public se retirent de la salle.

Ensuite, la commission se réunit à huis clos pour examiner les dossiers d’offres Technique des concurrents, elle écarte les concurrents ci-après pour les motifs suivants :
Concurrents | MOTIF D’ECARTEMENT
{excluded_tech_lines()}

Elle arrête ensuite la liste des concurrents admissibles :
A- Liste des concurrents admissibles sans réserves :
{admissible_tech_lines()}
B- Liste des concurrents admissibles avec réserves :
Néant

Ensuite, et conformément aux dispositions de l’article 38 du décret n°2-22-431 du 08 mars 2023 relatif aux marchés publics, la commission a décidé de consulter une sous-commission technique pour examiner et analyser les offres techniques fournis par les concurrents.
La sous-commission technique est composée de :

{subcommittee_lines()}

Le président de la commission suspend la séance et fixe la date de {fmt_date(st.session_state.reprise_date)} à {st.session_state.reprise_time} pour la reprise des travaux de la séance.

Fait à {st.session_state.signature_place} le : {fmt_date(st.session_state.session_date)}

APPEL D’OFFRES OUVERT NATIONAL
N° {st.session_state.reference} (1ère Séance Publique)
Objet : {st.session_state.objet}

SIGNE : LE PRESIDENT

LES MEMBRES
""".strip()


def render_pv2():
    ref, amounts, winner = reference_price_data()
    winner_name = winner[0] if winner else "................................"
    winner_amount = f"{winner[1]:,.2f} DHS" if winner else "................................"

    financial_calc = "\n".join(
        [f"· Offre financier {n} = {v:,.2f} DHS" for n, v in amounts]
    ) if amounts else "· Aucune offre admissible"

    return f"""ROYAUME DU MAROC

MINISTERE DE L’INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

PROCES VERBAL D'APPEL D'OFFRES OUVERT

SUR OFFRE DE PRIX N° : {st.session_state.reference}
2eme Séance Publique

Conformément à la décision de l’ordonnateur n° {st.session_state.decision_no} du {fmt_date(st.session_state.decision_date)}, le {fmt_date(st.session_state.reprise_date)} à {st.session_state.reprise_time}, la commission d’appel d’offres ouvert national sur offre de prix N°: {st.session_state.reference}, relatif à : {st.session_state.objet}, composée comme suit :

{committee_lines()}

S’est réunie en séance publique dans la salle de réunion de la Commune {st.session_state.commune}, Province {st.session_state.province}, Cercle {st.session_state.cercle}, Caidat {st.session_state.caidat}, en vue d’étudier le rapport de la sous-commission technique daté {fmt_date(st.session_state.reprise_date)} à {st.session_state.reprise_time} qui examine et analyse les offres techniques fournis par les concurrents admissibles suite à l’étude des dossiers administratifs.

Conformément aux critères d’évaluation des offres les concurrents ayant obtenu une note inférieure à (70 points) seront écartés.

Donne lecture de la liste et les notes des offres techniques des concurrents admissibles comme suit :
CONCURRENTS | Note Technique (Nt)
{technical_scores_lines()}

Elle arrête ensuite la liste des concurrents admissibles :
A- Liste des concurrents admissibles sans réserves :
{admissible_tech_lines()}
B- Liste des concurrents admissibles avec réserves :
Néant

La séance publique est alors reprise et le président donne lecture de la liste des soumissionnaires admissibles.

Le président procède ensuite à l’ouverture des enveloppes des concurrents admissibles portant la mention < offres financières > et donne lecture de la teneur des actes d’engagement, comme suit :

Concurrents | Montant des actes d’engagement
{financial_offers_lines()}

La commission poursuit alors ses travaux à huis clos.
Elle procède ensuite à la vérification des opérations arithmétiques des offres des concurrents admissibles et rectifie les erreurs de calcul relevées dans leurs actes d’engagement.

Ces rectifications donnent les résultats suivants :
Concurrents | Montant avant rectification | Montant rectifié
{rectified_offers_lines()}

Elle procède au calcul du prix de référence comme suit :

· Estimation = {st.session_state.estimation:,.2f} DHS
{financial_calc}
· Le prix de référence = {ref:,.2f} DHS

La commission procède au classement des offres des concurrents au regard du prix de référence :
{ranking_lines()}

L’offre économiquement la plus avantageuse à proposer au maître d’ouvrage est celle qui est la plus proche par défaut du prix de référence, qui est celle présentée par {winner_name} = {winner_amount}.

La commission invite, par voie électronique, le concurrent ayant présenté l’offre économiquement la plus avantageuse, dans un délai de {st.session_state.complement_limit_days} jours, à produire le complément du dossier administratif.

Le président de la commission suspend la séance et fixe la date de {fmt_date(st.session_state.session_date)} à {st.session_state.session_time} pour la reprise des travaux de la séance.

Le président de la commission

APPEL D’OFFRES OUVERT NATIONAL
N° {st.session_state.reference} (2eme Séance Publique)
Objet : {st.session_state.objet}

SIGNE : LE PRESIDENT
LES MEMBRES
""".strip()


def render_pv3():
    winner_name, winner_amount = current_winner()
    invited = next((b for b in st.session_state.bidders if b["name"] == winner_name), None)
    complement_sent = invited["complement_sent"] if invited else ""
    complement_received = invited["complement_received"] if invited else ""

    return f"""ROYAUME DU MAROC

MINISTERE DE L’INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

PROCES VERBAL D'APPEL D'OFFRES OUVERT

SUR OFFRE DE PRIX N° : {st.session_state.reference}

3eme Séance Publique
Le {fmt_date(st.session_state.session_date)} à {st.session_state.session_time}, une commission d’appel d’offres, conformément à la décision de l’ordonnateur n° {st.session_state.decision_no} du {fmt_date(st.session_state.decision_date)}, et composée comme suit :

{committee_lines()}

S’est réunie en séance publique dans la salle de réunion de la Commune {st.session_state.commune} Province {st.session_state.province}, Cercle {st.session_state.cercle}, Caidat {st.session_state.caidat}, en vue de procéder à l’ouverture des plis concernant du complément du dossier administratif de l’attributaire de l’appel d’offres ouvert national sur offre de prix N°: {st.session_state.reference}, relatif à : {st.session_state.objet}.

La commission s’assure du support ayant servi de moyen d’invitation du concurrent concerné {winner_name} : Date d'envoi de la lettre : {complement_sent or '................................'}
Elle vérifie les pièces et la réponse reçue : Dossier déposé le {complement_received or '................................'}

La commission examine les pièces complémentaires du dossier administratif et la réponse reçue et les juge acceptables, et décide de proposer au maître d’ouvrage de retenir l’offre du concurrent ayant présenté l’offre la plus avantageuse, est l’offre présentée par {winner_name} qui s’élevé à la somme de {winner_amount}

{st.session_state.signature_place} le : {fmt_date(st.session_state.session_date)}
APPEL D’OFFRES OUVERT NATIONAL

N° {st.session_state.reference} (3eme Séance Publique)
Objet : {st.session_state.objet}
SIGNE : LE PRESIDENT

LES MEMBRES
""".strip()


def render_rapport():
    passed = [b["name"] for b in st.session_state.bidders if b["name"].strip() and b["tech_score"] >= 70]
    failed = [b["name"] for b in st.session_state.bidders if b["name"].strip() and b["tech_score"] < 70]

    passed_text = "\n".join([f"· {x}" for x in passed]) if passed else "NEANT"
    failed_text = "\n".join([f"· {x}" for x in failed]) if failed else "NEANT"

    return f"""ROYAUME DU MAROC

MINISTERE DE L’INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

Rapport de la sous-commission technique

Appel d’offres ouvert {st.session_state.reference}

{st.session_state.objet}
EXAMEN DES OFFRES TECHNIQUES

Le {fmt_date(st.session_state.reprise_date)} à ({st.session_state.reprise_time}) Heures faisant suite à la séance d’ouverture des plis et à la décision du président de la commission d’ouverture des plis de désigner une sous-commission technique, et cela conformément à l’article 38 du décret 2-22-431 relatif aux marchés publics pour examiner et analyser les offres techniques fournis par les concurrents admis après l’étude des dossiers administratifs.

Cette sous-commission technique est composée de :

{subcommittee_lines()}

Ladite sous-commission s’est réunie à la date et l’heure susmentionnées ci-dessus pour examiner les éléments de l’OFFRE TECHNIQUE.

La liste des concurrents présentés par la commission d’ouverture pour l’examen des offres techniques est composée des concurrents suivants :

{bidder_lines()}

Conclusion :
Après l’examen des offres techniques des concurrents :
La sous-commission technique arrête la liste des concurrents dont la note des offres techniques est supérieure à la note technique limite fixé par le règlement de consultation à 70 points à savoir :
{passed_text}

La sous-commission technique arrête la liste des concurrents dont la note des offres techniques est inférieure à 70 points à savoir :
{failed_text}

Vous trouverez ci-joint les fiches de notation détaillées pour chaque concurrent.
Fiche de notation et évaluation de la sous-commission technique :
{technical_scores_lines()}

Le présent rapport est établi pour servir d’outil à la commission d’ouverture des plis pour fonder son choix quant au rejet ou à l’acceptation de l’offre concernée.

LES MEMBRES
""".strip()


def render_os_notification():
    company = st.session_state.company_name or current_winner()[0] or "................................"
    return f"""ROYAUME DU MAROC

MINISTERE DE L'INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

ORDRE DE SERVICE DE LA NOTIFICATION

DE L’APPROBATION DU MARCHE N°: {st.session_state.reference}

Le maître d’ouvrage représenté par {st.session_state.president} en qualité du président de la commune {st.session_state.commune}.

Informe

{company} que le marché qu’il a signé avec la commune {st.session_state.commune} ayant pour objet : {st.session_state.objet}
Est approuvé à la date du {fmt_date(st.session_state.session_date)}

Par conséquent, l'intéressé est invité à acquitter les droits de timbre dus au titre du présent marché conformément à la législation en vigueur.

Le présent ordre de service, certifié conforme à la minute, sera notifié à {company}.

A {st.session_state.signature_place}, Le {fmt_date(st.session_state.session_date)}

Le président :
""".strip()


def render_os_commencement():
    company = st.session_state.company_name or current_winner()[0] or "................................"
    return f"""ROYAUME DU MAROC

MINISTERE DE L'INTERIEUR

{st.session_state.province}
{st.session_state.cercle}
{st.session_state.caidat}
{st.session_state.commune}

ORDRE DE SERVICE A L’ENTREPRENEUR POUR

COMMENCEMENT DES TRAVAUX {st.session_state.reference}

Le maître d’ouvrage représenté par {st.session_state.president} en qualité du président de la commune {st.session_state.commune}.

Informe

{company} que le marché qu’il a signé avec la commune {st.session_state.commune} ayant pour objet : {st.session_state.objet} est approuvé.

Par conséquent, l'intéressé est invité à commencer les travaux objet du présent marché à compter du : {fmt_date(st.session_state.session_date)}

Le présent ordre de service sera notifié à {company}

A {st.session_state.signature_place}, Le {fmt_date(st.session_state.session_date)}

Le président :
""".strip()


# =========================================================
# DOCX EXPORT
# =========================================================
def text_to_docx_bytes(title, content):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Pt(42)
    section.bottom_margin = Pt(42)
    section.left_margin = Pt(50)
    section.right_margin = Pt(50)

    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)

    for line in content.splitlines():
        p = doc.add_paragraph()
        stripped = line.strip()

        if stripped.startswith("ROYAUME DU MAROC") or stripped.startswith("MINISTERE"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif stripped.startswith("PROCES VERBAL") or stripped.startswith("ORDRE DE SERVICE") or stripped.startswith("Rapport"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        run = p.add_run(line)
        run.font.name = "Arial"
        run.font.size = Pt(11)
        if (
            stripped.startswith("PROCES VERBAL")
            or stripped.startswith("ORDRE DE SERVICE")
            or stripped.startswith("Rapport")
            or stripped.startswith("SIGNE")
            or stripped.startswith("LES MEMBRES")
        ):
            run.bold = True

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()


# =========================================================
# UI
# =========================================================
init_state()
st.title("📄 Générateur des marchés publics")

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
        st.session_state.company_name = st.text_input("Entreprise concernée (OS)", st.session_state.company_name)

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
        st.session_state.subcommittee.append({"name": "", "quality": "technicien à la commune"})
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
    st.subheader("Génération")
    ref, _, winner = reference_price_data()
    if winner:
        st.info(f"Offre la plus proche du prix de référence ({ref:,.2f} DHS) : {winner[0]} - {winner[1]:,.2f} DHS")

    doc_type = st.selectbox(
        "Choisir le document",
        [
            "PV 1ère séance",
            "PV 2ème séance",
            "PV 3ème séance",
            "Rapport sous-commission",
            "OS notification",
            "OS commencement",
        ]
    )

    generators = {
        "PV 1ère séance": render_pv1,
        "PV 2ème séance": render_pv2,
        "PV 3ème séance": render_pv3,
        "Rapport sous-commission": render_rapport,
        "OS notification": render_os_notification,
        "OS commencement": render_os_commencement,
    }

    if st.button("Générer"):
        text = generators[doc_type]()
        st.text_area("Document généré", text, height=500)

        safe_name = doc_type.lower().replace(" ", "_").replace("è", "e").replace("é", "e")

        st.download_button(
            "Télécharger TXT",
            text,
            file_name=f"{safe_name}.txt",
            mime="text/plain"
        )

        docx_bytes = text_to_docx_bytes(doc_type, text)
        st.download_button(
            "Télécharger Word (.docx)",
            docx_bytes,
            file_name=f"{safe_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
