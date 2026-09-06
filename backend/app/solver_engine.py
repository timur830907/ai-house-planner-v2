import random
import networkx as nx

def solve_layout_single(graph: nx.Graph, total_area: float, seed: int = 0) -> dict:
    """Генерация одного варианта планировки с точным масштабированием площадей."""
    random.seed(seed)
    
    nodes = list(graph.nodes(data=True))
    
    # 1. Считаем суммарный минимальный вес запрошенных комнат
    raw_total_min_area = sum(data.get('min_area', 10.0) for _, data in nodes)
    
    # 2. Полезная площадь (учитываем ~10% на стены/проходы)
    usable_area = total_area * 0.90
    
    # Коэффициент масштабирования комнат под общую площадь
    scale_factor = usable_area / raw_total_min_area if raw_total_min_area > 0 else 1.0

    # Разбиваем комнаты по сетке/рядам
    random.shuffle(nodes)
    layout = {}
    current_x = 0.0
    current_y = 0.0
    max_row_height = 0.0
    
    # Ограничение по ширине ряда (квадратный или слегка вытянутый контур дома)
    row_width_limit = round((total_area ** 0.5) * 1.05, 1)

    for name, data in nodes:
        # Пропорциональный пересчет площади комнаты
        base_min_area = data.get('min_area', 10.0)
        target_room_area = max(4.0, round(base_min_area * scale_factor, 1))
        
        # Пропорция сторон (aspect ratio)
        aspect = random.uniform(1.0, 1.35)
        width = round((target_room_area * aspect) ** 0.5, 1)
        height = round(target_room_area / width, 1)

        # Перенос на новый ряд, если не вмещается по ширине
        if current_x + width > row_width_limit and current_x > 0:
            current_x = 0.0
            current_y += max_row_height
            max_row_height = 0.0

        x1, y1 = current_x, current_y
        x2, y2 = round(x1 + width, 1), round(y1 + height, 1)

        doors = [
            {"center": [round(x1 + width / 2, 1), y1]},
            {"center": [x1, round(y1 + height / 2, 1)]}
        ]

        layout[name] = {
            "bounds": [x1, y1, x2, y2],
            "width": width,
            "height": height,
            "area": round(width * height, 1),
            "doors": doors
        }

        current_x = round(current_x + width, 1)
        if height > max_row_height:
            max_row_height = height

    return layout

def solve_layout_variants(graph: nx.Graph, total_area: float, num_variants: int = 10) -> list:
    """Генерация списка вариантов."""
    variants = []
    for i in range(num_variants):
        variant_layout = solve_layout_single(graph, total_area, seed=i * 100 + 13)
        variants.append({
            "variant_id": i + 1,
            "layout": variant_layout
        })
    return variants