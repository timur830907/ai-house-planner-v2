import ezdxf

def export_to_dxf(layout: dict, file_path: str = "generated_house_plan.dxf"):
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Создаем слои
    doc.layers.add(name="WALLS", color=7)
    doc.layers.add(name="ROOM_LABELS", color=3)

    for room_name, room_info in layout.items():
        x1, y1, x2, y2 = room_info["bounds"]
        
        # Отрисовка контура комнаты (контур стен)
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "WALLS"})

        # Вычисление центра комнаты для подписи
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Подпись названия комнаты и площади
        text_content = f"{room_name} ({room_info['area']}m2)"
        msp.add_text(
            text_content,
            dxfattribs={"layer": "ROOM_LABELS", "height": 0.35}
        ).set_placement((center_x, center_y), align=ezdxf.enums.TextEntityAlignment.CENTER)

    doc.saveas(file_path)
    return file_path