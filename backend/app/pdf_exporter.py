import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_cyrillic_font():
    """Регистрация кириллического шрифта."""
    font_path = "C:\\Windows\\Fonts\\arial.ttf"  # Системный Arial для Windows
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Arial", font_path))
        return "Arial"
    return "Helvetica"

def export_to_pdf(layout: dict, file_path: str = "house_plan.pdf") -> str:
    c = canvas.Canvas(file_path, pagesize=letter)
    font_name = register_cyrillic_font()

    # Заголовок
    c.setFont(font_name, 16)
    c.drawString(50, 750, "План дома (Чертеж)")

    scale = 30
    offset_x = 50
    offset_y = 400

    for room_name, room_info in layout.items():
        x1, y1, x2, y2 = room_info["bounds"]

        # Перевод координат
        px1 = offset_x + x1 * scale
        py1 = offset_y + y1 * scale
        pw = room_info["width"] * scale
        ph = room_info["height"] * scale

        # Рисуем контур комнаты
        c.setLineWidth(1)
        c.rect(px1, py1, pw, ph)

        # Отрисовка текста (Наименование + Площадь)
        c.setFont(font_name, 9)
        c.drawString(px1 + 5, py1 + ph / 2, f"{room_name} ({room_info['area']} м²)")

    c.save()
    return file_path