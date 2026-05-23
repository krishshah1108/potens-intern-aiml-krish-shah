"""
Generate English policy PDFs (10-15 pages each) for RAG and contradiction testing.

Run: python scripts/generate_sample_documents.py
"""

from pathlib import Path

from fpdf import FPDF

DOCS_DIR = Path(__file__).resolve().parents[1] / "documents"
TARGET_PAGES = 12


class PolicyPDF(FPDF):
    def add_section(self, heading: str, paragraphs: list[str]) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font("Helvetica", size=11)
        for para in paragraphs:
            self.multi_cell(0, 6, para)
            self.ln(2)


def _filler_paragraphs(topic: str, section_num: int) -> list[str]:
    """Unique policy prose to pad page count without duplicate embeddings."""
    return [
        f"Section {section_num} of the {topic} defines responsibilities for all Potens "
        f"IT Services business units. Managers must communicate requirements during onboarding "
        f"and annual refresh training.",
        f"Non-compliance with section {section_num} may result in corrective action, "
        f"including restricted system access, mandatory coaching, or escalation to HR and Legal.",
        f"Records supporting section {section_num} must be stored in approved systems with "
        f"access limited to role-based groups. Informal channels such as personal email are not "
        f"permitted for official policy decisions.",
    ]


def write_long_pdf(
    filename: str,
    title: str,
    core_sections: list[tuple[str, list[str]]],
    target_pages: int = TARGET_PAGES,
) -> None:
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0,
        5,
        "Potens IT Services and Consultancy Pvt. Ltd. | Internal Use | Version 2025.1",
    )
    pdf.ln(4)

    section_idx = 0
    for heading, paragraphs in core_sections:
        pdf.add_section(heading, paragraphs)
        section_idx += 1

    appendix_num = 1
    while pdf.page_no() < target_pages:
        topic_short = title.split("-")[-1].strip()[:40]
        pdf.add_section(
            f"Appendix {appendix_num}: Operational guidance",
            _filler_paragraphs(topic_short, section_idx + appendix_num),
        )
        appendix_num += 1
        section_idx += 1

    path = DOCS_DIR / filename
    pdf.output(str(path))
    print(f"Created {path} ({pdf.page_no()} pages)")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Remove legacy / uploaded files not part of generated corpus
    for stale in (
        "multilingual_notice.pdf",
        "Potens_Intern_Take_Home_2026.pdf",
    ):
        p = DOCS_DIR / stale
        if p.exists():
            p.unlink()
            print(f"Removed {p.name}")

    write_long_pdf(
        "data_privacy_policy.pdf",
        "Potens IT Services - Data Privacy Policy",
        [
            (
                "1. Purpose and scope",
                [
                    "Effective date: 1 January 2025. Applies to employees, contractors, interns, "
                    "and systems processing personal data for Potens IT Services.",
                    "Personal data includes identifiers, employment records, client metadata, "
                    "and technical logs linkable to an individual.",
                ],
            ),
            (
                "2. Retention - client records",
                [
                    "Client contract records must be retained for a maximum of seven (7) years "
                    "from contract end unless law requires longer storage.",
                    "Marketing consents expire after twenty-four (24) months without interaction.",
                ],
            ),
            (
                "3. Security incidents",
                [
                    "Security incidents must be reported to the Data Protection Officer within "
                    "twenty-four (24) hours of discovery.",
                    "Annual data protection training is mandatory by 31 March each year.",
                ],
            ),
            (
                "4. Data subject rights",
                [
                    "Access, correction, or deletion requests must be fulfilled within thirty (30) "
                    "days of verified written request where legally permissible.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "leave_policy.pdf",
        "Potens IT Services - Employee Leave Policy",
        [
            (
                "1. Annual leave entitlement",
                [
                    "Full-time employees receive twenty (20) days of paid annual leave per "
                    "calendar year, pro-rated for mid-year joiners.",
                    "Requests require fourteen (14) days advance notice via the HR portal.",
                    "Up to five (5) unused days may carry forward; balance forfeits on 31 March.",
                ],
            ),
            (
                "2. Sick and parental leave",
                [
                    "Sick leave: twelve (12) days per year; medical certificate after three (3) "
                    "consecutive days.",
                    "Maternity leave: twenty-six (26) weeks per applicable labor law.",
                ],
            ),
            (
                "3. Public holidays",
                [
                    "Public holidays follow the published India office calendar.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "hr_handbook_excerpt.pdf",
        "Potens IT Services - HR Handbook (Benefits Excerpt)",
        [
            (
                "1. Health insurance",
                [
                    "Coverage begins the first day of the month after sixty (60) days of employment.",
                ],
            ),
            (
                "2. Annual leave summary",
                [
                    "The handbook summarizes eighteen (18) days of annual leave for full-time staff, "
                    "pro-rated for mid-year joiners. See the official Leave Policy for accrual detail.",
                ],
            ),
            (
                "3. Professional development",
                [
                    "Development budget: INR 25,000 per employee per fiscal year with manager approval.",
                ],
            ),
            (
                "4. Notice period",
                [
                    "Resignation notice: thirty (30) days for individual contributors; sixty (60) "
                    "days for people managers.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "remote_work_policy.pdf",
        "Potens IT Services - Remote Work Policy",
        [
            (
                "1. Eligibility and limits",
                [
                    "Eligible employees may work remotely up to three (3) days per week with "
                    "manager approval recorded in HR.",
                ],
            ),
            (
                "2. Security",
                [
                    "Requires VPN, company-managed device, and full-disk encryption.",
                    "Core collaboration hours: 10:00 AM to 4:00 PM IST on working days.",
                ],
            ),
            (
                "3. On-site requirements",
                [
                    "Monthly in-person team meetings at the assigned office are mandatory unless exempted.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "workplace_attendance_policy.pdf",
        "Potens IT Services - Workplace Attendance Policy",
        [
            (
                "1. Office presence",
                [
                    "Employees are expected on-site at least three (3) days per week at their "
                    "assigned location unless a formal remote schedule is approved.",
                ],
            ),
            (
                "2. Approved remote days",
                [
                    "Standard remote work allowance is two (2) days per week maximum for eligible roles.",
                    "Additional remote days require director approval and client notification.",
                ],
            ),
            (
                "3. Attendance tracking",
                [
                    "Badge and HRIS records are the system of record for attendance compliance.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "code_of_conduct.pdf",
        "Potens IT Services - Code of Conduct",
        [
            (
                "1. Integrity",
                [
                    "All personnel must act with integrity and comply with applicable laws.",
                    "Harassment, discrimination, and retaliation are prohibited.",
                ],
            ),
            (
                "2. Gifts and conflicts",
                [
                    "Gifts above INR 2,000 from vendors require prior written Compliance approval.",
                    "Conflicts of interest must be disclosed to HR within seven (7) days.",
                ],
            ),
            (
                "3. Reporting",
                [
                    "Anonymous reports may be submitted via the ethics hotline.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "information_security_policy.pdf",
        "Potens IT Services - Information Security Policy",
        [
            (
                "1. Password standards",
                [
                    "Passwords must be rotated every ninety (90) days on all production systems.",
                    "Minimum length twelve (12) characters with MFA on external access.",
                ],
            ),
            (
                "2. Data classification",
                [
                    "Confidential data must not be stored on personal devices or public cloud drives.",
                ],
            ),
            (
                "3. Incident response",
                [
                    "Suspected breaches must be reported to the Security Operations Center within one (1) hour.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "it_access_policy.pdf",
        "Potens IT Services - IT Access Policy",
        [
            (
                "1. Credential management",
                [
                    "User passwords on corporate systems must be changed every sixty (60) days.",
                    "Shared accounts are prohibited except documented break-glass accounts.",
                ],
            ),
            (
                "2. Access reviews",
                [
                    "Managers must certify direct-report access quarterly in the IAM portal.",
                ],
            ),
            (
                "3. Offboarding",
                [
                    "All access revoked within twenty-four (24) hours of termination notification.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "expense_reimbursement_policy.pdf",
        "Potens IT Services - Expense Reimbursement Policy",
        [
            (
                "1. Submission deadlines",
                [
                    "Expense reports must be submitted within thirty (30) days of incurring cost.",
                ],
            ),
            (
                "2. Travel meals",
                [
                    "Domestic travel meal limit: INR 1,500 per day without pre-approval.",
                    "International travel requires finance pre-approval above INR 25,000 per trip.",
                ],
            ),
            (
                "3. Client entertainment",
                [
                    "Client entertainment above INR 5,000 per event requires director approval.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "records_management_policy.pdf",
        "Potens IT Services - Records Management Policy",
        [
            (
                "1. Client contractual records",
                [
                    "Executed client contracts and statements of work must be archived for five (5) "
                    "years after project closure unless Legal specifies otherwise.",
                ],
            ),
            (
                "2. Email retention",
                [
                    "Corporate email retained ninety (90) days in live mailboxes; archives seven (7) years.",
                ],
            ),
            (
                "3. Destruction",
                [
                    "Destruction requires certificate of destruction from approved vendors.",
                ],
            ),
        ],
    )

    write_long_pdf(
        "employee_compliance_notice.pdf",
        "Potens IT Services - Employee Compliance Notice",
        [
            (
                "1. Emergency contact update deadline",
                [
                    "EMERGENCY CONTACT REQUIREMENT: Every employee must update emergency contact "
                    "information in the HR self-service portal no later than 31 December of each "
                    "calendar year.",
                    "Emergency contact details include phone numbers, names, and relationship "
                    "for primary and secondary contacts.",
                    "Payroll processing may be held until emergency contact records are verified.",
                ],
            ),
            (
                "2. Policy acknowledgements",
                [
                    "Annual policy acknowledgements must be completed within fourteen (14) days of assignment.",
                ],
            ),
            (
                "3. Contact",
                [
                    "Questions: hr@potens.in",
                ],
            ),
        ],
        target_pages=10,
    )

    print(f"\nDone. Generated corpus in {DOCS_DIR}")
    print("Re-ingest: restart main.py or POST /ingest")


if __name__ == "__main__":
    main()
