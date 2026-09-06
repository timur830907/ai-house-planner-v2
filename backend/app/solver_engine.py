import random

def solve_layout(width: float, length: float, rooms_req: dict = None, shape_type: str = "rectangle"):
    w = float(width)
    l = float(length)

    # Внешние стены: 38 см, Внутренние: 15 см
    ext_wall = 0.38
    int_wall = 0.15

    # Пропорциональное деление пространств (BSP)
    split_x = round(w * random.uniform(0.42, 0.58), 2)
    split_y = round(l * random.uniform(0.42, 0.58), 2)

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

    # Проемы (Окна и Двери) [x, y, width, height_z, rotation_deg, type]
    openings = [
        # Входная дверь
        {"pos": [split_x, ext_wall / 2], "width": 1.0, "type": "door_ext"},
        # Внутренние двери
        {"pos": [split_x - 0.6, split_y - int_wall/2], "width": 0.9, "type": "door_int"},
        {"pos": [split_x + 0.6, split_y - int_wall/2], "width": 0.9, "type": "door_int"},
        # Окна
        {"pos": [split_x / 2, ext_wall / 2], "width": 1.4, "type": "window"},
        {"pos": [w - ext_wall / 2, split_y / 2], "width": 1.4, "type": "window"},
        {"pos": [split_x / 2, l - ext_wall / 2], "width": 1.2, "type": "window"}
    ]

    # Мебель с точной привязкой и параметрами
    furniture = [
        {"type": "sofa", "pos": [ext_wall + 1.2, ext_wall + 1.0], "size": [2.2, 0.9, 0.85], "color": 0x2c3e50, "rot": 0},
        {"type": "tv_stand", "pos": [split_x - 0.8, ext_wall + 1.0], "size": [1.6, 0.45, 0.5], "color": 0x34495e, "rot": 0},
        {"type": "bed", "pos": [w - ext_wall - 1.1, ext_wall + 1.2], "size": [1.8, 2.0, 0.6], "color": 0x7f8c8d, "rot": 0},
        {"type": "kitchen_counter", "pos": [ext_wall + 1.5, l - ext_wall - 0.4], "size": [2.4, 0.6, 0.9], "color": 0xbdc3c7, "rot": 0},
        {"type": "bathtub", "pos": [w - ext_wall - 0.8, l - ext_wall - 0.9], "size": [1.6, 0.75, 0.55], "color": 0xecf0f1, "rot": 0}
    ]

    return {
        "dimensions": {"width": w, "length": l, "height": 3.0},
        "wall_thickness": {"external": ext_wall, "internal": int_wall},
        "rooms": rooms,
        "openings": openings,
        "furniture": furniture
    }