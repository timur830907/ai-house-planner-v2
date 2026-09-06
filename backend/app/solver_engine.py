import random

def solve_layout(width: float, length: float, rooms_req: dict = None, shape_type: str = "rectangle"):
    """
    Генерирует процедурную планировку дома с мебелью и поддержкой сложной геометрии.
    """
    w = float(width)
    l = float(length)

    # Вариативность перегородок (случайное смещение крестовины от 35% до 65%)
    split_x = w * random.uniform(0.35, 0.65)
    split_y = l * random.uniform(0.35, 0.65)

    # Основная сетка комнат
    rooms = {
        "Гостиная": {"bounds": [0.0, 0.0, split_x, split_y], "type": "living_room"},
        "Спальня": {"bounds": [split_x, 0.0, w, split_y], "type": "bedroom"},
        "Кухня": {"bounds": [0.0, split_y, split_x, l], "type": "kitchen"},
        "Санузел": {"bounds": [split_x, split_y, w, l], "type": "bathroom"}
    }

    # Если выбрана срезанная / Г-образная форма
    if shape_type in ["L_shape", "triangle_cut"]:
        rooms["Терраса / Вырез"] = {"bounds": [split_x, split_y, w, l], "type": "void"}
        rooms["Санузел"]["bounds"] = [split_x * 0.5, split_y, split_x, l]

    # Генерация процедурной мебели для каждой комнаты
    furniture = []
    for r_name, r_data in rooms.items():
        if r_data.get("type") == "void":
            continue
        x1, y1, x2, y2 = r_data["bounds"]
        rw = x2 - x1
        rl = y2 - y1
        cx, cy = x1 + rw / 2.0, y1 + rl / 2.0

        if r_data["type"] == "bedroom":
            # Кровать (1.6m x 2.0m)
            furniture.append({"type": "bed", "pos": [cx, cy], "size": [1.6, 2.0], "color": 0x8e44ad})
        elif r_data["type"] == "living_room":
            # Диван (2.2m x 0.9m) + стол (1.0m x 0.6m)
            furniture.append({"type": "sofa", "pos": [x1 + rw * 0.4, y1 + rl * 0.3], "size": [2.2, 0.9], "color": 0xe67e22})
            furniture.append({"type": "table", "pos": [x1 + rw * 0.4, y1 + rl * 0.6], "size": [1.2, 0.7], "color": 0xd35400})
        elif r_data["type"] == "kitchen":
            # Стол со стульями
            furniture.append({"type": "dining", "pos": [cx, cy], "size": [1.4, 0.9], "color": 0x16a085})
        elif r_data["type"] == "bathroom":
            # Ванна (1.7m x 0.7m)
            furniture.append({"type": "bath", "pos": [x1 + 0.9, y1 + 0.5], "size": [1.7, 0.7], "color": 0x2980b9})

    return {
        "rooms": rooms,
        "furniture": furniture,
        "shape": shape_type
    }