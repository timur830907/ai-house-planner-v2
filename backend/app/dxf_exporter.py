import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        self.drawString(50, 30, f"BIM ARCHITECT V2.0 — Страница {self._pageNumber} из {page_count}")
        self.restoreState()

def generate_pdf_report(layout: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=15
    )

    elements = []

    # Заголовок
    elements.append(Paragraph("Проект дома / House Project Plan", title_style))
    
    dims = layout.get("dimensions", {})
    w_m = dims.get("width", 12.0)
    l_m = dims.get("length", 14.0)
    shape = layout.get("shape", "rectangle")
    area = w_m * l_m

    info_text = f"<b>Габариты:</b> {w_m} м x {l_m} м &nbsp;&nbsp;|&nbsp;&nbsp; <b>Площадь:</b> {area:.1f} м² &nbsp;&nbsp;|&nbsp;&nbsp; <b>Форма:</b> {shape.upper()}"
    elements.append(Paragraph(info_text, body_style))
    elements.append(Spacer(1, 15))

    # Таблица помещений
    rooms = layout.get("rooms", {})
    table_data = [["Помещение / Room", "Тип покрытия / Floor", "Площадь / Area (m²)"]]
    
    for r_name, r_data in rooms.items():
        b = r_data.get("bounds", [0, 0, 1, 1])
        r_area = (b[2] - b[0]) * (b[3] - b[1])
        f_type = "Дерево (Wood)" if r_data.get("floor_type") == "wood" else "Плитка (Tile)"
        table_data.append([str(r_name), f_type, f"{r_area:.2f} м²"])

    t = Table(table_data, colWidths=[250, 200, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9F9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    
    elements.append(t)
    
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()