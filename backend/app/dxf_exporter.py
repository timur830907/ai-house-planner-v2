import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(width: float, length: float, layout_data: dict) -> bytes:
    """
    Генерирует PDF-документ с параметрами планировки и таблицей помещений.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    )

    story.append(Paragraph("Отчет планировки: AI House Planner v2.0", title_style))
    story.append(Paragraph(f"Общие габариты здания: {width} м x {length} м (Площадь: {width * length:.2f} кв. м)", styles['Normal']))
    story.append(Spacer(1, 15))

    table_data = [["Помещение", "Координаты (x1, y1, x2, y2)", "Площадь (кв. м)"]]
    rooms = layout_data.get("rooms", {})

    for room_name, data in rooms.items():
        bounds = data.get("bounds") if isinstance(data, dict) else data
        x1, y1, x2, y2 = bounds
        area = (x2 - x1) * (y2 - y1)
        bounds_str = f"[{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]"
        table_data.append([room_name, bounds_str, f"{area:.2f}"])

    t = Table(table_data, colWidths=[150, 220, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F4F4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(t)
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()