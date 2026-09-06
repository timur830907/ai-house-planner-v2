import networkx as nx

ROOM_MIN_AREAS = {
    "Гостиная": 20.0,
    "Кухня": 12.0,
    "Прихожая": 8.0,
    "Ванная": 6.0,
    "Спальня 1": 14.0,
    "Спальня 2": 12.0,
    "Кабинет": 10.0,
    "Гардероб": 5.0,
}

def build_graph_from_rooms(rooms: list) -> nx.Graph:
    """Создает граф NetworkX со свойствами минимальной площади для каждой комнаты."""
    graph = nx.Graph()
    
    for room in rooms:
        min_area = ROOM_MIN_AREAS.get(room, 10.0)
        graph.add_node(room, min_area=min_area)
        
    if "Прихожая" in rooms and "Гостиная" in rooms:
        graph.add_edge("Прихожая", "Гостиная")
    if "Гостиная" in rooms and "Кухня" in rooms:
        graph.add_edge("Гостиная", "Кухня")
        
    return graph