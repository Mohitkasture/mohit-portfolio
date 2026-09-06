"""Build the one-page resume PDF served on the portfolio."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "home" / "static" / "home" / "files" / "Mohit-Kasture-resume.pdf"

INK = HexColor("#16181c")
MUTED = HexColor("#5c6570")
LINE = HexColor("#d8dce2")
ACCENT = HexColor("#3d6b1f")
HEADER = HexColor("#08090b")
LIME = HexColor("#d4ff3f")


def wrap(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if c.stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def section_title(c: canvas.Canvas, title: str, x: float, y: float, width: float) -> float:
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 9.2)
    c.drawString(x, y, title.upper())
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(x, y - 3.2, x + width, y - 3.2)
    return y - 14


def bullet(c: canvas.Canvas, text: str, x: float, y: float, width: float, size: float = 8.4) -> float:
    c.setFillColor(ACCENT)
    c.circle(x + 2.2, y + 2.1, 1.15, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica", size)
    lines = wrap(c, text, "Helvetica", size, width - 10)
    for i, line in enumerate(lines):
        c.drawString(x + 8, y - (i * 11.2), line)
    return y - (len(lines) * 11.2) - 3.2


def role_head(
    c: canvas.Canvas,
    title: str,
    org: str,
    dates: str,
    place: str,
    x: float,
    y: float,
    width: float,
) -> float:
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, title)
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(x + width, y, dates)
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.6)
    c.drawString(x, y - 12, org)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawRightString(x + width, y - 12, place)
    return y - 24


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = A4
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=0)
    c.setTitle("Mohit Kasture — Python & Django Developer")
    c.setAuthor("Mohit Kasture")

    # Header
    c.setFillColor(HEADER)
    c.rect(0, height - 42 * mm, width, 42 * mm, stroke=0, fill=1)
    c.setFillColor(LIME)
    c.rect(0, height - 42 * mm, width, 2.2 * mm, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(16 * mm, height - 18 * mm, "MOHIT KASTURE")
    c.setFillColor(LIME)
    c.setFont("Helvetica", 10.5)
    c.drawString(16 * mm, height - 25.2 * mm, "Python & Django Developer")
    c.setFillColor(HexColor("#c9cdd3"))
    c.setFont("Helvetica", 8)
    c.drawString(
        16 * mm,
        height - 32.4 * mm,
        "Ahmedabad  ·  +91 88172 84530  ·  mkymohitkumaryadav0@gmail.com",
    )
    c.drawString(
        16 * mm,
        height - 37.4 * mm,
        "linkedin.com/in/mohit-kasture-812a44261  ·  github.com/Mohitkasture",
    )

    x = 16 * mm
    content_w = width - 32 * mm
    y = height - 50 * mm

    y = section_title(c, "Summary", x, y, content_w)
    summary = (
        "I am a dedicated Python and Django Developer with hands-on experience in backend development, "
        "REST API design, and PostgreSQL database management. I am skilled at building scalable web "
        "applications, collaborating across teams, and creating clean, efficient code. I am eager to "
        "contribute to innovative software projects and continuously enhance my skillset."
    )
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.6)
    for line in wrap(c, summary, "Helvetica", 8.6, content_w):
        c.drawString(x, y, line)
        y -= 11.4
    y -= 8

    y = section_title(c, "Experience", x, y, content_w)
    y = role_head(
        c,
        "Python Developer",
        "AppUnik — Enterprise web solutions",
        "Jan 2026 – Present",
        "Ahmedabad, India",
        x,
        y,
        content_w,
    )
    for item in (
        "Designed and implemented REST APIs with Python and Django for core business workflows and frontend integrations.",
        "Designed PostgreSQL schemas and data relationships for storage, processing, and application workflows.",
        "Implemented backend features for user data management and API integrations.",
        "Kept frontend–backend communication reliable through structured, documented API contracts.",
    ):
        y = bullet(c, item, x, y, content_w)

    y -= 4
    y = role_head(
        c,
        "Backend Intern",
        "AppUnik",
        "Sep 2025 – Dec 2025",
        "Ahmedabad, India",
        x,
        y,
        content_w,
    )
    for item in (
        "Wrote PostgreSQL queries and worked on schema changes for application data.",
        "Used Git and GitHub for feature branches, commits, and pull requests.",
        "Followed main vs development branch workflows on live project code.",
        "Configured environments with .env files so credentials stay out of source.",
    ):
        y = bullet(c, item, x, y, content_w)

    y -= 4
    y = role_head(
        c,
        "Software Intern",
        "Qspider — Python, SQL, Django, manual testing",
        "Mar 2025 – Sep 2025",
        "Ahmedabad, India",
        x,
        y,
        content_w,
    )
    for item in (
        "Practiced Python problem-solving for backend-oriented tasks.",
        "Wrote SQL for retrieval and updates across relational tables.",
        "Learned manual testing: test cases, testing types, and SDLC / STLC.",
    ):
        y = bullet(c, item, x, y, content_w)

    y -= 8
    y = section_title(c, "Projects", x, y, content_w)
    y = role_head(
        c,
        "Flowcreator — AI-powered social content SaaS",
        "Django backend for generation, scheduling, publishing, RBAC, and billing",
        "Nov 2025 – Feb 2026",
        "Ahmedabad, India",
        x,
        y,
        content_w,
    )
    for item in (
        "Built Django backend APIs and workflows for caption and image generation, scheduling, and publishing.",
        "Implemented caption generation with prompt enhancement and tone selection, plus image generation from user inputs.",
        "Established role-based access control and subscription billing on a SaaS architecture.",
    ):
        y = bullet(c, item, x, y, content_w)

    y -= 4
    y = role_head(
        c,
        "Meditation App",
        "Backend for user management and session tracking",
        "Mar 2026",
        "Ahmedabad, India",
        x,
        y,
        content_w,
    )
    for item in (
        "Built Django REST Framework APIs over PostgreSQL for users, sessions, completion tracking, and activity updates.",
        "Documented APIs so the frontend can rely on a stable contract.",
    ):
        y = bullet(c, item, x, y, content_w)

    y -= 8
    y = section_title(c, "Skills", x, y, content_w)
    skills = (
        ("Backend", "Python, Django, Django REST Framework, REST APIs"),
        ("Database", "PostgreSQL, SQL, RDBMS"),
        ("Frontend", "HTML, CSS, JavaScript, React"),
        ("Tools", "Git, GitHub"),
        ("Testing", "Manual Testing, SDLC, STLC"),
    )
    c.setFont("Helvetica", 8.6)
    for label, value in skills:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 8.6)
        c.drawString(x, y, f"{label}:")
        label_w = c.stringWidth(f"{label}:  ", "Helvetica-Bold", 8.6)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.6)
        c.drawString(x + label_w, y, value)
        y -= 12.2

    y -= 6
    y = section_title(c, "Education", x, y, content_w)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(x, y, "Master of Computer Applications (MCA)")
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(x + content_w, y, "Jul 2023 – May 2025")
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.4)
    c.drawString(x, y - 12, "Rajiv Gandhi Proudyogiki Vishwavidyalaya · Bhopal")
    y -= 28
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(x, y, "Bachelor of Science (BSc)")
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(x + content_w, y, "Jul 2020 – May 2023")
    c.setFillColor(INK)
    c.setFont("Helvetica", 8.4)
    c.drawString(x, y - 12, "Barkatullah University · Bhopal")
    if y - 24 < 12 * mm:
        raise RuntimeError(f"Resume overflowed the page (y={y:.1f})")

    c.showPage()
    c.save()
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
