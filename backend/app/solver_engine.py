import random
import math

def solve_layout(width: float, length: float, rooms_req: dict = None, shape_type: str = "rectangle"):
    w = float(width)
    l = float(length)

    ext_wall = 0.38
    int_wall = 0.15

    # Координаты основных осей
    split_x = round(w * 0.55, 2)
    split_y = round(l * 0.45, 2)
    
    # Распределение комнат:
    # Ванная и Туалет проектируются маленькими (компактными)
    rooms = {
        "Зал": {
            "bounds": [ext_wall, ext_wall, split_x - int_wall/2, split_y - int_wall/2],
            "type": "living_room",
            "floor_type": "wood",
            "doors": [{"wall": "north", "pos": 0.5, "width": 0.9}]
        },
        "Кухня": {
            "bounds": [split_x + int_wall/2, ext_wall, w - ext_wall, split_y - int_wall/2],
            "type": "kitchen",
            "floor_type": "tile",
            "doors": [{"wall": "north", "pos": 0.5, "width": 0.9}]
        },
        "Прихожая": {
            "bounds": [ext_wall, split_y + int_wall/2, ext_wall + (split_x - ext_wall) * 0.45, l - ext_wall],
            "type": "hallway",
            "floor_type": "tile",
            "doors": [{"wall": "east", "pos": 0.5, "width": 0.9}]
        },
        "Холл": {
            "bounds": [ext_wall + (split_x - ext_wall) * 0.45 + int_wall/2, split_y + int_wall/2, split_x - int_wall/2, l - ext_wall],
            "type": "corridor",
            "floor_type": "wood",
            "doors": [{"wall": "south", "pos": 0.5, "width": 0.9}]
        },
        "Спальня": {
            "bounds": [split_x + int_wall/2, split_y + int_wall/2, w - ext_wall - 2.2, l - ext_wall],
            "type": "bedroom",
            "floor_type": "wood",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.8}]
        },
        # Маленькие санузлы
        "Ванная": {
            "bounds": [w - ext_wall - 2.2 + int_wall/2, split_y + int_wall/2 + 1.6, w - ext_wall, l - ext_wall],
            "type": "bathroom",
            "floor_type": "tile",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.7}]
        },
        "Туалет": {
            "bounds": [w - ext_wall - 2.2 + int_wall/2, split_y + int_wall/2, w - ext_wall, split_y + int_wall/2 + 1.4],
            "type": "toilet",
            "floor_type": "tile",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.7}]
        }
    }

    # Позиционирование базовой мебели без ТВ
    furniture = [
        {"type": "sofa", "pos": [ext_wall + 1.2, ext_wall + 1.0], "size": [2.2, 0.9, 0.85], "color": 0x2c3e50},
        {"type": "bed", "pos": [split_x + 1.2, split_y + 1.5], "size": [1.8, 2.0, 0.6], "color": 0x7f8c8d},
        {"type": "kitchen_counter", "pos": [split_x + 1.0, ext_wall + 0.4], "size": [2.2, 0.6, 0.9], "color": 0xbdc3c7},
        {"type": "bathtub", "pos": [w - ext_wall - 0.7, l - ext_wall - 0.6], "size": [1.4, 0.7, 0.55], "color": 0xecf0f1},
        {"type": "toilet_bowl", "pos": [w - ext_wall - 0.5, split_y + int_wall/2 + 0.5], "size": [0.5, 0.6, 0.4], "color": 0xffffff}
    ]

    return {
        "dimensions": {"width": w, "length": l, "height": 2.8},
        "wall_thickness": {"external": ext_wall, "internal": int_wall},
        "shape": shape_type,
        "rooms": rooms,
        "furniture": furniture
    }