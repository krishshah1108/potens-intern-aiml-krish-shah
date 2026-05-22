"""
Generate 5 substantive sample PDFs for ingestion testing.

Run: python scripts/generate_sample_documents.py
"""

from pathlib import Path

from fpdf import FPDF

DOCS_DIR = Path(__file__).resolve().parents[1] / "documents"


def write_pdf(filename: str, title: str, paragraphs: list[str]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", size=11)

    for para in paragraphs:
        pdf.multi_cell(0, 6, para)
        pdf.ln(2)

    path = DOCS_DIR / filename
    pdf.output(str(path))
    print(f"Created {path}")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    write_pdf(
        "data_privacy_policy.pdf",
        "Potens Data Privacy Policy",
        [
            "Effective Date: January 2025. This policy governs personal data collected "
            "from employees, clients, and website visitors of Potens IT Services.",
            "Personal data must be retained only for as long as necessary to fulfill "
            "the stated purpose, with a maximum retention period of seven (7) years for "
            "client contract records unless law requires longer storage.",
            "All employees must complete annual data protection training by March 31 each year.",
            "Data subjects may request deletion of personal data within thirty (30) days "
            "of a verified written request, except where legal obligations require retention.",
            "Security incidents must be reported to the Data Protection Officer within "
            "twenty-four (24) hours of discovery.",
        ],
    )

    write_pdf(
        "leave_policy.pdf",
        "Potens Employee Leave Policy",
        [
            "Full-time employees receive twenty (20) days of paid annual leave per calendar year.",
            "Annual leave must be requested at least fourteen (14) days in advance through the HR portal.",
            "Unused annual leave may be carried forward up to five (5) days into the next year; "
            "remaining balance is forfeited on March 31.",
            "Sick leave entitlement is twelve (12) days per year with medical certificate required "
            "for absences exceeding three (3) consecutive days.",
            "Maternity leave is twenty-six (26) weeks as per applicable labor regulations.",
        ],
    )

    write_pdf(
        "remote_work_policy.pdf",
        "Potens Remote Work Policy",
        [
            "Eligible employees may work remotely up to three (3) days per week with manager approval.",
            "Remote work requires a dedicated secure workspace and company-approved VPN connection.",
            "Core collaboration hours are 10:00 AM to 4:00 PM IST on working days.",
            "Employees working remotely must attend monthly in-person team meetings at the assigned office.",
            "Equipment provided by Potens remains company property and must be returned upon exit.",
        ],
    )

    write_pdf(
        "code_of_conduct.pdf",
        "Potens Code of Conduct",
        [
            "All personnel must act with integrity, respect, and compliance with applicable laws.",
            "Conflicts of interest must be disclosed to HR within seven (7) days of awareness.",
            "Accepting gifts valued above INR 2,000 from vendors requires prior written approval.",
            "Harassment, discrimination, and retaliation are strictly prohibited and subject to "
            "disciplinary action up to termination.",
            "Whistleblower reports may be submitted anonymously via the ethics hotline.",
        ],
    )

    write_pdf(
        "hr_handbook_excerpt.pdf",
        "Potens HR Handbook - Benefits Excerpt",
        [
            "Health insurance coverage begins on the first day of the month following sixty (60) "
            "days of employment.",
            "Annual leave for full-time staff is eighteen (18) days per year, pro-rated for mid-year joiners.",
            "Performance reviews occur twice yearly in June and December.",
            "Professional development budget of INR 25,000 per employee per fiscal year requires "
            "manager sign-off.",
            "Resignation notice period is thirty (30) days for individual contributors and "
            "sixty (60) days for managers.",
        ],
    )

    # Multilingual excerpt document
    write_pdf(
        "multilingual_notice.pdf",
        "Potens Multilingual Employee Notice",
        [
            "English: All employees must update emergency contact details by 31 December annually.",
            "Hindi (Devanagari stored in README; PDF uses English index line): "
            "All employees must update emergency contacts by 31 December - Hindi notice.",
            "Gujarati notice: All employees must update emergency contacts by 31 December annually.",
            "Marathi notice: All employees must update emergency contacts by 31 December annually.",
            "Violation of this requirement may result in payroll hold until compliance is confirmed.",
        ],
    )

    print("\nDone. Run ingestion via API or restart main.py to index.")


if __name__ == "__main__":
    main()
