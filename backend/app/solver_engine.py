import random
import math

def solve_layout(width: float, length: float, rooms_req: dict = None, shape_type: str = "rectangle"):
    w = float(width)
    l = float(length)

    ext_wall = 0.38
    int_wall = 0.15

    # Вариативность перегородок
    split_x = round(w * random.uniform(0.35, 0.65), 2)
    split_y = round(l * random.uniform(0.35, 0.65), 2)

    rooms = {
        "Гостиная": {
            "bounds": [ext_wall, ext_wall, split_x - int_wall/2, split_y - int_wall/2],
            "type": "living_room",
            "floor_type": "wood"
        },
        "Спальня": {
            "bounds": [split_x + int_wall/2, ext_wall, w - ext_wall, split_y - int_wall/2],
            "type": "bedroom",
            "floor_type": "wood"
        },
        "Кухня": {
            "bounds": [ext_wall, split_y + int_wall/2, split_x - int_wall/2, l - ext_wall],
            "type": "kitchen",
            "floor_type": "tile"
        },
        "Санузел": {
            "bounds": [split_x + int_wall/2, split_y + int_wall/2, w - ext_wall, l - ext_wall],
            "type": "bathroom",
            "floor_type": "tile"
        }
    }

    # Позиционирование базовой мебели
    furniture = [
        {"type": "sofa", "pos": [ext_wall + 1.2, ext_wall + 1.0], "size": [2.2, 0.9, 0.85], "color": 0x2c3e50},
        {"type": "tv_stand", "pos": [split_x - 0.8, ext_wall + 1.0], "size": [1.6, 0.45, 0.5], "color": 0x34495e},
        {"type": "bed", "pos": [w - ext_wall - 1.1, ext_wall + 1.2], "size": [1.8, 2.0, 0.6], "color": 0x7f8c8d},
        {"type": "kitchen_counter", "pos": [ext_wall + 1.5, l - ext_wall - 0.4], "size": [2.4, 0.6, 0.9], "color": 0xbdc3c7},
        {"type": "bathtub", "pos": [w - ext_wall - 0.8, l - ext_wall - 0.9], "size": [1.6, 0.75, 0.55], "color": 0xecf0f1}
    ]

    return {
        "dimensions": {"width": w, "length": l, "height": 2.8},
        "wall_thickness": {"external": ext_wall, "internal": int_wall},
        "shape": shape_type,
        "rooms": rooms,
        "furniture": furniture
    }