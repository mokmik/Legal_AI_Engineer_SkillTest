"""Built-in test cases, one per EU instrument type (Regulation / Directive / national law).
What confidence I expected each to return, and what the harness actually shows, is discussed in the README (Evaluation).
"""

TEST_CASES = [
    {
        "title": "Test case 1 - SEPA transfer clause (EU Regulation), France to Germany",
        "clause": (
            "Les virements en euros sont exécutés conformément à la réglementation SEPA "
            "applicable aux virements et prélèvements en euros."
        ),
        "change": "Qonto is aligning this clause with the new SEPA instant credit transfer rules.",
        "source_country": "France",
        "target_country": "Germany",
    },
    {
        "title": "Test case 2 - Distance-contract withdrawal right (EU Directive), France to Spain",
        "clause": (
            "Le client dispose d'un délai de rétractation de 14 jours à compter de la "
            "conclusion du contrat à distance, conformément aux dispositions applicables."
        ),
        "change": "Qonto is standardising its distance-contract withdrawal terms across EU markets.",
        "source_country": "France",
        "target_country": "Spain",
    },
    {
        "title": "Test case 3 - Liability limitation (national law), France to Netherlands",
        "clause": (
            "La responsabilité de Qonto est limitée au montant des frais payés par le "
            "client au cours des 12 derniers mois. Cette limitation s'applique à tous "
            "les dommages directs et indirects."
        ),
        "change": "Qonto is expanding its liability framework to cover new payment services.",
        "source_country": "France",
        "target_country": "Netherlands",
    },
    {
        "title": "Test case 4 - Restatement of GDPR data-subject rights (Regulation, rights-granting), France to Germany",
        "clause": (
            "Le client peut exercer à tout moment ses droits d'accès, de rectification "
            "et d'effacement concernant ses données personnelles, conformément au "
            "Règlement général sur la protection des données (RGPD)."
        ),
        "change": "Qonto is harmonising how customers' GDPR rights are presented across EU markets.",
        "source_country": "France",
        "target_country": "Germany",
    },
]
