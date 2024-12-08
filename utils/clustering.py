import numpy as np
from sklearn_extra.cluster import KMedoids

def perform_clustering(graph, nodes, config):
    """
    Realiza clustering iterativo con restricciones de distancia y capacidad,
    seleccionando nodos existentes como splitters.

    Args:
        graph (nx.Graph): Grafo inicial con nodos y aristas.
        nodes (np.ndarray): Coordenadas de los nodos.
        config (Config): Configuración del proyecto.

    Returns:
        clusters (dict): Diccionario donde las claves son IDs de clústeres y los valores son listas de nodos.
        splitters (list): Nodos seleccionados como splitters.
        graph (nx.Graph): Grafo actualizado con los splitters etiquetados.
    """
    num_clusters = config.num_clusters
    valid_clustering = False

    while not valid_clustering:
        # Aplicar K-Medoids para clusterizar y seleccionar nodos existentes como splitters
        kmedoids = KMedoids(n_clusters=num_clusters, random_state=42, method='pam')
        node_indices = [node for node in graph.nodes if graph.nodes[node].get('type') != 'OLT']
        coordinates = np.array([graph.nodes[node]['pos'] for node in node_indices])
        labels = kmedoids.fit_predict(coordinates)

        # Crear un diccionario para almacenar los clústeres
        clusters = {i: [] for i in range(num_clusters)}
        for idx, label in enumerate(labels):
            clusters[label].append(node_indices[idx])

        # Seleccionar nodos existentes como splitters
        splitters = [node_indices[medoid] for medoid in kmedoids.medoid_indices_]

        # Verificar restricciones
        valid_clustering = True
        for cluster_id, node_indices in clusters.items():
            splitter = splitters[cluster_id]
            splitter_pos = graph.nodes[splitter]['pos']

            # Validar distancia máxima
            for user_idx in node_indices:
                user_pos = graph.nodes[user_idx]['pos']
                distance = np.linalg.norm(np.array(user_pos) - np.array(splitter_pos))
                if distance > config.max_distance_splitters:
                    valid_clustering = False
                    print(f"Clúster {cluster_id}: Usuario {user_idx} excede la distancia máxima ({distance:.2f} m).")
                    break

            # Validar capacidad máxima
            if len(node_indices) > config.max_users_per_splitter:
                valid_clustering = False
                print(f"Clúster {cluster_id}: Excede la capacidad máxima de usuarios ({len(node_indices)}).")
                break

        # Si las restricciones no se cumplen, incrementar el número de clústeres
        if not valid_clustering:
            num_clusters += 1
            print(f"Aumentando el número de clústeres a {num_clusters}.")

    # Etiquetar los splitters en el grafo
    for splitter in splitters:
        graph.nodes[splitter]['type'] = 'splitter'

    return clusters, splitters, graph
