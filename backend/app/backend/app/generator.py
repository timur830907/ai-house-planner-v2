import random
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
    
    # Смешанное динамическое деление (не одинаковыми сетками)
    split_x = round(width * random.uniform(0.45, 0.60), 2)
    split_y = round(length * random.uniform(0.40, 0.55), 2)
    
    rooms = {}
    total_r = len(room_names)
    
    # Зонирование
    for idx, name in enumerate(room_names):
        if idx == 0:  # Гостиная
            bounds = [0.0, 0.0, split_x, split_y]
        elif idx == 1:  # Спальня / Кухня
            bounds = [split_x, 0.0, width, split_y]
        elif idx == 2:
            bounds = [0.0, split_y, split_x, length]
        else:
            # Для остальных комнат делим оставшиеся блоки
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
        "room_count": target_count,
        "rooms": rooms
    }