from datetime import datetime
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.core.errors import archived_record, not_found, validation_failure
from app.models.common import generate_uuid
from app.models.estimate import Estimate, EstimateDocument, EstimateItem, EstimateRevision
from app.models.identity import Company, User
from app.services.estimates import calculate_revision_totals, latest_revision

DOCUMENT_TYPE_ESTIMATE_QUOTE_PDF = "estimate_quote_pdf"
PDF_FONT_NAME = "BuildIQUnicode"
REGISTERED_FONT_NAME: Optional[str] = None


def get_estimate_document_for_company(
    db: Session,
    *,
    company_id: str,
    document_id: str,
) -> EstimateDocument:
    document = (
        db.query(EstimateDocument)
        .filter(
            EstimateDocument.id == document_id,
            EstimateDocument.company_id == company_id,
            EstimateDocument.archived_at.is_(None),
        )
        .one_or_none()
    )
    if document is None:
        raise not_found()
    return document


def resolve_storage_file_path(storage_path: str, relative_file_path: str) -> Path:
    storage_root = Path(storage_path).expanduser().resolve()
    output_path = (storage_root / relative_file_path).resolve()
    try:
        output_path.relative_to(storage_root)
    except ValueError as exc:
        raise validation_failure("Невалидна патека за PDF документ.") from exc
    return output_path


def resolve_estimate_revision(
    estimate: Estimate,
    *,
    revision_id: Optional[str],
) -> EstimateRevision:
    if revision_id is None:
        revision = latest_revision(estimate)
    else:
        revision = next(
            (
                item
                for item in estimate.revisions
                if item.id == revision_id and item.archived_at is None
            ),
            None,
        )
    if revision is None:
        raise not_found("Ревизијата на понудата не е пронајдена.")
    if revision.estimate_id != estimate.id or revision.company_id != estimate.company_id:
        raise validation_failure("Ревизијата не припаѓа на избраната понуда.")
    return revision


def create_estimate_pdf_document(
    db: Session,
    *,
    company: Company,
    current_user: User,
    estimate: Estimate,
    revision_id: Optional[str],
    storage_path: str,
) -> EstimateDocument:
    if estimate.company_id != company.id:
        raise not_found()
    if estimate.archived_at is not None or estimate.status == "archived":
        raise archived_record("Не може да се генерира PDF за архивирана понуда.")

    revision = resolve_estimate_revision(estimate, revision_id=revision_id)
    generated_at = datetime.utcnow()
    document_id = generate_uuid()
    relative_file_path = (
        Path("estimate-documents")
        / company.id
        / estimate.id
        / f"{document_id}.pdf"
    ).as_posix()
    output_path = resolve_storage_file_path(storage_path, relative_file_path)
    items = [
        item
        for item in sorted(revision.items, key=lambda estimate_item: estimate_item.sort_order)
        if item.archived_at is None
    ]
    totals = calculate_revision_totals(revision)

    write_estimate_pdf(
        output_path=output_path,
        company=company,
        estimate=estimate,
        revision=revision,
        items=items,
        totals=totals,
        generated_at=generated_at,
    )

    document = EstimateDocument(
        id=document_id,
        company_id=company.id,
        estimate_id=estimate.id,
        revision_id=revision.id,
        document_type=DOCUMENT_TYPE_ESTIMATE_QUOTE_PDF,
        file_path=relative_file_path,
        generated_by_user_id=current_user.id,
        generated_at=generated_at,
    )
    db.add(document)
    db.flush()
    return document


def register_pdf_font() -> str:
    global REGISTERED_FONT_NAME

    if REGISTERED_FONT_NAME is not None:
        return REGISTERED_FONT_NAME

    candidate_paths = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/local/share/fonts/DejaVuSans.ttf"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for font_path in candidate_paths:
        if not font_path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(PDF_FONT_NAME, str(font_path)))
        except Exception:
            continue
        REGISTERED_FONT_NAME = PDF_FONT_NAME
        return REGISTERED_FONT_NAME

    REGISTERED_FONT_NAME = "Helvetica"
    return REGISTERED_FONT_NAME


def paragraph_text(value: object) -> str:
    text = "-" if value is None or value == "" else str(value)
    return escape(text).replace("\n", "<br/>")


def format_datetime(value: datetime) -> str:
    return value.strftime("%d.%m.%Y %H:%M")


def format_money(value: float) -> str:
    return f"{float(value or 0.0):.2f} ден."


def format_number(value: float) -> str:
    return f"{float(value or 0.0):.4g}"


def status_label(status_value: str) -> str:
    labels = {
        "draft": "Нацрт",
        "sent": "Испратена",
        "accepted": "Прифатена",
        "rejected": "Одбиена",
        "archived": "Архивирана",
    }
    return labels.get(status_value, status_value)


def item_type_label(item_type: str) -> str:
    labels = {
        "material": "Материјал",
        "labor": "Работна рака",
        "service": "Услуга",
        "discount": "Попуст",
        "adjustment": "Корекција",
    }
    return labels.get(item_type, item_type)


def build_styles(font_name: str) -> dict[str, ParagraphStyle]:
    sample_styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "BuildIQTitle",
            parent=sample_styles["Title"],
            fontName=font_name,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        ),
        "heading": ParagraphStyle(
            "BuildIQHeading",
            parent=sample_styles["Heading2"],
            fontName=font_name,
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "normal": ParagraphStyle(
            "BuildIQNormal",
            parent=sample_styles["Normal"],
            fontName=font_name,
            fontSize=9,
            leading=12,
        ),
        "small": ParagraphStyle(
            "BuildIQSmall",
            parent=sample_styles["Normal"],
            fontName=font_name,
            fontSize=8,
            leading=10,
        ),
    }


def p(value: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(paragraph_text(value), style)


def add_key_value_section(
    story: list[object],
    *,
    title: str,
    rows: list[tuple[str, object]],
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(p(title, styles["heading"]))
    table = Table(
        [[p(label, styles["small"]), p(value, styles["normal"])] for label, value in rows],
        colWidths=[45 * mm, 125 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), styles["normal"].fontName),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
            ]
        )
    )
    story.append(table)


def item_table_data(
    *,
    items: list[EstimateItem],
    styles: dict[str, ParagraphStyle],
) -> list[list[object]]:
    rows: list[list[object]] = [
        [
            p("Назив", styles["small"]),
            p("Опис", styles["small"]),
            p("Тип", styles["small"]),
            p("Количина", styles["small"]),
            p("Единица", styles["small"]),
            p("Единечна цена", styles["small"]),
            p("Вкупно", styles["small"]),
        ]
    ]
    for item in items:
        rows.append(
            [
                p(item.name, styles["small"]),
                p(item.description, styles["small"]),
                p(item_type_label(item.item_type), styles["small"]),
                p(format_number(item.quantity), styles["small"]),
                p(item.unit, styles["small"]),
                p(format_money(item.unit_price), styles["small"]),
                p(format_money(item.total_price), styles["small"]),
            ]
        )
    if len(rows) == 1:
        rows.append([p("Нема ставки.", styles["small"]), "", "", "", "", "", ""])
    return rows


def add_items_section(
    story: list[object],
    *,
    items: list[EstimateItem],
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(p("Ставки", styles["heading"]))
    table = Table(
        item_table_data(items=items, styles=styles),
        colWidths=[34 * mm, 29 * mm, 22 * mm, 20 * mm, 18 * mm, 27 * mm, 27 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), styles["small"].fontName),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)


def add_totals_section(
    story: list[object],
    *,
    totals: dict[str, float],
    styles: dict[str, ParagraphStyle],
) -> None:
    add_key_value_section(
        story,
        title="Вкупно",
        rows=[
            ("Меѓузбир", format_money(totals["subtotal"])),
            ("Попуст", format_money(totals["discount_total"])),
            ("Корекција", format_money(totals["adjustment_total"])),
            ("Данок", format_money(totals["tax_total"])),
            ("Вкупно за плаќање", format_money(totals["total"])),
        ],
        styles=styles,
    )


def write_estimate_pdf(
    *,
    output_path: Path,
    company: Company,
    estimate: Estimate,
    revision: EstimateRevision,
    items: list[EstimateItem],
    totals: dict[str, float],
    generated_at: datetime,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font_name = register_pdf_font()
    styles = build_styles(font_name)
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    story: list[object] = [p("Понуда", styles["title"])]

    add_key_value_section(
        story,
        title="Компанија",
        rows=[
            ("Име", company.name),
            ("Даночен број", company.tax_number),
            ("Адреса", company.address),
            ("Телефон", company.phone),
            ("Е-пошта", company.email),
        ],
        styles=styles,
    )
    add_key_value_section(
        story,
        title="Клиент",
        rows=[
            ("Име", estimate.customer.name),
            ("Телефон", estimate.customer.phone),
            ("Е-пошта", estimate.customer.email),
            ("Адреса", estimate.customer.address),
        ],
        styles=styles,
    )
    add_key_value_section(
        story,
        title="Проект и објект",
        rows=[
            ("Понуда", estimate.title),
            ("Проект", estimate.project.name),
            ("Објект", estimate.property.name),
            ("Адреса на објект", estimate.property.address or estimate.project.address),
            ("Град", estimate.property.city),
            ("Статус", status_label(estimate.status)),
            ("Ревизија", revision.revision_number),
            ("Генерирано", format_datetime(generated_at)),
        ],
        styles=styles,
    )
    add_items_section(story, items=items, styles=styles)
    add_totals_section(story, totals=totals, styles=styles)

    notes = revision.notes or estimate.description
    if notes:
        story.append(p("Белешки", styles["heading"]))
        story.append(p(notes, styles["normal"]))

    story.append(Spacer(1, 8 * mm))
    story.append(p("Документот е генериран од BuildIQ.", styles["small"]))
    document.build(story)
