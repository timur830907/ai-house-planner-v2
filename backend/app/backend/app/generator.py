import random
from typing import Dict, Any

# Названия комнат на русском языке (от 1 до 10 комнат)
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
    
    target_room_count = max(1, min(10, num_rooms))
    room_names = RUSSIAN_ROOM_TEMPLATES.get(target_room_count, RUSSIAN_ROOM_TEMPLATES[3])
    
    grid_cols = 2 if target_room_count <= 4 else (3 if target_room_count <= 7 else 4)
    grid_rows = (len(room_names) + grid_cols - 1) // grid_cols
    
    col_width = width / grid_cols
    row_length = length / grid_rows
    
    rooms = {}
    furniture = []
    
    for idx, r_name in enumerate(room_names):
        c = idx % grid_cols
        r = idx // grid_cols
        
        x1 = round(c * col_width, 2)
        y1 = round(r * row_length, 2)
        x2 = round((c + 1) * col_width, 2)
        y2 = round((r + 1) * row_length, 2)
        
        floor_type = "tile" if any(w in r_name for w in ["Санузел", "с/у", "Кухня", "SPA", "Прачечная"]) else "wood"
        
        rooms[r_name] = {
            "bounds": [x1, y1, x2, y2],
            "floor_type": floor_type
        }
        
        cx = round((x1 + x2) / 2, 2)
        cy = round((y1 + y2) / 2, 2)
        furniture.append({
            "name": f"Мебель ({r_name})",
            "pos": [cx, cy],
            "size": [1.2, 1.2, 0.8],
            "color": 0x34495e if floor_type == "wood" else 0x2980b9
        })

    return {
        "dimensions": {"width": width, "length": length, "height": 2.8},
        "shape": shape,
        "room_count": target_room_count,
        "rooms": rooms,
        "furniture": furniture
    }