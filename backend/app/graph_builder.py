import networkx as nx

def build_layout_graph(rooms_data: dict) -> nx.Graph:
    """
    Создает граф смежности помещений на основе их прямоугольных границ.
    """
    G = nx.Graph()
    rooms = rooms_data.get("rooms", {})

    for room_name, data in rooms.items():
        bounds = data.get("bounds") if isinstance(data, dict) else data
        G.add_node(room_name, bounds=bounds)

    room_names = list(rooms.keys())
    for i in range(len(room_names)):
        for j in range(i + 1, len(room_names)):
            r1_name = room_names[i]
            r2_name = room_names[j]
            
            b1 = rooms[r1_name].get("bounds") if isinstance(rooms[r1_name], dict) else rooms[r1_name]
            b2 = rooms[r2_name].get("bounds") if isinstance(rooms[r2_name], dict) else rooms[r2_name]

            if is_adjacent(b1, b2):
                G.add_edge(r1_name, r2_name)

    return G

def is_adjacent(b1: list, b2: list, tol: float = 0.01) -> bool:
    """
    Проверяет, соприкасаются ли два прямоугольника стенами.
    """
    x1_min, y1_min, x1_max, y1_max = b1
    x2_min, y2_min, x2_max, y2_max = b2

    # Проверка общего вертикального ребра
    touch_x = abs(x1_max - x2_min) < tol or abs(x2_max - x1_min) < tol
    overlap_y = max(0.0, min(y1_max, y2_max) - max(y1_min, y2_min)) > tol

    # Проверка общего горизонтального ребра
    touch_y = abs(y1_max - y2_min) < tol or abs(y2_max - y1_min) < tol
    overlap_x = max(0.0, min(x1_max, x2_max) - max(x1_min, x2_min)) > tol

    return (touch_x and overlap_y) or (touch_y and overlap_x)