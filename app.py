elif menu == "الصفقات العمومية":
    st.markdown('<div class="section-title">تدبير الصفقات العمومية SMART PRO+</div>', unsafe_allow_html=True)

    def init_procurement_smart_tables():
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS market_master_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                market_object TEXT,
                market_owner TEXT,
                president_name TEXT,
                commune_name TEXT,
                province_name TEXT,
                cercle_name TEXT,
                caidat_name TEXT,
                decision_ref TEXT,
                decision_date TEXT,
                publication_portal_date TEXT,
                publication_newspaper_1 TEXT,
                publication_newspaper_2 TEXT,
                publication_newspaper_1_date TEXT,
                publication_newspaper_2_date TEXT,
                opening_date TEXT,
                opening_time TEXT,
                opening_place TEXT,
                estimate_amount REAL,
                estimate_amount_words TEXT,
                rc_article_ref TEXT,
                cps_article_ref TEXT,
                company_awarded TEXT,
                company_representative TEXT,
                company_quality TEXT,
                company_address TEXT,
                approval_date TEXT,
                os_register_number TEXT,
                notification_date TEXT,
                commencement_date TEXT,
                complement_file_date TEXT,
                invitation_date TEXT,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS market_commission_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                member_name TEXT,
                member_role TEXT,
                member_quality TEXT,
                member_order_num INTEGER,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS market_subcommission_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                member_name TEXT,
                member_role TEXT,
                member_quality TEXT,
                member_order_num INTEGER,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS market_competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                competitor_name TEXT,
                submitted_electronically TEXT,
                admin_status TEXT,
                technical_status TEXT,
                technical_score REAL,
                financial_offer REAL,
                corrected_offer REAL,
                remarks TEXT,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS market_doc_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_ref TEXT,
                doc_type TEXT,
                doc_number INTEGER,
                created_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    init_procurement_smart_tables()

    def format_amount_words_fr(value):
        try:
            val = float(value)
            words = num2words(val, lang="fr").upper()
            cents = int(round((val - int(val)) * 100))
            text = f"{words} DIRHAMS"
            if cents > 0:
                text += f" ET {num2words(cents, lang='fr').upper()} CENTIMES"
            else:
                text += " ,00 CTS"
            return text
        except Exception:
            return "________________"

    def fmt_number(value):
        try:
            return f"{float(value):,.2f}".replace(",", " ")
        except Exception:
            return str(value)

    def get_market_refs():
        rows = fetch_all(
            "SELECT market_ref FROM market_master_data WHERE market_ref IS NOT NULL AND market_ref != '' ORDER BY id DESC"
        )
        refs = []
        for r in rows:
            if r["market_ref"] not in refs:
                refs.append(r["market_ref"])
        return refs

    def get_market_data(market_ref):
        rows = fetch_all(
            "SELECT * FROM market_master_data WHERE market_ref = ? ORDER BY id DESC LIMIT 1",
            (market_ref,)
        )
        return rows[0] if rows else None

    def get_commission(market_ref):
        return fetch_all(
            "SELECT * FROM market_commission_members WHERE market_ref = ? ORDER BY member_order_num ASC, id ASC",
            (market_ref,)
        )

    def get_subcommission(market_ref):
        return fetch_all(
            "SELECT * FROM market_subcommission_members WHERE market_ref = ? ORDER BY member_order_num ASC, id ASC",
            (market_ref,)
        )

    def get_competitors(market_ref):
        return fetch_all(
            "SELECT * FROM market_competitors WHERE market_ref = ? ORDER BY id ASC",
            (market_ref,)
        )

    def corrected_value(comp):
        val = comp["corrected_offer"]
        if val in [None, "", 0]:
            return float(comp["financial_offer"] or 0)
        return float(val)

    def nearest_below_reference(ref_price, values):
        eligible = [v for v in values if v <= ref_price]
        if eligible:
            return max(eligible)
        return min(values) if values else None

    def next_doc_number(market_ref, doc_type):
        rows = fetch_all(
            "SELECT MAX(doc_number) AS max_num FROM market_doc_counter WHERE market_ref = ? AND doc_type = ?",
            (market_ref, doc_type)
        )
        max_num = rows[0]["max_num"] if rows and rows[0]["max_num"] is not None else 0
        new_num = int(max_num) + 1
        insert_record(
            "INSERT INTO market_doc_counter (market_ref, doc_type, doc_number, created_at) VALUES (?, ?, ?, ?)",
            (market_ref, doc_type, new_num, str(date.today()))
        )
        return new_num

    def style_doc(doc):
        section = doc.sections[0]
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)

    def add_top_header(doc, market):
        for line in [
            "ROYAUME DU MAROC",
            "MINISTERE DE L’INTERIEUR",
            f"PROVINCE DE {market['province_name'] or 'TAROUDANT'}",
            f"CERCLE {market['cercle_name'] or 'TALIOUINE'}",
            f"CAIDAT {market['caidat_name'] or 'ASKAOUEN'}",
            f"COMMUNE {market['commune_name'] or 'ASKAOUEN'}",
        ]:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(line).bold = True
        doc.add_paragraph("")

    def add_doc_title(doc, title, subtitle=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(14)

        if subtitle:
            p2 = doc.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r2 = p2.add_run(subtitle)
            r2.bold = True

    def add_members_block(doc, members):
        for m in members:
            doc.add_paragraph(
                f"· {m['member_name']} : {m['member_quality']} -------------------------------- {m['member_role']}"
            )

    def add_signature_table(doc, members, include_president=True):
        names = []
        if include_president:
            president = [m for m in members if "PRESIDENT" in (m["member_role"] or "").upper()]
            others = [m for m in members if m not in president]
            names.extend(president + others)
        else:
            names.extend(members)

        if not names:
            return

        cols = min(3, len(names))
        rows_needed = (len(names) + cols - 1) // cols
        table = doc.add_table(rows=rows_needed * 2, cols=cols)
        table.style = "Table Grid"

        idx = 0
        for r in range(0, rows_needed * 2, 2):
            for c in range(cols):
                if idx < len(names):
                    role_cell = table.rows[r].cells[c]
                    name_cell = table.rows[r + 1].cells[c]
                    role_cell.text = names[idx]["member_role"] or "MEMBRE"
                    name_cell.text = names[idx]["member_name"]
                    role_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    name_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    idx += 1

    def add_footer_line(doc, place_name, date_value):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.add_run(f"Fait à {place_name}, le : {date_value}")

    def generate_pv1_docx(market_ref):
        market = get_market_data(market_ref)
        members = get_commission(market_ref)
        competitors = get_competitors(market_ref)
        admin_excluded = [c for c in competitors if c["admin_status"] == "مرفوض" or c["technical_status"] == "مرفوض"]
        admin_admissible = [c for c in competitors if c["admin_status"] != "مرفوض"]
        tech_excluded = [c for c in competitors if c["technical_status"] == "مرفوض"]
        tech_admissible = [c for c in competitors if c["technical_status"] != "مرفوض"]
        submembers = get_subcommission(market_ref)

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(
            doc,
            "PROCES VERBAL D'APPEL D'OFFRES OUVERT",
            f"SUR OFFRE DE PRIX N° : {market['market_ref']}\n1ère Séance Publique"
        )

        doc_num = next_doc_number(market_ref, "PV1")

        doc.add_paragraph(
            f"Le {market['opening_date']} à {market['opening_time']}, une commission d’appel d’offres, "
            f"conformément à la décision de l’ordonnateur n° {market['decision_ref']} du {market['decision_date']}, "
            f"est composée comme suit :"
        )
        add_members_block(doc, members)

        doc.add_paragraph(
            f"S’est réunie en séance publique dans {market['opening_place']}, Province {market['province_name'] or 'TAROUDANT'}, "
            f"Cercle {market['cercle_name'] or 'TALIOUINE'}, Caidat {market['caidat_name'] or 'ASKAOUEN'}, "
            f"en vue de procéder à l’ouverture des plis concernant l’appel d’offres ouvert national sur offre de prix "
            f"N°: {market['market_ref']}, relatif aux {market['market_object']}."
        )

        doc.add_paragraph("Conformément à l’avis publié dans les journaux suivants :")
        doc.add_paragraph(f"· {market['publication_newspaper_1']} du {market['publication_newspaper_1_date']}")
        doc.add_paragraph(f"· {market['publication_newspaper_2']} du {market['publication_newspaper_2_date']}")
        doc.add_paragraph(f"· La mise en ligne au portail des marchés publics la date du {market['publication_portal_date']}")

        doc.add_paragraph("Le président cite les concurrents ayant envoyé leurs plis par voie électronique :")
        if competitors:
            for i, comp in enumerate(competitors, start=1):
                doc.add_paragraph(f"{i}) {comp['competitor_name']}")
        else:
            doc.add_paragraph("Néant")

        estimate_words = market["estimate_amount_words"] or format_amount_words_fr(market["estimate_amount"])

        doc.add_paragraph("Le président s’assure de la présence des membres dont la présence est obligatoire.")
        doc.add_paragraph(
            f"Le président remet le support écrit contenant l’estimation des couts détaillés des prestations "
            f"dont le montant est fixé à {fmt_number(market['estimate_amount'])} DHS TTC "
            f"({estimate_words}) Toutes Taxes Comprises."
        )
        doc.add_paragraph("Les membres de la commission paraphent le support de l’estimation des couts des prestations.")
        doc.add_paragraph("Le président cite les journaux et les références de publication au portail des marchés publics.")
        doc.add_paragraph("Le président demande aux membres de la commission de formuler leurs réserves ou observations sur les vices éventuels qui entachent la procédure.")
        doc.add_paragraph(
            "Le président ouvre les enveloppes extérieures des plis contenant les dossiers des concurrents, cite dans chacun "
            "la présence des enveloppes exigées. Il ouvre ensuite l’enveloppe portant la mention « dossiers administratif "
            "et technique », énonce les pièces contenues dans chaque dossier (dossiers administratif et technique) "
            "et dresse un état des pièces fournies par chaque concurrent."
        )
        doc.add_paragraph("Cette formalité accomplie, la séance publique est suspendue, les concurrents et le public se retirent de la salle.")
        doc.add_paragraph(
            "Ensuite, la commission se réunit à huis clos pour examiner les dossiers administratifs et techniques des concurrents, "
            "elle écarte les concurrents ci-après pour les motifs suivants."
        )

        t1 = doc.add_table(rows=1, cols=2)
        t1.style = "Table Grid"
        t1.rows[0].cells[0].text = "Concurrents"
        t1.rows[0].cells[1].text = "MOTIFIF D’ECARTEMENT"
        if admin_excluded:
            for c in admin_excluded:
                row = t1.add_row().cells
                row[0].text = c["competitor_name"]
                row[1].text = c["remarks"] or "Non conforme"
        else:
            row = t1.add_row().cells
            row[0].text = "NEANT"
            row[1].text = "NEANT"

        doc.add_paragraph("Elle arrête ensuite la liste des concurrents admissibles en précisant ceux dont les dossiers comportent des erreurs ou discordances à rectifier, à savoir :")
        doc.add_paragraph("A- Liste des concurrents admissibles sans réserves :")
        if admin_admissible:
            for i, c in enumerate(admin_admissible, start=1):
                doc.add_paragraph(f"{i}) {c['competitor_name']}")
        else:
            doc.add_paragraph("Néant")
        doc.add_paragraph("B- Liste des concurrents admissibles avec réserves : Néant")

        doc.add_paragraph("La séance publique est alors reprise et le président :")
        doc.add_paragraph("· Donne lecture de la liste des soumissionnaires admissibles cités ci-dessus.")
        doc.add_paragraph("· Rend contre décharge, aux concurrents écartés présents, leurs dossiers à l’exception des éléments d’information ayant été à l’origine de leur élimination. Il s’agit de : NEANT")
        doc.add_paragraph(
            "Le président procède ensuite à l’ouverture des enveloppes des soumissionnaires retenus portant la mention "
            "« offres Technique », énonce les pièces contenues dans chaque dossier et dresse un état des pièces fournies par chaque concurrent."
        )
        doc.add_paragraph("Cette formalité accomplie, la séance publique est suspendue, les concurrents et le public se retirent de la salle.")
        doc.add_paragraph(
            "Ensuite, la commission se réunit à huis clos pour examiner les dossiers d’offres Technique des concurrents, "
            "elle écarte les concurrents ci-après pour les motifs suivants."
        )

        t2 = doc.add_table(rows=1, cols=2)
        t2.style = "Table Grid"
        t2.rows[0].cells[0].text = "Concurrents"
        t2.rows[0].cells[1].text = "MOTIFIF D’ECARTEMENT"
        if tech_excluded:
            for c in tech_excluded:
                row = t2.add_row().cells
                row[0].text = c["competitor_name"]
                row[1].text = c["remarks"] or "Offre technique non conforme"
        else:
            row = t2.add_row().cells
            row[0].text = "NEANT"
            row[1].text = "NEANT"

        doc.add_paragraph("Elle arrête ensuite la liste des concurrents admissibles en précisant ceux dont les dossiers comportent des erreurs ou discordances à rectifier, à savoir :")
        doc.add_paragraph("A- Liste des concurrents admissibles sans réserves :")
        if tech_admissible:
            for c in tech_admissible:
                doc.add_paragraph(f"· {c['competitor_name']}")
        else:
            doc.add_paragraph("Néant")
        doc.add_paragraph("B- Liste des concurrents admissibles avec réserves : Néant")

        doc.add_paragraph(
            f"Ensuite, et conformément aux dispositions de l’article {market['rc_article_ref'] or '38'} du décret n°2-22-431 du 15 chaabane 1444 "
            f"(08 mars 2023) relatif aux marchés publics la commission a décidé de consulter une sous-commission technique pour examiner "
            f"et analyser les offres techniques fournies par les concurrents."
        )
        doc.add_paragraph("La sous-commission technique est composée de :")
        if submembers:
            for sm in submembers:
                doc.add_paragraph(f"· {sm['member_name']} : {sm['member_quality']} -------------------------------- {sm['member_role']}")
        else:
            doc.add_paragraph("· ……………………….")
            doc.add_paragraph("· ……………………….")
            doc.add_paragraph("· ……………………….")

        doc.add_paragraph("Le président de la commission suspend la séance et fixe la date de reprise des travaux de la séance.")
        add_footer_line(doc, market["commune_name"] or "ASKAOUEN", market["opening_date"])
        doc.add_paragraph(f"APPEL D’OFFRES OUVERT NATIONAL N° {market['market_ref']} (1ère Séance Publique)")
        doc.add_paragraph(f"Objet : {market['market_object']}")
        doc.add_paragraph("SIGNE : LE PRESIDENT")
        doc.add_paragraph("LES MEMBRES")
        add_signature_table(doc, members)

        return doc, doc_num

    def generate_rapport_technique_docx(market_ref):
        market = get_market_data(market_ref)
        submembers = get_subcommission(market_ref)
        competitors = get_competitors(market_ref)
        accepted = [c for c in competitors if float(c["technical_score"] or 0) >= 70]
        rejected = [c for c in competitors if float(c["technical_score"] or 0) < 70]

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(doc, "Rapport de la sous-commission technique", f"Appel d’offres ouvert {market['market_ref']}")

        doc_num = next_doc_number(market_ref, "RAPPORT_TECHNIQUE")

        doc.add_paragraph(market["market_object"])
        doc.add_paragraph("EXAMEN DES OFFRES TECHNIQUES")
        doc.add_paragraph(
            f"Le {market['opening_date']} à ({market['opening_time']}) Heures faisant suite à la séance d’ouverture des plis et à la décision "
            f"du président de la commission d’ouverture des plis de désigner une sous-commission technique, et cela conformément à l’article 38 "
            f"du décret 2-22-431 relatif aux marchés publics pour examiner et analyser les offres techniques fournies par les concurrents admis."
        )

        doc.add_paragraph("Cette sous-commission technique est composée de :")
        if submembers:
            for sm in submembers:
                doc.add_paragraph(f"· {sm['member_name']} : {sm['member_quality']} -------------------------------- {sm['member_role']}")
        else:
            doc.add_paragraph("· ……………………….")
            doc.add_paragraph("· ……………………….")
            doc.add_paragraph("· ……………………….")

        doc.add_paragraph("La liste des concurrents présentés pour l’examen des offres techniques est composée des concurrents suivants :")
        for i, c in enumerate(competitors, start=1):
            doc.add_paragraph(f"{i}) {c['competitor_name']}")

        doc.add_paragraph("Conclusion :")
        doc.add_paragraph("Après l’examen des offres techniques des concurrents :")
        doc.add_paragraph("La sous-commission technique arrête la liste des concurrents dont la note des offres techniques est supérieure à la note technique limite fixée par le règlement de consultation à 70 points à savoir :")
        if accepted:
            for c in accepted:
                doc.add_paragraph(f"· {c['competitor_name']} : {c['technical_score']} points")
        else:
            doc.add_paragraph("· Néant")

        doc.add_paragraph("La sous-commission technique arrête la liste des concurrents dont la note des offres techniques est inférieure à 70 points à savoir :")
        if rejected:
            for c in rejected:
                doc.add_paragraph(f"· {c['competitor_name']} : {c['technical_score']} points")
        else:
            doc.add_paragraph("· Néant")

        t = doc.add_table(rows=1, cols=2)
        t.style = "Table Grid"
        t.rows[0].cells[0].text = "Concurrent"
        t.rows[0].cells[1].text = "Note technique"
        for c in competitors:
            row = t.add_row().cells
            row[0].text = c["competitor_name"]
            row[1].text = str(c["technical_score"] or 0)

        doc.add_paragraph("Le présent rapport est établi pour servir d’outil à la commission d’ouverture des plis pour fonder son choix quant au rejet ou à l’acceptation de l’offre concernée.")
        doc.add_paragraph("LES MEMBRES")
        add_signature_table(doc, submembers, include_president=False)

        return doc, doc_num

    def generate_pv2_docx(market_ref):
        market = get_market_data(market_ref)
        members = get_commission(market_ref)
        competitors = get_competitors(market_ref)
        admissibles = [c for c in competitors if float(c["technical_score"] or 0) >= 70 and c["technical_status"] != "مرفوض"]

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(
            doc,
            "PROCES VERBAL D'APPEL D'OFFRES OUVERT",
            f"SUR OFFRE DE PRIX N° : {market['market_ref']}\n2eme Séance Publique"
        )

        doc_num = next_doc_number(market_ref, "PV2")

        doc.add_paragraph(
            f"Conformément à la décision de l’ordonnateur n° {market['decision_ref']} du {market['decision_date']}, "
            f"la commission d’appel d’offres ouvert national sur offre de prix N°: {market['market_ref']}, "
            f"relatif aux {market['market_object']}, composée comme suit :"
        )
        add_members_block(doc, members)

        doc.add_paragraph(
            f"S’est réunie en séance publique dans {market['opening_place']}, en vue d’étudier le rapport de la sous-commission technique "
            f"qui examine et analyse les offres techniques fournies par les concurrents admissibles suite à l’étude des dossiers administratifs."
        )
        doc.add_paragraph(
            f"Conformément aux critères d’évaluation des offres dans l’article {market['rc_article_ref'] or '...'} du règlement de consultation "
            f"les concurrents ayant obtenu une note inférieure à (70 points) seront écartés."
        )

        doc.add_paragraph("Donne lecture de la liste et les notes des offres techniques des concurrents admissibles comme suite :")
        t1 = doc.add_table(rows=1, cols=2)
        t1.style = "Table Grid"
        t1.rows[0].cells[0].text = "CONCURRENTS"
        t1.rows[0].cells[1].text = "Note Technique (Nt)"
        for c in competitors:
            row = t1.add_row().cells
            row[0].text = c["competitor_name"]
            row[1].text = str(c["technical_score"] or 0)

        doc.add_paragraph("A- Liste des concurrents admissibles sans réserves :")
        if admissibles:
            for i, c in enumerate(admissibles, start=1):
                doc.add_paragraph(f"{i}) {c['competitor_name']}")
        else:
            doc.add_paragraph("Néant")
        doc.add_paragraph("B- Liste des concurrents admissibles avec réserves : Néant")

        doc.add_paragraph("La séance publique est alors reprise et le président procède ensuite à l’ouverture des enveloppes des concurrents admissibles portant la mention < offres financières > et donne lecture de la teneur des actes d’engagement, comme suit :")

        t2 = doc.add_table(rows=1, cols=2)
        t2.style = "Table Grid"
        t2.rows[0].cells[0].text = "Concurrents"
        t2.rows[0].cells[1].text = "Montant des actes d’engagement"
        for c in admissibles:
            row = t2.add_row().cells
            row[0].text = c["competitor_name"]
            row[1].text = f"{fmt_number(c['financial_offer'])} DHS"

        doc.add_paragraph("La commission poursuit alors ses travaux à huis clos.")
        doc.add_paragraph("Elle procède ensuite à la vérification des opérations arithmétiques des offres des concurrents admissibles et rectifie les erreurs de calcul relevées dans leurs actes d’engagement.")

        t3 = doc.add_table(rows=1, cols=3)
        t3.style = "Table Grid"
        t3.rows[0].cells[0].text = "Concurrents"
        t3.rows[0].cells[1].text = "Montant avant rectification"
        t3.rows[0].cells[2].text = "Montant rectifié"

        corrected_vals = []
        for c in admissibles:
            corr = corrected_value(c)
            corrected_vals.append(corr)
            row = t3.add_row().cells
            row[0].text = c["competitor_name"]
            row[1].text = f"{fmt_number(c['financial_offer'])} DHS"
            row[2].text = f"{fmt_number(corr)} DHS"

        estimate = float(market["estimate_amount"] or 0)
        candidates = [estimate] + corrected_vals if corrected_vals else [estimate]
        ref_price = sum(candidates) / len(candidates) if candidates else 0
        winner_value = nearest_below_reference(ref_price, corrected_vals)

        ranked = sorted(admissibles, key=lambda x: corrected_value(x))
        winner = None
        for c in ranked:
            if corrected_value(c) == winner_value:
                winner = c
                break

        doc.add_paragraph("Elle procède au calcul du prix de référence comme suit :")
        doc.add_paragraph(f"· Estimation = {fmt_number(estimate)} dhs")
        for c in admissibles:
            doc.add_paragraph(f"· Offre financière {c['competitor_name']} = {fmt_number(corrected_value(c))} dhs")
        doc.add_paragraph(f"· Le prix de référence = {fmt_number(ref_price)} dhs")

        doc.add_paragraph("La commission procède au classement des offres des concurrents au regard du prix de référence ;")
        doc.add_paragraph(f"Le prix de référence = {fmt_number(ref_price)} dhs")
        for i, c in enumerate(ranked, start=1):
            doc.add_paragraph(f"{i}. Offre financière {c['competitor_name']} = {fmt_number(corrected_value(c))} dhs")

        if winner:
            doc.add_paragraph(
                f"L’offre économiquement la plus avantageuse à proposer au maître d’ouvrage, est celle qui est la plus proche par défaut "
                f"du prix de référence, qui est celle présentée par {winner['competitor_name']} = {fmt_number(winner_value)} dhs."
            )
            doc.add_paragraph(
                f"La commission invite, par voie électronique, le concurrent ayant présenté l’offre économiquement la plus avantageuse, "
                f"qui est {winner['competitor_name']} dans un délai de 7 jours, après réception de la lettre, à produire le complément "
                f"du dossier administratif visé à l’article {market['rc_article_ref'] or '...'} du Règlement de consultation."
            )

        add_footer_line(doc, market["commune_name"] or "ASKAOUEN", market["opening_date"])
        doc.add_paragraph(f"APPEL D’OFFRES OUVERT NATIONAL N° {market['market_ref']} (2eme Séance Publique)")
        doc.add_paragraph(f"Objet : {market['market_object']}")
        doc.add_paragraph("SIGNE : LE PRESIDENT")
        doc.add_paragraph("LES MEMBRES")
        add_signature_table(doc, members)

        return doc, doc_num

    def generate_pv3_docx(market_ref):
        market = get_market_data(market_ref)
        members = get_commission(market_ref)
        competitors = get_competitors(market_ref)
        ranked = sorted(
            [c for c in competitors if float(c["technical_score"] or 0) >= 70 and c["technical_status"] != "مرفوض"],
            key=lambda x: corrected_value(x)
        )
        winner = ranked[0] if ranked else None

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(
            doc,
            "PROCES VERBAL D'APPEL D'OFFRES OUVERT",
            f"SUR OFFRE DE PRIX N° : {market['market_ref']}\n3eme Séance Publique"
        )

        doc_num = next_doc_number(market_ref, "PV3")

        doc.add_paragraph(
            f"Le {market['opening_date']} à {market['opening_time']}, une commission d’appel d’offres, conformément à la décision "
            f"de l’ordonnateur n° {market['decision_ref']} du {market['decision_date']}, et composée comme suit :"
        )
        add_members_block(doc, members)

        doc.add_paragraph(
            f"S’est réunie en séance publique dans {market['opening_place']}, Province {market['province_name'] or 'TAROUDANT'}, "
            f"Cercle {market['cercle_name'] or 'TALIOUINE'}, Caidat {market['caidat_name'] or 'ASKAOUEN'}, en vue de procéder "
            f"à l’ouverture des plis concernant le complément du dossier administratif de l’attributaire de l’appel d’offres "
            f"ouvert national sur offre de prix N°: {market['market_ref']}, relatif aux {market['market_object']}."
        )

        if winner:
            doc.add_paragraph(
                f"La commission s’assure du support ayant servi de moyen d’invitation du concurrent concerné {winner['competitor_name']} : "
                f"Date d'envoi de la lettre : {market['invitation_date'] or '........'}"
            )
            doc.add_paragraph(
                f"Elle vérifie les pièces et la réponse reçue : Dossier déposé le {market['complement_file_date'] or '........'} "
                f"sur le portail marocain des marchés publics."
            )
            amount = corrected_value(winner)
            amount_words = format_amount_words_fr(amount)
            doc.add_paragraph(
                f"La commission examine les pièces complémentaires du dossier administratif et la réponse reçue et les juge acceptables, "
                f"et décide de proposer au maître d’ouvrage de retenir l’offre du concurrent ayant présenté l’offre la plus avantageuse "
                f"à savoir {winner['competitor_name']} qui s’élève à la somme de {fmt_number(amount)} Dhs ({amount_words})."
            )
        else:
            doc.add_paragraph("Aucun attributaire provisoire n’a été identifié.")

        add_footer_line(doc, market["commune_name"] or "ASKAOUEN", market["opening_date"])
        doc.add_paragraph(f"APPEL D’OFFRES OUVERT NATIONAL N° {market['market_ref']} (3eme Séance Publique)")
        doc.add_paragraph(f"Objet : {market['market_object']}")
        doc.add_paragraph("SIGNE : LE PRESIDENT")
        doc.add_paragraph("LES MEMBRES")
        add_signature_table(doc, members)

        return doc, doc_num

    def generate_os_notification_docx(market_ref):
        market = get_market_data(market_ref)

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(doc, "ORDRE DE SERVICE DE LA NOTIFICATION", f"DE L’APPROBATION DU MARCHE N°: {market['market_ref']}")

        doc_num = next_doc_number(market_ref, "OS_NOTIFICATION")

        doc.add_paragraph(
            f"Le maître d’ouvrage représenté par {market['president_name']} en qualité du président de la commune "
            f"{market['commune_name'] or 'ASKAOUEN'} informe {market['company_representative']} ayant pour qualité "
            f"{market['company_quality']} agissant au nom et pour le compte de la société {market['company_awarded']}, "
            f"faisant élection de domicile à {market['company_address']} que le marché qu’il a signé avec la commune "
            f"{market['commune_name'] or 'ASKAOUEN'} ayant pour objet : {market['market_object']} est approuvé à la date du {market['approval_date']}."
        )

        doc.add_paragraph(
            f"Par conséquent, l'intéressé est invité à acquitter les droits de timbre dus au titre du présent marché conformément à la législation "
            f"en vigueur, la caution définitive est prévue pour ce marché conformément à l’article {market['cps_article_ref'] or '12'} du CPS."
        )

        doc.add_paragraph(
            f"Le présent ordre de service, certifié conforme à la minute inscrit au registre sous le N°: {market['os_register_number']} "
            f"sera notifié à {market['company_representative']} demeurant à {market['company_address']}."
        )

        doc.add_paragraph(f"A {market['commune_name'] or 'ASKAOUEN'}, Le {market['notification_date']}")
        doc.add_paragraph("Le président :")

        doc.add_paragraph("--------------------------------------------------------------------------------------------------------------------------------")
        doc.add_paragraph(
            f"Le : ..............., Je soussigné : {market['company_representative']} ayant pour qualité {market['company_quality']} "
            f"agissant au nom et pour le compte de la société {market['company_awarded']}, faisant élection de domicile à {market['company_address']} "
            f"avoir reçu une copie de l’ordre de service de l’approbation du marché {market['market_ref']} en date du : {market['approval_date']} "
            f"inscrit au registre sous le N°: {market['os_register_number']}."
        )

        return doc, doc_num

    def generate_os_commencement_docx(market_ref):
        market = get_market_data(market_ref)

        doc = Document()
        style_doc(doc)
        add_top_header(doc, market)
        add_doc_title(doc, "ORDRE DE SERVICE A L’ENTREPRENEUR POUR COMMENCEMENT DES TRAVAUX", f"{market['market_ref']}")

        doc_num = next_doc_number(market_ref, "OS_COMMENCEMENT")

        doc.add_paragraph(
            f"Le maître d’ouvrage représenté par {market['president_name']} en qualité du président de la commune "
            f"{market['commune_name'] or 'ASKAOUEN'} informe {market['company_representative']} ayant pour qualité {market['company_quality']} "
            f"agissant au nom et pour le compte de la société {market['company_awarded']}, faisant élection de domicile à {market['company_address']} "
            f"que le marché qu’il a signé avec la commune {market['commune_name'] or 'ASKAOUEN'} ayant pour objet : {market['market_object']} est approuvé."
        )

        doc.add_paragraph(
            f"Par conséquent, l'intéressé est invité à commencer les travaux objet du présent marché à compter du : {market['commencement_date']}"
        )

        doc.add_paragraph(
            f"Le présent ordre de service, certifié conforme à la minute inscrit au registre sous le N°: {market['os_register_number']} "
            f"sera notifié à {market['company_representative']} demeurant à {market['company_address']}."
        )

        doc.add_paragraph(f"A {market['commune_name'] or 'ASKAOUEN'}, Le {market['notification_date']}")
        doc.add_paragraph("Le président :")

        doc.add_paragraph("--------------------------------------------------------------------------------------------------------------------------------")
        doc.add_paragraph(
            f"Le : ..............., Je soussigné : {market['company_representative']} ayant pour qualité {market['company_quality']} "
            f"agissant au nom et pour le compte de la société {market['company_awarded']}, faisant élection de domicile à {market['company_address']} "
            f"avoir reçu une copie de l'ordre de service de commencement des prestations relatif au marché n° {market['market_ref']} "
            f"et cela à compter du {market['commencement_date']}, inscrit au registre sous le N° : {market['os_register_number']}."
        )

        return doc, doc_num

    tabs = st.tabs([
        "Fiche marché",
        "Commission",
        "Sous-commission",
        "Concurrents",
        "Génération الوثائق",
        "Registre"
    ])

    with tabs[0]:
        st.subheader("Fiche marché SMART PRO+")
        with st.form("market_master_form"):
            c1, c2 = st.columns(2)

            with c1:
                market_ref = st.text_input("Référence du marché")
                market_object = st.text_area("Objet du marché")
                market_owner = st.text_input("Maître d’ouvrage", value="COMMUNE ASKAOUEN")
                president_name = st.text_input("Président", value="ZILALI MOHAMED")
                commune_name = st.text_input("Commune", value="ASKAOUEN")
                province_name = st.text_input("Province", value="TAROUDANT")
                cercle_name = st.text_input("Cercle", value="TALIOUINE")
                caidat_name = st.text_input("Caidat", value="ASKAOUEN")
                decision_ref = st.text_input("Référence décision ordonnateur")
                decision_date = st.text_input("Date décision")
                publication_portal_date = st.text_input("Date publication portail")

            with c2:
                publication_newspaper_1 = st.text_input("Journal 1")
                publication_newspaper_1_date = st.text_input("Date Journal 1")
                publication_newspaper_2 = st.text_input("Journal 2")
                publication_newspaper_2_date = st.text_input("Date Journal 2")
                opening_date = st.text_input("Date ouverture")
                opening_time = st.text_input("Heure ouverture", value="10h")
                opening_place = st.text_input("Lieu ouverture", value="Salle de réunion de la Commune ASKAOUEN")
                estimate_amount = st.number_input("Montant estimation TTC", min_value=0.0, step=1000.0)
                estimate_amount_words = st.text_input("Montant en lettres")
                rc_article_ref = st.text_input("Article RC / juridique", value="38")
                cps_article_ref = st.text_input("Article CPS", value="12")

            c3, c4 = st.columns(2)
            with c3:
                company_awarded = st.text_input("Société attributaire")
                company_representative = st.text_input("Représentant société")
                company_quality = st.text_input("Qualité du représentant", value="Gérant")
                company_address = st.text_area("Adresse société")
            with c4:
                approval_date = st.text_input("Date approbation")
                os_register_number = st.text_input("N° registre OS")
                notification_date = st.text_input("Date notification")
                commencement_date = st.text_input("Date commencement")
                invitation_date = st.text_input("Date envoi invitation complément dossier")
                complement_file_date = st.text_input("Date dépôt complément dossier")

            if st.form_submit_button("حفظ fiche marché"):
                insert_record(
                    """
                    INSERT INTO market_master_data (
                        market_ref, market_object, market_owner, president_name, commune_name, province_name,
                        cercle_name, caidat_name, decision_ref, decision_date, publication_portal_date,
                        publication_newspaper_1, publication_newspaper_2, publication_newspaper_1_date,
                        publication_newspaper_2_date, opening_date, opening_time, opening_place, estimate_amount,
                        estimate_amount_words, rc_article_ref, cps_article_ref, company_awarded,
                        company_representative, company_quality, company_address, approval_date,
                        os_register_number, notification_date, commencement_date, complement_file_date,
                        invitation_date, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        market_ref, market_object, market_owner, president_name, commune_name, province_name,
                        cercle_name, caidat_name, decision_ref, decision_date, publication_portal_date,
                        publication_newspaper_1, publication_newspaper_2, publication_newspaper_1_date,
                        publication_newspaper_2_date, opening_date, opening_time, opening_place, estimate_amount,
                        estimate_amount_words, rc_article_ref, cps_article_ref, company_awarded,
                        company_representative, company_quality, company_address, approval_date,
                        os_register_number, notification_date, commencement_date, complement_file_date,
                        invitation_date, str(date.today())
                    )
                )
                st.success("تم حفظ fiche marché.")

    with tabs[1]:
        refs = get_market_refs()
        if not refs:
            st.warning("أدخل fiche marché أولًا.")
        else:
            selected_ref = st.selectbox("Référence marché", refs, key="commission_ref")
            with st.form("commission_form"):
                c1, c2, c3, c4 = st.columns(4)
                member_name = c1.text_input("Nom membre")
                member_role = c2.text_input("Rôle", placeholder="PRESIDENT / MEMBRE")
                member_quality = c3.text_input("Qualité", placeholder="Président / Représentant percepteur / Directeur ...")
                member_order_num = c4.number_input("Ordre", min_value=1, step=1)
                if st.form_submit_button("Ajouter membre commission"):
                    insert_record(
                        "INSERT INTO market_commission_members (market_ref, member_name, member_role, member_quality, member_order_num, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (selected_ref, member_name, member_role, member_quality, member_order_num, str(date.today()))
                    )
                    st.success("تمت إضافة عضو اللجنة.")
            st.dataframe(get_commission(selected_ref), use_container_width=True, hide_index=True)

    with tabs[2]:
        refs = get_market_refs()
        if not refs:
            st.warning("أدخل fiche marché أولًا.")
        else:
            selected_ref = st.selectbox("Référence marché", refs, key="subcommission_ref")
            with st.form("subcommission_form"):
                c1, c2, c3, c4 = st.columns(4)
                member_name = c1.text_input("Nom membre technique")
                member_role = c2.text_input("Rôle", value="MEMBRE")
                member_quality = c3.text_input("Qualité", placeholder="Technicien à la commune ...")
                member_order_num = c4.number_input("Ordre technique", min_value=1, step=1)
                if st.form_submit_button("Ajouter membre sous-commission"):
                    insert_record(
                        "INSERT INTO market_subcommission_members (market_ref, member_name, member_role, member_quality, member_order_num, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (selected_ref, member_name, member_role, member_quality, member_order_num, str(date.today()))
                    )
                    st.success("تمت إضافة عضو sous-commission.")
            st.dataframe(get_subcommission(selected_ref), use_container_width=True, hide_index=True)

    with tabs[3]:
        refs = get_market_refs()
        if not refs:
            st.warning("أدخل fiche marché أولًا.")
        else:
            selected_ref = st.selectbox("Référence marché", refs, key="competitors_ref")
            with st.form("competitor_form"):
                c1, c2 = st.columns(2)
                with c1:
                    competitor_name = st.text_input("Nom concurrent")
                    submitted_electronically = st.selectbox("Dépôt électronique", ["Oui", "Non"])
                    admin_status = st.selectbox("Statut administratif", ["مقبول", "مرفوض"])
                    technical_status = st.selectbox("Statut technique", ["مقبول", "مرفوض"])
                with c2:
                    technical_score = st.number_input("Note technique", min_value=0.0, max_value=100.0, step=1.0)
                    financial_offer = st.number_input("Offre financière", min_value=0.0, step=1000.0)
                    corrected_offer = st.number_input("Offre rectifiée", min_value=0.0, step=1000.0)
                    remarks = st.text_area("Remarques")

                if st.form_submit_button("Ajouter concurrent"):
                    insert_record(
                        """
                        INSERT INTO market_competitors (
                            market_ref, competitor_name, submitted_electronically, admin_status,
                            technical_status, technical_score, financial_offer, corrected_offer, remarks, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            selected_ref, competitor_name, submitted_electronically, admin_status,
                            technical_status, technical_score, financial_offer, corrected_offer, remarks, str(date.today())
                        )
                    )
                    st.success("تمت إضافة المتنافس.")
            st.dataframe(get_competitors(selected_ref), use_container_width=True, hide_index=True)

    with tabs[4]:
        refs = get_market_refs()
        if not refs:
            st.warning("أدخل fiche marché أولًا.")
        else:
            selected_ref = st.selectbox("Référence marché", refs, key="docs_ref")
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("📄 توليد PV1"):
                    doc, num = generate_pv1_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل PV1 رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"PV1_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                if st.button("📄 توليد Rapport technique"):
                    doc, num = generate_rapport_technique_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل Rapport رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"Rapport_Technique_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            with c2:
                if st.button("📄 توليد PV2"):
                    doc, num = generate_pv2_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل PV2 رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"PV2_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                if st.button("📄 توليد OS Notification"):
                    doc, num = generate_os_notification_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل OS Notification رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"OS_Notification_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            with c3:
                if st.button("📄 توليد PV3"):
                    doc, num = generate_pv3_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل PV3 رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"PV3_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                if st.button("📄 توليد OS Commencement"):
                    doc, num = generate_os_commencement_docx(selected_ref)
                    bio = BytesIO()
                    doc.save(bio)
                    st.download_button(
                        f"تحميل OS Commencement رقم {num}",
                        data=bio.getvalue(),
                        file_name=f"OS_Commencement_{selected_ref}_{num}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    with tabs[5]:
        st.subheader("Registre marchés")
        st.dataframe(fetch_all("SELECT * FROM market_master_data ORDER BY id DESC"), use_container_width=True, hide_index=True)
        st.subheader("Commission")
        st.dataframe(fetch_all("SELECT * FROM market_commission_members ORDER BY id DESC"), use_container_width=True, hide_index=True)
        st.subheader("Sous-commission")
        st.dataframe(fetch_all("SELECT * FROM market_subcommission_members ORDER BY id DESC"), use_container_width=True, hide_index=True)
        st.subheader("Concurrents")
        st.dataframe(fetch_all("SELECT * FROM market_competitors ORDER BY id DESC"), use_container_width=True, hide_index=True)
        st.subheader("Compteur الوثائق")
        st.dataframe(fetch_all("SELECT * FROM market_doc_counter ORDER BY id DESC"), use_container_width=True, hide_index=True)
