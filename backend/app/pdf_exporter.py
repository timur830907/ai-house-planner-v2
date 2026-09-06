import io
import ezdxf

def generate_dxf_file(width: float, length: float, layout_data: dict) -> bytes:
    """
    Генерирует чертеж DXF с контурами стен и названиями комнат.
    """
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Добавляем слои
    doc.layers.add(name="OUTLINE", color=1)  # Красный
    doc.layers.add(name="ROOMS", color=3)    # Зеленый
    doc.layers.add(name="TEXT", color=7)     # Белый/Черный

    # Внешний контур здания
    msp.add_lwpolyline([(0, 0), (width, 0), (width, length), (0, length)], close=True, dxfattribs={'layer': 'OUTLINE'})

    # Перегородки и надписи
    rooms = layout_data.get("rooms", {})
    for room_name, data in rooms.items():
        bounds = data.get("bounds") if isinstance(data, dict) else data
        x1, y1, x2, y2 = bounds
        
        # Контур комнаты
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        msp.add_lwpolyline(points, close=True, dxfattribs={'layer': 'ROOMS'})
        
        # Название в центре комнаты
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        msp.add_text(room_name, dxfattribs={'layer': 'TEXT', 'height': 0.3}).set_placement((cx, cy), align=ezdxf.enums.TextEntityAlignment.CENTER)

    out_stream = io.StringIO()
    doc.write(out_stream)
    return out_stream.getvalue().encode('utf-8')