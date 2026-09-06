import random
import math
from typing import Dict, Any

RUSSIAN_ROOM_TEMPLATES = {
    1: ["Жилая комната / Студия", "Кухня-ниша", "Совмещенный с/у", "Прихожая"],
    2: ["Гостиная", "Спальня", "Кухня", "Санузел", "Прихожая"],
    3: ["Гостиная", "Спальня 1", "Спальня 2", "Кухня", "Санузел", "Холл"],
    4: ["Гостиная", "Главная спальня", "Спальня 2", "Детская", "Кухня-Столовая", "Санузел 1", "Санузел 2"],
    5: ["Гостиная", "Мастер-спальня", "Спальня 2", "Детская", "Кабинет", "Кухня", "Столовая", "Санузел 1", "Санузел 2"],
    6: ["Гостиная", "Мастер-спальня", "Спальня 2", "Детская 1", "Детская 2", "Кабинет", "Кухня", "Столовая", "Санузел 1", "Санузел 2"],
    7: ["Гостиная", "Мастер-спальня", "Спальня 2", "Спальня 3", "Детская 1", "Детская 2", "Кабинет", "Кухня", "Столовая", "Санузел 1", "Санузел 2"],
    8: ["Гостиная", "Мастер-спальня", "Спальня 2", "Спальня 3", "Гостевая спальня", "Детская 1", "Детская 2", "Кабинет", "Кухня", "Столовая", "Спортзал"],
    9: ["Гостиная", "Мастер-спальня", "Спальня 2", "Спальня 3", "Гостевая спальня", "Детская 1", "Детская 2", "Кабинет", "Игровая", "Кухня", "Столовая", "SPA-зона"],
    10: ["Гостиная", "Мастер-спальня", "Спальня 2", "Спальня 3", "Гостевая 1", "Гостевая 2", "Детская 1", "Детская 2", "Кабинет", "Библиотека", "Кухня", "Столовая", "Кинотеатр"]
}

def generate_house_layout(width: float, length: float, num_rooms: int = 3, shape: str = "rectangle", seed: int = 0) -> Dict[str, Any]:
    random.seed(seed)
    
    target_count = max(1, min(10, num_rooms))
    room_names = RUSSIAN_ROOM_TEMPLATES.get(target_count, RUSSIAN_ROOM_TEMPLATES[3])
    
    rooms = {}
    
    # Генерация контуров комнат с учетом формы внешней геометрии
    if shape.lower() in ["circle", "круг"]:
        # Сегментированная планировка для круглого дома (сектора/кольца)
        radius = min(width, length) / 2.0
        angle_step = (2 * math.pi) / len(room_names)
        
        for idx, name in enumerate(room_names):
            a1 = idx * angle_step
            a2 = (idx + 1) * angle_step
            # Аппроксимация прямоугольными границами для 3D трехмерного рендеринга
            x1 = round(radius + (radius * 0.2) * math.cos(a1), 2)
            y1 = round(radius + (radius * 0.2) * math.sin(a1), 2)
            x2 = round(radius + radius * math.cos(a2), 2)
            y2 = round(radius + radius * math.sin(a2), 2)
            
            floor_type = "tile" if any(w in name for w in ["Санузел", "с/у", "Кухня", "SPA"]) else "wood"
            rooms[name] = {
                "bounds": [min(x1, x2), min(y1, y2), max(x1, x2) + 2.0, max(y1, y2) + 2.0],
                "floor_type": floor_type
            }
            
    elif shape.lower() in ["diamond", "ромб"]:
        # Диагональная планировка
        cx, cy = width / 2.0, length / 2.0
        step_x = width / (len(room_names) + 1)
        step_y = length / (len(room_names) + 1)
        
        for idx, name in enumerate(room_names):
            x1 = round(step_x * idx, 2)
            y1 = round(cy - (step_y * (idx + 1) / 2), 2)
            x2 = round(x1 + step_x * 1.2, 2)
            y2 = round(y1 + step_y * 1.5, 2)
            
            floor_type = "tile" if any(w in name for w in ["Санузел", "с/у", "Кухня", "SPA"]) else "wood"
            rooms[name] = {"bounds": [x1, y1, x2, y2], "floor_type": floor_type}
            
    else:
        # Стандартная/Г-образная динамическая сетка
        split_x = round(width * random.uniform(0.40, 0.60), 2)
        split_y = round(length * random.uniform(0.40, 0.60), 2)
        
        total_r = len(room_names)
        for idx, name in enumerate(room_names):
            if idx == 0:
                bounds = [0.0, 0.0, split_x, split_y]
            elif idx == 1:
                bounds = [split_x, 0.0, width, split_y]
            elif idx == 2:
                bounds = [0.0, split_y, split_x, length]
            else:
                step = (width - split_x) / max(1, (total_r - 3))
                offset = (idx - 3) * step
                bounds = [
                    round(split_x + offset, 2), 
                    split_y, 
                    round(min(width, split_x + offset + step), 2), 
                    length
                ]
            floor_type = "tile" if any(w in name for w in ["Санузел", "с/у", "Кухня", "SPA"]) else "wood"
            rooms[name] = {"bounds": bounds, "floor_type": floor_type}

    return {
        "dimensions": {"width": width, "length": length, "height": 2.8},
        "shape": shape,
        "room_count": len(room_names),
        "rooms": rooms
    }
def add_mep_routes(rooms: dict, width: float, length: float) -> dict:
    routes = {"pipes": [], "cables": []}
    
    # Вводная точка (щиток / стояк)
    main_hub = [0.5, 0.5, 0.0] 
    
    for r_name, r_data in rooms.items():
        b = r_data["bounds"]
        center = [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2, 0.1]
        
        # Трубы идут к санузлам и кухне
        if any(w in r_name for w in ["Санузел", "Кухня", "SPA", "с/у"]):
            routes["pipes"].append({"from": main_hub, "to": center, "type": "water"})
            
        # Кабели идут во все помещения
        routes["cables"].append({"from": main_hub, "to": center, "type": "power"})
        
    return routes