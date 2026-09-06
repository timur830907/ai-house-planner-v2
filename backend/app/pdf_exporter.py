import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_pdf_report(layout: dict) -> bytes:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width_page, height_page = landscape(A4)

    # Заголовок
    p.setFont("Helvetica-Bold", 18)
    p.drawString(40, height_page - 40, "Проект дома / House Plan (BIM ARCHITECT)")

    dims = layout.get("dimensions", {})
    w_m = dims.get("width", 12.0)
    l_m = dims.get("length", 14.0)
    shape = layout.get("shape", "rectangle")
    
    p.setFont("Helvetica", 11)
    p.drawString(40, height_page - 60, f"Габариты: {w_m} м x {l_m} м | Площадь: {w_m * l_m:.1f} м² | Форма: {shape}")

    # Отрисовка схемы (2D-план)
    rooms = layout.get("rooms", {})
    if rooms:
        # Масштабирование схемы под холст PDF
        scale = min(400 / w_m, 350 / l_m)
        offset_x = 50
        offset_y = 100

        p.setStrokeColor(colors.HexColor("#2C3E50"))
        p.setLineWidth(2)

        for room_name, room_data in rooms.items():
            bounds = room_data.get("bounds", [0, 0, 1, 1])
            x1, y1, x2, y2 = bounds

            px1 = offset_x + x1 * scale
            py1 = offset_y + y1 * scale
            pw = (x2 - x1) * scale
            ph = (y2 - y1) * scale

            # Заливка помещения
            p.setFillColor(colors.HexColor("#ECF0F1") if room_data.get("floor_type") == "wood" else colors.HexColor("#E1F5FE"))
            p.rect(px1, py1, pw, ph, fill=1, stroke=1)

            # Название комнаты
            p.setFillColor(colors.HexColor("#2C3E50"))
            p.setFont("Helvetica-Bold", 9)
            p.drawCentredString(px1 + pw / 2, py1 + ph / 2 + 5, str(room_name))
            
            # Площадь
            area = (x2 - x1) * (y2 - y1)
            p.setFont("Helvetica", 8)
            p.drawCentredString(px1 + pw / 2, py1 + ph / 2 - 8, f"{area:.1f} m²")

    # Справа рисуем экспликацию (таблицу)
    table_x = 500
    table_y = height_page - 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(table_x, table_y, "Экспликация помещений")
    
    p.setFont("Helvetica", 9)
    y_curr = table_y - 20
    for r_name, r_data in rooms.items():
        b = r_data.get("bounds", [0, 0, 1, 1])
        area = (b[2] - b[0]) * (b[3] - b[1])
        p.drawString(table_x, y_curr, f"• {r_name}: {area:.1f} м²")
        y_curr -= 16

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()