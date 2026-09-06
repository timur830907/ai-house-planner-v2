import io
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Словарь для безопасной транслитерации кириллицы на случай отсутствия TTF-шрифтов
CYR_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
    'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
    'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
    'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
}

def cyr_to_lat(text: str) -> str:
    return "".join(CYR_TO_LAT.get(ch, ch) for ch in text)

def generate_pdf_report(layout: dict) -> bytes:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    font_name = "Helvetica-Bold"
    font_regular = "Helvetica"
    has_cyrillic_font = False
    
    # Попытка загрузить кириллический TTF-шрифт
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    
    for font_path in possible_fonts:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('CustomCyrillic', font_path))
                font_name = 'CustomCyrillic'
                font_regular = 'CustomCyrillic'
                has_cyrillic_font = True
                break
            except Exception:
                pass

    # Функция-обертка для безопасного вывода текста без ошибки 500
    def safe_str(text: str) -> str:
        if has_cyrillic_font:
            return text
        return cyr_to_lat(text)

    # 1. Заголовок
    p.setFont(font_name, 18)
    p.setFillColor(colors.HexColor('#2C3E50'))
    p.drawString(40, 540, safe_str("ПРОЕКТ ДОМА / HOUSE PLAN REPORT"))
    
    dims = layout.get("dimensions", {})
    w = dims.get("width", 12.0)
    l = dims.get("length", 14.0)
    shape = layout.get("shape", "rectangle")
    
    # 2. Параметры дома
    p.setFont(font_regular, 11)
    p.setFillColor(colors.HexColor('#34495E'))
    info_str = f"Габариты: {w} m x {l} m | Площадь: {w*l:.1f} m2 | Форма: {shape}"
    p.drawString(40, 515, safe_str(info_str))
    
    p.setStrokeColor(colors.HexColor('#BDC3C7'))
    p.setLineWidth(1)
    p.line(40, 500, 800, 500)
    
    # 3. Список комнат
    rooms = layout.get("rooms", {})
    y = 470
    
    p.setFont(font_name, 12)
    p.drawString(40, y, safe_str("Экспликация помещений:"))
    y -= 25
    
    p.setFont(font_regular, 10)
    
    if isinstance(rooms, dict) and rooms:
        for name, data in rooms.items():
            bounds = data.get("bounds", [0, 0, 1, 1])
            area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
            floor_raw = data.get("floor_type", "wood")
            
            floor_name = "Плитка" if floor_raw == "tile" else "Дерево/Ламинат"
            line = f"* {name}: {area:.2f} m2 (Покрытие: {floor_name})"
            
            p.drawString(50, y, safe_str(line))
            y -= 20
            
            if y < 60:
                p.showPage()
                y = 540
                p.setFont(font_regular, 10)

    # 4. Подвал
    p.setFont(font_regular, 8)
    p.setFillColor(colors.HexColor('#95A5A6'))
    p.drawString(40, 30, safe_str("Сгенерировано в BIM ARCHITECT V2.0"))

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()