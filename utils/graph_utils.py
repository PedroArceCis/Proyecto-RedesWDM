import numpy as np
import networkx as nx
from scipy.spatial import Delaunay

def generate_graph(config):
    """
    Genera un grafo inicial basado en nodos aleatorios o manuales, y etiqueta el nodo central como OLT.

    Args:
        config (Config): Configuración del proyecto.

    Returns:
        graph (nx.Graph): Grafo generado con la OLT etiquetada.
        nodes (np.ndarray): Coordenadas de los nodos.
    """
    # Generar nodos
    if config.input_type == 'random':
        nodes = np.random.rand(config.num_nodes, 2) * config.area
    elif config.input_type == 'manual':
        nodes = np.array(config.manual_nodes)
    else:
        raise ValueError("Tipo de entrada inválido. Use 'random' o 'manual'.")

    # Crear el grafo
    graph = nx.Graph()
    for i, coord in enumerate(nodes):
        graph.add_node(i, pos=coord)

    # Conectar nodos usando triangulación de Delaunay
    tri = Delaunay(nodes)
    for simplex in tri.simplices:
        for i in range(3):
            graph.add_edge(
                simplex[i], simplex[(i + 1) % 3],
                weight=np.linalg.norm(nodes[simplex[i]] - nodes[simplex[(i + 1) % 3]])
            )

    # Calcular la centralidad de proximidad
    centrality = nx.closeness_centrality(graph)
    
    # Encontrar el nodo con mayor centralidad
    olt_index = max(centrality, key=centrality.get)

    # Etiquetar el nodo como OLT
    graph.nodes[olt_index]['type'] = 'OLT'
    print(f"Nodo {olt_index} etiquetado como OLT con centralidad {centrality[olt_index]:.4f}.")

    return graph, nodes
