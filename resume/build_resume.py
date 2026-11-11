"""Build public/resume.pdf from resume/resume.yaml.

Run from the repo root (dependencies are fetched by uv, nothing to install):
    npm run resume
which runs:
    uv run --no-project --with reportlab==5.1.0 --with pyyaml==6.0.3 python resume/build_resume.py

Layout: US Letter, Helvetica, a centred header, dark-blue section headings with a rule under each,
and entries with the organisation on the left and dates on the right.
"""

from html import escape
from pathlib import Path

import yaml
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Same content -> byte-identical PDF (no embedded timestamp or random ID), so a rebuild with no
# content change doesn't show up as a change in git.
rl_config.invariant = 1

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "resume" / "resume.yaml"
OUTPUT = ROOT / "public" / "resume.pdf"

NAVY = colors.HexColor("#1f3a60")
GREY = colors.HexColor("#555555")
MARGIN = 0.7 * inch
CONTENT_WIDTH = LETTER[0] - 2 * MARGIN

STYLES = {
    "name": ParagraphStyle(
        "name", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY, alignment=TA_CENTER
    ),
    "title": ParagraphStyle(
        "title", fontName="Helvetica", fontSize=12, leading=15, textColor=GREY, alignment=TA_CENTER
    ),
    "contact": ParagraphStyle(
        "contact", fontName="Helvetica", fontSize=9, leading=12, textColor=GREY, alignment=TA_CENTER
    ),
    "heading": ParagraphStyle(
        "heading", fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=NAVY
    ),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=13),
    "org": ParagraphStyle("org", fontName="Helvetica-Bold", fontSize=10, leading=13),
    "dates": ParagraphStyle(
        "dates", fontName="Helvetica", fontSize=10, leading=13, textColor=GREY, alignment=2
    ),
    "role": ParagraphStyle(
        "role", fontName="Helvetica-Oblique", fontSize=10, leading=13, textColor=GREY, leftIndent=6
    ),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, leading=13),
}


def text(value: str) -> str:
    """Escape for ReportLab's mini-markup (&, <, >)."""
    return escape(" ".join(value.split()), quote=False)


def heading(title: str) -> list:
    return [
        Spacer(1, 10),
        Paragraph(text(title.upper()), STYLES["heading"]),
        HRFlowable(width="100%", thickness=0.8, color=NAVY, spaceBefore=2, spaceAfter=5),
    ]


def left_right(left: Paragraph, right: Paragraph) -> Table:
    """One line with `left` flush left and `right` flush right."""
    table = Table([[left, right]], colWidths=[CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.3])
    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def entry(item: dict) -> KeepTogether:
    """An experience or internship entry: organisation and dates, role, bullets."""
    parts = [
        left_right(
            Paragraph(text(item["organization"]), STYLES["org"]),
            Paragraph(text(item["dates"]), STYLES["dates"]),
        ),
        Paragraph(text(item["role"]), STYLES["role"]),
        ListFlowable(
            [ListItem(Paragraph(text(b), STYLES["bullet"]), leftIndent=13) for b in item["bullets"]],
            bulletType="bullet",
            start="•",
            bulletFontSize=9,
            leftIndent=13,
            bulletDedent=8,
            bulletOffsetY=-1,
        ),
        Spacer(1, 6),
    ]
    return KeepTogether(parts)


def build(content: dict) -> list:
    contact = " &nbsp;|&nbsp; ".join(
        f'<a href="{escape(c["url"])}" color="#555555">{text(c["text"])}</a>'
        for c in content["contact"]
    )
    story = [
        Paragraph(text(content["name"].upper()), STYLES["name"]),
        Paragraph(text(content["title"]), STYLES["title"]),
        Spacer(1, 2),
        Paragraph(contact, STYLES["contact"]),
    ]

    story += heading("Professional Summary")
    story.append(Paragraph(text(content["summary"]), STYLES["body"]))

    story += heading("Core Skills")
    for skill in content["skills"]:
        story.append(
            Paragraph(f"<b>{text(skill['label'])}:</b> {text(skill['items'])}", STYLES["body"])
        )

    story += heading("Professional Experience")
    story += [entry(item) for item in content["experience"]]

    story += heading("Internships")
    story += [entry(item) for item in content["internships"]]

    story += heading("Education")
    for school in content["education"]:
        story.append(
            left_right(
                Paragraph(text(school["degree"]), STYLES["org"]),
                Paragraph(text(school["date"]), STYLES["dates"]),
            )
        )
        story.append(Paragraph(text(school["school"]), STYLES["role"]))
        story.append(Spacer(1, 4))
    return story


def main() -> None:
    content = yaml.safe_load(CONTENT.read_text(encoding="utf-8"))
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=f"{content['name']} - Resume",
        author=content["name"],
    )
    doc.build(build(content))
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
