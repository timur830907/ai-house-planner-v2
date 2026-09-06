import networkx as nx

def build_room_graph(rooms_data):
    G = nx.Graph()
    
    for room in rooms_data:
        G.add_node(room['name'], min_area=room['min_area'])
    
    for room in rooms_data:
        room_name = room['name']
        for adjacent in room.get('preferred_adjacent', []):
            if G.has_node(adjacent):
                G.add_edge(room_name, adjacent)
                
    return G