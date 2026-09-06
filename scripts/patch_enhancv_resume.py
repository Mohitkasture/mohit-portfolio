"""Patch Mohit-Kasture-resume mk.pdf in place. Keep Enhancv design; update content."""

from __future__ import annotations

import shutil
from pathlib import Path

import pymupdf

SRC = Path(r"C:\Users\HP\Downloads\Mohit-Kasture-resume mk.pdf")
BACKUP = Path(r"C:\Users\HP\Downloads\Mohit-Kasture-resume mk.original-backup.pdf")
OUT_DOWNLOADS = Path(r"C:\Users\HP\Downloads\Mohit-Kasture-resume-corrected.pdf")
OUT_MK = Path(r"C:\Users\HP\Downloads\Mohit-Kasture-resume mk.pdf")
OUT_PORTFOLIO = Path(r"d:\projects\mohit-portfolio\home\static\home\files\Mohit-Kasture-resume.pdf")
FONTS = Path(r"d:\projects\mohit-portfolio\scripts\resume-fonts")
FONT_R = str(FONTS / "Inter-Regular.ttf")
FONT_B = str(FONTS / "Inter-Bold.ttf")
FONT_M = str(FONTS / "Rubik-Medium.ttf")

BLACK = (0, 0, 0)
BLUE = (0.0, 0.549, 1.0)
GRAY = (62 / 255, 62 / 255, 62 / 255)
ULINE = (0.6627, 0.6627, 0.6627)
ICON = (0.3961, 0.4118, 0.4275)
WHITE = (1, 1, 1)

LEFT = 38.69
BODY_X = 50.3
LEFT_W = 298.0
BODY_W = 286.0
RIGHT_X = 358.4
RIGHT_W = 199.2
SKILL_SIZE = 8.88
BODY_SIZE = 8.25
META_SIZE = 7.61
LH_BODY = 10.12


def wrap(font: pymupdf.Font, text: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if font.text_length(trial, size) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paint(page: pymupdf.Page, rect: pymupdf.Rect) -> None:
    page.draw_rect(rect, color=None, fill=WHITE, overlay=True)


def grow(rect: tuple[float, float, float, float] | pymupdf.Rect, dx: float, dy: float) -> pymupdf.Rect:
    r = pymupdf.Rect(rect)
    return pymupdf.Rect(r.x0 - dx, r.y0 - dy, r.x1 + dx, r.y1 + dy)


def redact_matching(page: pymupdf.Page, texts: set[str], x_min: float | None = None) -> None:
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                raw = (span.get("text") or "").replace("\xa0", " ").strip()
                if raw not in texts:
                    continue
                bb = pymupdf.Rect(span["bbox"])
                if x_min is not None and bb.x0 < x_min:
                    continue
                page.add_redact_annot(bb, fill=WHITE)


def redact_region(page: pymupdf.Page, rect: pymupdf.Rect, x_min: float | None = None) -> None:
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                bb = pymupdf.Rect(span["bbox"])
                if not rect.intersects(bb):
                    continue
                text = (span.get("text") or "").strip()
                if text in {"•", "SKILLS", "PROJECTS", "EXPERIENCE", "SUMMARY", "EDUCATION"}:
                    continue
                if x_min is not None and bb.x0 < x_min:
                    continue
                page.add_redact_annot(bb, fill=WHITE)


def put(
    page: pymupdf.Page,
    xy: tuple[float, float],
    text: str,
    *,
    fontname: str,
    size: float,
    color: tuple[float, float, float],
) -> float:
    fontfile = FONT_B if fontname.endswith("b") else FONT_R
    page.insert_text(xy, text, fontname=fontname, fontfile=fontfile, fontsize=size, color=color)
    return xy[0]


def draw_pin(page: pymupdf.Page, x: float, y: float) -> None:
    cx, cy = x + 2.75, y + 2.65
    page.draw_circle((cx, cy), 2.55, color=None, fill=ICON, overlay=True)
    page.draw_circle((cx, cy), 1.05, color=None, fill=WHITE, overlay=True)
    page.draw_polyline(
        [(cx - 2.15, cy + 1.35), (cx + 2.15, cy + 1.35), (cx, y + 7.45)],
        color=None,
        fill=ICON,
        overlay=True,
        closePath=True,
    )


def put_bullets(
    page: pymupdf.Page,
    font: pymupdf.Font,
    items: list[str],
    x: float,
    y_top: float,
    width: float,
    fontname: str,
    dot_x: float,
) -> None:
    baseline = y_top + 7.99
    for item in items:
        page.insert_text(
            (dot_x, baseline),
            "•",
            fontname="inter-r",
            fontfile=FONT_R,
            fontsize=BODY_SIZE,
            color=GRAY,
        )
        for line in wrap(font, item, BODY_SIZE, width):
            page.insert_text(
                (x, baseline),
                line,
                fontname=fontname,
                fontfile=FONT_R,
                fontsize=BODY_SIZE,
                color=GRAY,
            )
            baseline += LH_BODY
        baseline += 0.8


def skill_row(
    page: pymupdf.Page,
    font: pymupdf.Font,
    tags: list[str],
    x: float,
    baseline: float,
    max_x: float,
) -> None:
    cursor = x
    gap = 12.2
    for tag in tags:
        width = font.text_length(tag, SKILL_SIZE)
        if cursor + width > max_x:
            break
        page.insert_text(
            (cursor, baseline),
            tag,
            fontname="inter-b",
            fontfile=FONT_B,
            fontsize=SKILL_SIZE,
            color=GRAY,
        )
        ul = pymupdf.Rect(cursor - 5.7, baseline + 5.12, cursor + width + 5.8, baseline + 5.72)
        page.draw_rect(ul, color=None, fill=ULINE, overlay=True)
        cursor += width + gap


def patch() -> Path:
    if not BACKUP.exists():
        shutil.copy2(SRC, BACKUP)

    doc = pymupdf.open(BACKUP if BACKUP.exists() else SRC)
    page = doc[0]
    font_r = pymupdf.Font(fontfile=FONT_R)
    font_b = pymupdf.Font(fontfile=FONT_B)

    # Remove exact old strings we will replace.
    redact_matching(
        page,
        {
            "918817284530",
            "I am a dedicated Python and Django Developer with hands-on experience in",
            "backend development, RESTful API design, and PostgreSQL database",
            "management. I am skilled at building scalable web applications,",
            "collaborating across teams, and creating clean, efficient code. I am eager to",
            "contribute to innovative software projects and continuously enhance my",
            "skillset",
            "01/2026",
            "09/2025 - 12/2025",
            "03/2025 - 09/2025",
            "11/2025 - 02/2026",
            "03/2026",
            "07/2023 - 05/2025",
            "07/2020 - 05/2023",
            "www.enhancv.com",
            "Powered by",
        },
    )
    redact_matching(
        page,
        {
            "Python",
            "Django",
            "Gmail",
            "RESTful API",
            "PostgreSQL",
            "REST",
            "GitHub",
            "SQL",
            "Manual Testing",
            "RDBMS",
            "SDLC",
            "STLC",
            "Flask",
            "JavaScript",
            "React",
            "HTML",
            "CSS",
            "Git",
        },
        x_min=350,
    )
    # Body / project copy that will be rewritten.
    redact_region(page, pymupdf.Rect(48, 294, 338, 366), x_min=48)
    redact_region(page, pymupdf.Rect(48, 425, 338, 494), x_min=48)
    redact_region(page, pymupdf.Rect(48, 556, 338, 638), x_min=48)
    redact_region(page, pymupdf.Rect(357, 349, 560, 480), x_min=357)
    redact_region(page, pymupdf.Rect(357, 517, 560, 660), x_min=357)
    page.apply_redactions(images=0)

    # Cover leftover Enhancv skill underlines, logo, and unused original bullets.
    paint(page, pymupdf.Rect(357.2, 147.5, 559.0, 298.5))
    paint(page, pymupdf.Rect(428.0, 768.0, 575.0, 838.0))
    paint(page, pymupdf.Rect(36.0, 798.0, 130.0, 816.0))
    for y in (296.5, 316.8, 337.1, 357.4, 427.8, 448.1, 468.4, 478.5, 559.1, 579.4, 599.7, 620.0):
        paint(page, pymupdf.Rect(38.4, y - 0.6, 47.2, y + 10.2))
    for y in (373.9, 404.3, 424.6, 444.9, 465.2, 542.0, 562.3, 582.5, 613.0, 633.3):
        paint(page, pymupdf.Rect(357.8, y - 0.6, 367.0, y + 10.2))

    # Phone
    put(page, (48.84, 88.80), "+91 88172 84530", fontname="inter-b", size=META_SIZE, color=GRAY)
    # GitHub on the location row, aligned under email
    put(page, (123.84, 99.59), "github.com/Mohitkasture", fontname="inter-b", size=META_SIZE, color=GRAY)

    # Summary
    summary = (
        "Python and Django Developer with hands-on experience in backend development, "
        "REST API design, and PostgreSQL database management. Builds web applications "
        "and backend features with a focus on clean code, reliable frontend–backend "
        "integration, and practical development workflows."
    )
    y = 149.9 + 7.99
    for line in wrap(font_r, summary, BODY_SIZE, LEFT_W):
        put(page, (LEFT, y), line, fontname="inter-r", size=BODY_SIZE, color=GRAY)
        y += LH_BODY

    # Dates that need Present / month names. Keep calendar icons; move pin if needed.
    def replace_date_line(
        old_date_bbox: tuple[float, float, float, float],
        pin_rect: tuple[float, float, float, float],
        loc_bbox: tuple[float, float, float, float],
        new_date: str,
        location: str,
        baseline: float,
        date_x: float,
        loc_origin_x: float,
        loc_origin_y: float,
        pin_xy: tuple[float, float],
    ) -> None:
        paint(page, grow(old_date_bbox, 1.2, 0.8))
        paint(page, grow(pin_rect, 1.0, 1.0))
        paint(page, grow(loc_bbox, 1.2, 0.8))
        put(page, (date_x, baseline), new_date, fontname="inter-r", size=META_SIZE, color=GRAY)
        date_w = font_r.text_length(new_date, META_SIZE)
        pin_x = date_x + date_w + 8.0
        # Keep pin if it still fits; otherwise shift it.
        if pin_x < loc_origin_x - 2:
            pin_x = pin_xy[0]
        paint(page, pymupdf.Rect(pin_x - 0.5, pin_xy[1] - 0.5, pin_x + 7.0, pin_xy[1] + 8.2))
        draw_pin(page, pin_x, pin_xy[1])
        loc_x = pin_x + 9.7
        put(page, (loc_x, loc_origin_y), location, fontname="inter-r", size=META_SIZE, color=GRAY)

    replace_date_line(
        (50.11, 272.36, 82.2, 281.57),
        (91.7, 273.5, 97.3, 280.9),
        (101.4, 272.36, 170.0, 281.57),
        "Jan 2026 – Present",
        "Ahmedabad, India",
        279.73,
        50.11,
        101.4,
        279.73,
        (91.7, 273.5),
    )
    replace_date_line(
        (50.11, 403.66, 120.5, 412.87),
        (129.8, 404.8, 135.3, 412.2),
        (139.7, 403.66, 210.0, 412.87),
        "Sep 2025 – Dec 2025",
        "Ahmedabad, India",
        403.66 + 7.37,
        50.11,
        139.7,
        403.66 + 7.37,
        (129.8, 404.8),
    )
    replace_date_line(
        (50.11, 534.96, 122.0, 544.2),
        (131.7, 536.1, 137.2, 543.5),
        (141.2, 534.96, 212.0, 544.2),
        "Mar 2025 – Sep 2025",
        "Ahmedabad, India",
        534.96 + 7.37,
        50.11,
        141.2,
        534.96 + 7.37,
        (131.7, 536.1),
    )
    replace_date_line(
        (50.11, 701.76, 121.0, 711.0),
        (131.1, 702.9, 136.6, 710.4),
        (140.6, 701.76, 175.0, 711.0),
        "Jul 2023 – May 2025",
        "Bhopal",
        701.76 + 7.37,
        50.11,
        140.6,
        701.76 + 7.37,
        (131.1, 702.9),
    )
    replace_date_line(
        (50.11, 747.46, 121.0, 756.7),
        (131.1, 748.6, 136.6, 756.0),
        (140.8, 747.46, 175.0, 756.7),
        "Jul 2020 – May 2023",
        "Bhopal",
        747.46 + 7.37,
        50.11,
        140.8,
        747.46 + 7.37,
        (131.1, 748.6),
    )
    replace_date_line(
        (369.8, 339.59, 449.0, 348.8),
        (448.9, 340.7, 454.4, 348.2),
        (458.3, 339.59, 530.0, 348.8),
        "Nov 2025 – Feb 2026",
        "Ahmedabad, India",
        339.59 + 7.37,
        369.8,
        458.3,
        339.59 + 7.37,
        (448.9, 340.7),
    )
    replace_date_line(
        (369.8, 507.66, 413.0, 516.9),
        (412.7, 508.8, 418.2, 516.3),
        (422.4, 507.66, 500.0, 516.9),
        "Mar 2026",
        "Ahmedabad, India",
        507.66 + 7.37,
        369.8,
        422.4,
        507.66 + 7.37,
        (412.7, 508.8),
    )

    put_bullets(
        page,
        font_r,
        [
            "Designed and implemented REST APIs with Python and Django for core business workflows and frontend integrations.",
            "Designed PostgreSQL schemas and data relationships for storage, processing, and application workflows.",
            "Implemented backend features for user data management and API integrations.",
            "Kept frontend–backend communication reliable through structured, documented API contracts.",
        ],
        BODY_X,
        296.5,
        BODY_W,
        "inter-r",
        41.2,
    )
    put_bullets(
        page,
        font_r,
        [
            "Wrote PostgreSQL queries and worked on schema changes for application data.",
            "Used Git and GitHub for feature branches, commits, and pull requests.",
            "Followed main vs development branch workflows on live project code.",
            "Configured environments with .env files so credentials stay out of source.",
        ],
        BODY_X,
        427.8,
        BODY_W,
        "inter-r",
        41.2,
    )
    put_bullets(
        page,
        font_r,
        [
            "Practiced Python problem-solving for backend-oriented tasks.",
            "Wrote SQL for retrieval and updates across relational tables.",
            "Learned manual testing: test cases, testing types, and SDLC / STLC.",
        ],
        BODY_X,
        559.1,
        BODY_W,
        "inter-r",
        41.2,
    )

    # Flowcreator description + bullets
    desc = "AI-powered social content SaaS"
    put(page, (RIGHT_X, 351.7 + 7.99), desc, fontname="inter-r", size=BODY_SIZE, color=GRAY)
    put(
        page,
        (RIGHT_X, 519.8 + 7.99),
        "A meditation app for user management and",
        fontname="inter-r",
        size=BODY_SIZE,
        color=GRAY,
    )
    put(
        page,
        (RIGHT_X, 529.9 + 7.99),
        "session tracking",
        fontname="inter-r",
        size=BODY_SIZE,
        color=GRAY,
    )
    put_bullets(
        page,
        font_r,
        [
            "Built Django backend APIs and workflows for caption and image generation, scheduling, and publishing.",
            "Implemented caption generation with prompt enhancement and tone selection, plus image generation from user inputs.",
            "Established role-based access control and subscription billing on a SaaS architecture.",
        ],
        370.0,
        373.9,
        187.0,
        "inter-r",
        360.9,
    )
    put_bullets(
        page,
        font_r,
        [
            "Built Django REST Framework APIs over PostgreSQL for users, sessions, completion tracking, and activity updates.",
            "Documented APIs so the frontend can rely on a stable contract.",
        ],
        370.0,
        542.0,
        187.0,
        "inter-r",
        360.9,
    )

    # Skills: original underline-tag style, grouped with small category labels.
    groups = [
        ("Backend", ["Python", "Django", "REST APIs"]),
        ("", ["Django REST Framework"]),
        ("Database", ["PostgreSQL", "SQL", "RDBMS"]),
        ("Frontend", ["HTML", "CSS", "JavaScript", "React"]),
        ("Tools", ["Git", "GitHub"]),
        ("Testing", ["Manual Testing", "SDLC", "STLC"]),
    ]
    y = 158.2
    for label, tags in groups:
        if label:
            put(page, (RIGHT_X, y), label, fontname="inter-b", size=7.4, color=BLUE)
            y += 12.6
        skill_row(page, font_b, tags, 364.09, y, 557.6)
        y += 14.8

    OUT_DOWNLOADS.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_DOWNLOADS, garbage=4, deflate=True)
    doc.close()
    shutil.copy2(OUT_DOWNLOADS, OUT_MK)
    shutil.copy2(OUT_DOWNLOADS, OUT_PORTFOLIO)
    return OUT_DOWNLOADS


if __name__ == "__main__":
    path = patch()
    print("wrote", path)
