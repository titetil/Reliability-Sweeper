from enum import Enum

class Graph_Type(Enum):
    H_vs_R = 0
    T_vs_R = 1
    Both = 2


def test(graph_type):
    graph_type = Graph_Type(graph_type)
    if graph_type == Graph_Type.Both:
        print(graph_type.name)

test(2)

