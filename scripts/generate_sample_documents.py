"""
Generate sample policy PDFs for ingestion testing.

Run: python scripts/generate_sample_documents.py
"""

import os
from pathlib import Path

from fpdf import FPDF

DOCS_DIR = Path(__file__).resolve().parents[1] / "documents"


def _hindi_font_path() -> Path | None:
    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    for name in ("Nirmala.ttf", "NirmalaB.ttf", "Mangal.ttf", "ArialUni.ttf"):
        candidate = fonts_dir / name
        if candidate.exists():
            return candidate
    return None


class PolicyPDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self._hindi_font = "Helvetica"
        hindi_path = _hindi_font_path()
        if hindi_path:
            self.add_font("PotensHindi", "", str(hindi_path))
            self._hindi_font = "PotensHindi"

    def add_section(self, heading: str, paragraphs: list[str]) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, heading, ln=True)
        self.ln(2)
        self.set_font("Helvetica", size=11)
        for para in paragraphs:
            self.multi_cell(0, 6, para)
            self.ln(2)

    def add_hindi_block(self, paragraphs: list[str]) -> None:
        self.set_font(self._hindi_font, size=11)
        for para in paragraphs:
            self.multi_cell(0, 6, para)
            self.ln(2)


def write_pdf(filename: str, title: str, sections: list[tuple[str, list[str]]]) -> None:
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)

    for heading, paragraphs in sections:
        pdf.add_section(heading, paragraphs)

    path = DOCS_DIR / filename
    pdf.output(str(path))
    print(f"Created {path}")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    write_pdf(
        "data_privacy_policy.pdf",
        "Potens IT Services - Data Privacy Policy",
        [
            (
                "1. Purpose and scope",
                [
                    "Effective date: 1 January 2025. This policy applies to all employees, "
                    "contractors, interns, and systems that process personal data on behalf of "
                    "Potens IT Services and Consultancy Pvt. Ltd.",
                    "Personal data includes identifiers, contact details, employment records, "
                    "client project metadata, and technical logs that can be linked to an individual.",
                ],
            ),
            (
                "2. Retention and minimization",
                [
                    "Data must be collected only for defined business purposes and retained no "
                    "longer than necessary. Client contract records are retained for a maximum of "
                    "seven (7) years unless a longer period is required by law or an active dispute.",
                    "Employee HR records are retained for seven (7) years after separation unless "
                    "regulations require otherwise.",
                ],
            ),
            (
                "3. Security and training",
                [
                    "All employees must complete annual data protection training by 31 March each year.",
                    "Security incidents must be reported to the Data Protection Officer within "
                    "twenty-four (24) hours of discovery. Critical incidents require immediate "
                    "containment steps documented in the security runbook.",
                ],
            ),
            (
                "4. Data subject rights",
                [
                    "Data subjects may request access, correction, or deletion of personal data within "
                    "thirty (30) days of a verified written request, except where legal obligations "
                    "require retention.",
                    "Deletion requests for client data require approval from Legal and the "
                    "account owner.",
                ],
            ),
        ],
    )

    write_pdf(
        "leave_policy.pdf",
        "Potens IT Services - Employee Leave Policy",
        [
            (
                "1. Annual leave",
                [
                    "Full-time employees receive twenty (20) days of paid annual leave per "
                    "calendar year, pro-rated for mid-year joiners.",
                    "Annual leave must be requested at least fourteen (14) days in advance through "
                    "the HR portal unless an exception is approved by the line manager.",
                    "Unused annual leave may be carried forward up to five (5) days into the next "
                    "year; any remaining balance is forfeited on 31 March.",
                ],
            ),
            (
                "2. Sick and special leave",
                [
                    "Sick leave entitlement is twelve (12) days per year. A medical certificate is "
                    "required for absences exceeding three (3) consecutive working days.",
                    "Maternity leave is twenty-six (26) weeks as per applicable labor regulations. "
                    "Paternity leave is ten (10) working days with two weeks' notice.",
                ],
            ),
            (
                "3. Public holidays and approvals",
                [
                    "Public holidays follow the published India office calendar. Leave overlapping "
                    "with mandatory client on-site days requires director approval.",
                    "HR publishes monthly leave utilization reports for managers.",
                ],
            ),
        ],
    )

    write_pdf(
        "remote_work_policy.pdf",
        "Potens IT Services - Remote Work Policy",
        [
            (
                "1. Eligibility",
                [
                    "Eligible employees may work remotely up to three (3) days per week with "
                    "written manager approval documented in the HR system.",
                    "Roles with client-site obligations may be limited to one (1) remote day per week.",
                ],
            ),
            (
                "2. Security and availability",
                [
                    "Remote work requires a dedicated secure workspace, company-approved VPN, and "
                    "full-disk encryption on company-managed devices.",
                    "Core collaboration hours are 10:00 AM to 4:00 PM IST on working days. Employees "
                    "must remain reachable on approved channels during these hours.",
                ],
            ),
            (
                "3. Meetings and equipment",
                [
                    "Employees working remotely must attend monthly in-person team meetings at the "
                    "assigned office unless exempted by the program lead.",
                    "Equipment provided by Potens remains company property and must be returned within "
                    "five (5) business days of employment end.",
                ],
            ),
        ],
    )

    write_pdf(
        "code_of_conduct.pdf",
        "Potens IT Services - Code of Conduct",
        [
            (
                "1. Standards of behavior",
                [
                    "All personnel must act with integrity, respect, and compliance with applicable laws.",
                    "Harassment, discrimination, and retaliation are strictly prohibited and may result "
                    "in termination and legal action.",
                ],
            ),
            (
                "2. Conflicts and gifts",
                [
                    "Conflicts of interest must be disclosed to HR within seven (7) days of awareness.",
                    "Accepting gifts valued above INR 2,000 from vendors or partners requires prior "
                    "written approval from Compliance.",
                ],
            ),
            (
                "3. Reporting",
                [
                    "Whistleblower reports may be submitted anonymously via the ethics hotline. "
                    "Retaliation against reporters is a serious policy violation.",
                    "Investigations are handled confidentially; outcomes are communicated to relevant "
                    "stakeholders on a need-to-know basis.",
                ],
            ),
        ],
    )

    write_pdf(
        "hr_handbook_excerpt.pdf",
        "Potens IT Services - HR Handbook (Benefits Excerpt)",
        [
            (
                "1. Health benefits",
                [
                    "Health insurance coverage begins on the first day of the month following sixty (60) "
                    "days of continuous employment.",
                    "Dependents may be enrolled within thirty (30) days of eligibility; late enrollment "
                    "requires underwriting review.",
                ],
            ),
            (
                "2. Leave and performance (handbook summary)",
                [
                    "The handbook summarizes eighteen (18) days of annual leave for full-time staff, "
                    "pro-rated for mid-year joiners. Detailed accrual rules appear in the Leave Policy.",
                    "Performance reviews occur twice yearly in June and December. Ratings inform "
                    "development plans and bonus eligibility.",
                ],
            ),
            (
                "3. Development and separation",
                [
                    "Professional development budget of INR 25,000 per employee per fiscal year requires "
                    "manager sign-off and must align with role competencies.",
                    "Resignation notice period is thirty (30) days for individual contributors and "
                    "sixty (60) days for people managers.",
                ],
            ),
        ],
    )

    # English + Hindi notice (no Gujarati/Marathi)
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Potens IT Services - Bilingual Employee Notice", ln=True)
    pdf.ln(4)
    pdf.add_section(
        "English",
        [
            "All employees must update emergency contact details in the HR portal by "
            "31 December each year.",
            "Failure to comply may result in payroll processing hold until records are verified.",
            "Questions should be directed to HR at hr@potens.in.",
        ],
    )
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Hindi", ln=True)
    pdf.ln(2)
    pdf.add_hindi_block(
        [
            "सभी कर्मचारियों को प्रत्येक वर्ष 31 दिसंबर तक आपातकालीन संपर्क विवरण HR पोर्टल में अपडेट करना अनिवार्य है।",
            "अनुपालन न करने पर पेरोल प्रसंस्करण तब तक रोकी जा सकती है जब तक रिकॉर्ड सत्यापित नहीं हो जाते।",
            "प्रश्नों के लिए hr@potens.in पर HR से संपर्क करें।",
        ],
    )
    path = DOCS_DIR / "multilingual_notice.pdf"
    pdf.output(str(path))
    print(f"Created {path}")

    print("\nDone. Re-ingest documents (restart main.py or POST /ingest) to refresh the vector store.")


if __name__ == "__main__":
    main()
