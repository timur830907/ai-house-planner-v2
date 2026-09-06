import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(width: float, length: float, layout_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#2c3e50"))
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph(f"<b>БИМ Проект Дома (BIM ARCHITECT)</b>", title_style))
    story.append(Spacer(1, 12))

    area = round(width * length, 2)
    shape_name = layout_data.get("shape", "rectangle")
    story.append(Paragraph(f"<b>Габариты:</b> {width} м x {length} м | <b>Площадь:</b> {area} м² | <b>Форма:</b> {shape_name}", text_style))
    story.append(Spacer(1, 15))

    # Экспликация помещений
    data = [["Наименование", "Тип покрытия", "Примерная площадь"]]
    rooms = layout_data.get("rooms", {})
    for r_name, r_info in rooms.items():
        b = r_info.get("bounds", [0, 0, 0, 0])
        r_area = round((b[2] - b[0]) * (b[3] - b[1]), 2)
        f_type = "Дерево" if r_info.get("floor_type") == "wood" else "Плитка"
        data.append([r_name, f_type, f"{r_area} м²"])

    t = Table(data, colWidths=[200, 150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#34495e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
    ]))
    story.append(t)

    doc.build(story)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value