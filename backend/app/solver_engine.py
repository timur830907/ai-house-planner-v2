import random
import math

def solve_layout(width: float, length: float, rooms_req: dict = None, shape_type: str = "rectangle") -> dict:
    w = float(width)
    l = float(length)

    ext_wall = 0.38
    int_wall = 0.15

    # Приводим тип формы к нижнему регистру
    shape_clean = str(shape_type).lower().strip()
    
    # Маппинг кириллических значений из UI в системные ключи
    shape_map = {
        "г-образный": "l_shape",
        "l-образный": "l_shape",
        "т-образный": "t_shape",
        "эллипс": "ellipse",
        "круг": "circle",
        "прямоугольник": "rectangle"
    }
    actual_shape = shape_map.get(shape_clean, shape_clean)

    # 1. Генерация рандомных сдвигов перегородок для вариативности (30 вариантов)
    # Используем диапазоны, чтобы комнаты сохраняли пропорциональность
    split_x = round(w * random.uniform(0.48, 0.62), 2)
    split_y = round(l * random.uniform(0.40, 0.52), 2)
    
    # Сдвиг для Прихожей/Холла
    corridor_split = round(split_x * random.uniform(0.40, 0.50), 2)
    
    # Ширина блока санузлов
    bathroom_w = round(random.uniform(1.8, 2.3), 2)
    toilet_h = round(random.uniform(1.2, 1.5), 2)

    # 2. Адаптация габаритов под форму здания
    usable_w = w - ext_wall * 2
    usable_l = l - ext_wall * 2

    if actual_shape == "l_shape":
        # Урезаем правую верхнюю часть дома под L-образный контур
        split_x = min(split_x, round(w * 0.5, 2))
    elif actual_shape == "t_shape":
        # Адаптация под Т-образную форму
        split_x = round(w * 0.5, 2)

    # 3. Распределение комнат с учетом динамических осей
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
            "bounds": [ext_wall, split_y + int_wall/2, corridor_split, l - ext_wall],
            "type": "hallway",
            "floor_type": "tile",
            "doors": [{"wall": "east", "pos": 0.5, "width": 0.9}]
        },
        "Холл": {
            "bounds": [corridor_split + int_wall/2, split_y + int_wall/2, split_x - int_wall/2, l - ext_wall],
            "type": "corridor",
            "floor_type": "wood",
            "doors": [{"wall": "south", "pos": 0.5, "width": 0.9}]
        },
        "Спальня": {
            "bounds": [split_x + int_wall/2, split_y + int_wall/2, w - ext_wall - bathroom_w, l - ext_wall],
            "type": "bedroom",
            "floor_type": "wood",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.8}]
        },
        # Компактный санузел: Ванная и Туалет
        "Туалет": {
            "bounds": [w - ext_wall - bathroom_w + int_wall/2, split_y + int_wall/2, w - ext_wall, split_y + int_wall/2 + toilet_h],
            "type": "toilet",
            "floor_type": "tile",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.7}]
        },
        "Ванная": {
            "bounds": [w - ext_wall - bathroom_w + int_wall/2, split_y + int_wall/2 + toilet_h + int_wall/2, w - ext_wall, l - ext_wall],
            "type": "bathroom",
            "floor_type": "tile",
            "doors": [{"wall": "west", "pos": 0.5, "width": 0.7}]
        }
    }

    # 4. Динамическая расстановка мебели (автоматически встает по габаритам комнат)
    hall_bounds = rooms["Зал"]["bounds"]
    bed_bounds = rooms["Спальня"]["bounds"]
    kit_bounds = rooms["Кухня"]["bounds"]
    bath_bounds = rooms["Ванная"]["bounds"]
    toilet_bounds = rooms["Туалет"]["bounds"]

    furniture = [
        # Диван в Зале
        {
            "type": "sofa",
            "pos": [round(hall_bounds[0] + 1.2, 2), round(hall_bounds[1] + 1.0, 2)],
            "size": [2.2, 0.9, 0.85],
            "color": 0x2c3e50
        },
        # Кровать в Спальне
        {
            "type": "bed",
            "pos": [round(bed_bounds[0] + 1.2, 2), round(bed_bounds[1] + 1.2, 2)],
            "size": [1.8, 2.0, 0.6],
            "color": 0x7f8c8d
        },
        # Кухонный гарнитур в Кухне
        {
            "type": "kitchen_counter",
            "pos": [round(kit_bounds[0] + 0.4, 2), round(kit_bounds[1] + 0.4, 2)],
            "size": [2.2, 0.6, 0.9],
            "color": 0xbdc3c7
        },
        # Ванна в Ванной
        {
            "type": "bathtub",
            "pos": [round(bath_bounds[2] - 0.8, 2), round(bath_bounds[3] - 0.5, 2)],
            "size": [1.4, 0.7, 0.55],
            "color": 0xecf0f1
        },
        # Унитаз в Туалете
        {
            "type": "toilet_bowl",
            "pos": [round(toilet_bounds[2] - 0.5, 2), round(toilet_bounds[1] + 0.5, 2)],
            "size": [0.5, 0.6, 0.4],
            "color": 0xffffff
        }
    ]

    return {
        "dimensions": {"width": w, "length": l, "height": 2.8},
        "wall_thickness": {"external": ext_wall, "internal": int_wall},
        "shape": actual_shape,
        "rooms": rooms,
        "furniture": furniture
    }