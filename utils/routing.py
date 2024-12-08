import networkx as nx
import numpy as np

def validate_positions(graph, terminals):
    """
    Verifica que todos los nodos tengan una posición ('pos') definida.

    Args:
        graph (nx.Graph): Grafo donde verificar los nodos.
        terminals (list): Lista de nodos que deben tener posición.

    Raises:
        ValueError: Si algún nodo no tiene definida una posición.
    """
    for node in terminals:
        if 'pos' not in graph.nodes[node]:
            raise ValueError(f"El nodo {node} no tiene definida una posición ('pos').")


def diagnose_cluster(graph, cluster_id):
    """
    Diagnostica los nodos en un clúster específico.

    Args:
        graph (nx.Graph): Grafo que contiene los nodos y atributos.
        cluster_id (int): ID del clúster que se desea verificar.
    """
    print(f"Diagnóstico para el clúster {cluster_id}:")
    cluster_nodes = [node for node, attr in graph.nodes(data=True) if attr.get('cluster') == cluster_id]
    if not cluster_nodes:
        print(f"No se encontraron nodos asociados al clúster {cluster_id}.")
        return
    
    for node in cluster_nodes:
        node_type = graph.nodes[node].get('type', 'Desconocido')
        node_pos = graph.nodes[node].get('pos', 'Sin posición')
        print(f"Nodo {node} - Tipo: {node_type}, Posición: {node_pos}")

def connect_splitters_to_olt_with_steiner(graph, splitters, config):
    """
    Conecta los splitters a la OLT utilizando un Árbol de Steiner subóptimo.

    Args:
        graph (nx.Graph): Grafo inicial con nodos y aristas.
        splitters (list): Lista de nodos etiquetados como splitters.
        config (Config): Configuración del proyecto.

    Returns:
        nx.Graph: Árbol de Steiner subóptimo que incluye todos los nodos y aristas del grafo original.
    """
    # Seleccionar la OLT con mayor centralidad de proximidad
    olts = [node for node, attr in graph.nodes(data=True) if attr.get('type') == 'OLT']
    if not olts:
        raise ValueError("No se encontró ninguna OLT en el grafo.")
    
    centrality = nx.closeness_centrality(graph)
    olt = max(olts, key=lambda node: centrality[node])  # OLT con mayor centralidad

    print(f"OLT seleccionada: {olt} (Centralidad: {centrality[olt]:.4f})")

    # Definir los terminales (splitters + OLT seleccionada)
    terminals = [olt] + splitters
    print(f"Terminales identificados: {terminals}")

    # Validar que todos los nodos relevantes tienen posiciones
    validate_positions(graph, terminals)

    # Crear un grafo que copia todos los nodos y aristas originales
    steiner_graph = nx.Graph()
    for node, attr in graph.nodes(data=True):
        steiner_graph.add_node(node, **attr)
    for u, v, attr in graph.edges(data=True):
        steiner_graph.add_edge(u, v, **attr)

    # Inicializar conjunto de terminales conectados
    connected_terminals = set()
    connected_terminals.add(olt)  # Comienza desde la OLT seleccionada
    steiner_edges = set()

    # Construir el Árbol de Steiner
    while len(connected_terminals) < len(terminals):
        found_any_path = False
        for src in connected_terminals.copy():
            for dest in terminals:
                if dest not in connected_terminals:
                    # Verificar si hay un camino entre src y dest
                    if nx.has_path(graph, src, dest):
                        path = nx.shortest_path(graph, source=src, target=dest, weight='weight')
                        print(f"Conectando camino: {path}")
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i + 1]
                            steiner_edges.add((u, v))  # Agregar al Árbol de Steiner
                        connected_terminals.update(path)  # Agregar nodos conectados
                        found_any_path = True

        if not found_any_path:
            print("No se encontraron más caminos válidos. Verifique el grafo original.")
            break

    # Destacar las aristas relevantes en el grafo final
    for u, v in steiner_edges:
        if steiner_graph.has_edge(u, v):
            steiner_graph[u][v]['steiner'] = True

    # Validar que todos los terminales están conectados
    for terminal in terminals:
        if terminal not in steiner_graph.nodes:
            print(f"Advertencia: El terminal {terminal} no está presente en el Árbol de Steiner.")
        elif not nx.has_path(steiner_graph, terminal, olt):
            print(f"Advertencia: No hay ruta válida desde el terminal {terminal} hacia la OLT en el Árbol de Steiner.")

    return steiner_graph



def connect_splitters_to_olt(graph, splitters, config):
    """
    Conecta los splitters a la OLT utilizando un Árbol de Mínima Expansión (MST),
    comenzando desde la OLT y asegurando que todos los splitters estén conectados.
    Se usan distancias euclidianas.

    Args:
        graph (nx.Graph): Grafo inicial con nodos y aristas.
        splitters (list): Lista de nodos etiquetados como splitters.
        config (Config): Configuración del proyecto.

    Returns:
        nx.Graph: Subgrafo con conexiones entre splitters y la OLT.
    """
    # Crear un grafo vacío para las conexiones entre splitters y la OLT
    splitter_olt_graph = nx.Graph()

    # Obtener la OLT (nodo con mayor centralidad)
    olt_node = [node for node, attr in graph.nodes(data=True) if attr.get('type') == 'OLT'][0]
    olt_pos = graph.nodes[olt_node]['pos']  # Obtener la posición de la OLT

    # Añadir los splitters y la OLT al grafo reducido
    for splitter in splitters:
        splitter_olt_graph.add_node(splitter, pos=graph.nodes[splitter]['pos'], type='splitter')
    splitter_olt_graph.add_node(olt_node, pos=olt_pos, type='OLT')

    # Calcular distancias euclidianas y añadir aristas
    nodes = splitters + [olt_node]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            pos_i = graph.nodes[nodes[i]]['pos']
            pos_j = graph.nodes[nodes[j]]['pos']
            distance = np.linalg.norm(np.array(pos_i) - np.array(pos_j))
            splitter_olt_graph.add_edge(nodes[i], nodes[j], weight=distance)

    # Resolver el MST comenzando desde la OLT
    mst = nx.minimum_spanning_tree(splitter_olt_graph, weight='weight')

    # Asegurar que todos los nodos estén conectados al MST
    mst_nodes = set(mst.nodes)
    for splitter in splitters:
        if splitter not in mst_nodes:
            print(f"Advertencia: El splitter {splitter} no está conectado. Conectando manualmente al MST.")
            closest_node = min(
                mst.nodes, 
                key=lambda node: np.linalg.norm(
                    np.array(graph.nodes[splitter]['pos']) - np.array(graph.nodes[node]['pos'])
                )
            )
            distance = np.linalg.norm(
                np.array(graph.nodes[splitter]['pos']) - np.array(graph.nodes[closest_node]['pos'])
            )
            mst.add_edge(splitter, closest_node, weight=distance)

    return mst



def connect_users_to_splitters(graph, clusters, config):
    """
    Conecta los usuarios a los splitters utilizando rutas óptimas dentro del grafo original,
    respetando restricciones de distancia y capacidad.

    Args:
        graph (nx.Graph): Grafo original con nodos y aristas.
        clusters (dict): Diccionario que asigna usuarios a splitters.
        config (Config): Configuración del proyecto.

    Returns:
        nx.Graph: Grafo con las conexiones entre usuarios y splitters.
    """
    user_splitter_graph = nx.Graph()

    # Copiar nodos al nuevo grafo
    for node, attr in graph.nodes(data=True):
        user_splitter_graph.add_node(node, **attr)

    # Diagnóstico inicial de nodos y atributos
    print("Diagnóstico inicial de nodos:")
    for node, attr in graph.nodes(data=True):
        print(f"Nodo {node} - Tipo: {attr.get('type', 'Desconocido')}, Clúster: {attr.get('cluster', 'Sin clúster')}")

    # Conectar cada usuario a su splitter asignado
    for cluster_id, user_indices in clusters.items():
        print(f"Procesando clúster {cluster_id}...")

        # Buscar splitters válidos en el clúster
        splitter = [node for node, attr in graph.nodes(data=True) 
                    if attr.get('type') == 'splitter' and attr.get('cluster') == cluster_id]

        if not splitter:
            print(f"Advertencia: No se encontró un splitter válido para el clúster {cluster_id}.")
            continue

        splitter = splitter[0]  # Solo debe haber un splitter por clúster
        print(f"Splitter encontrado para el clúster {cluster_id}: {splitter}")

        # Conectar usuarios al splitter
        for user in user_indices:
            if nx.has_path(graph, user, splitter):
                path = nx.shortest_path(graph, source=user, target=splitter, weight='weight')
                print(f"Conectando usuario {user} al splitter {splitter} con camino: {path}")
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    user_splitter_graph.add_edge(u, v, **graph[u][v])
            else:
                print(f"No hay ruta válida entre el usuario {user} y el splitter {splitter}.")

    return user_splitter_graph