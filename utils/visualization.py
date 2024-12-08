import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def plot_graph(graph, nodes, title="Grafo Inicial con OLT"):
    """
    Visualiza el grafo inicial con nodos y aristas, destacando la OLT como un rectángulo.

    Args:
        graph (nx.Graph): Grafo generado.
        nodes (list): Lista de nodos con coordenadas.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')

    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_size=50, node_color="blue", edge_color="gray", with_labels=False)

    # Destacar la OLT
    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'OLT':  # Verificar si el nodo es la OLT
            olt_pos = attributes['pos']
            rect = plt.Rectangle((olt_pos[0] - 50, olt_pos[1] - 50), 100, 100, color='red', alpha=0.7, label='OLT')
            plt.gca().add_patch(rect)
            plt.text(olt_pos[0], olt_pos[1] + 70, 'OLT', color='red', fontsize=12, fontweight='bold', ha='center')

    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.show()


def plot_clusters(graph, nodes, clusters, splitters, title="Clustering de nodos"):
    """
    Visualiza los clústeres y las ubicaciones de los splitters, destacando la OLT como un rectángulo.

    Args:
        graph (nx.Graph): Grafo generado.
        nodes (list): Lista de nodos con coordenadas.
        clusters (dict): Clústeres generados.
        splitters (list): Lista de nodos etiquetados como splitters.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')

    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_size=30, alpha=0.6, with_labels=False, edge_color="gray")

    # Dibujar pesos de las aristas (redondeados)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    edge_labels = {key: round(value) for key, value in edge_labels.items()}  # Redondear pesos
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8, font_color="black")

    # Dibujar nodos de cada clúster
    colors = plt.cm.tab10.colors
    for cluster_id, node_indices in clusters.items():
        cluster_coords = np.array([graph.nodes[i]['pos'] for i in node_indices])  # Coordenadas del clúster
        if cluster_coords.size > 0:
            plt.scatter(cluster_coords[:, 0], cluster_coords[:, 1], label=f"Cluster {cluster_id}", color=colors[cluster_id % 10])

    # Dibujar splitters
    splitter_coords = np.array([graph.nodes[s]['pos'] for s in splitters])  # Coordenadas de los splitters
    plt.scatter(splitter_coords[:, 0], splitter_coords[:, 1], color='red', s=100, label='Splitters', edgecolor='black')

    # Destacar la OLT
    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'OLT':
            olt_pos = attributes['pos']
            rect = plt.Rectangle((olt_pos[0] - 50, olt_pos[1] - 50), 100, 100, color='red', alpha=0.7, label='OLT')
            plt.gca().add_patch(rect)
            plt.text(olt_pos[0], olt_pos[1] + 70, 'OLT', color='red', fontsize=12, fontweight='bold', ha='center')

    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()


def plot_user_splitter_connections(graph, title="Conexión de Usuarios a Splitters"):
    """
    Visualiza las conexiones entre usuarios y splitters.

    Args:
        graph (nx.Graph): Grafo con conexiones entre usuarios y splitters.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')
    plt.figure(figsize=(10, 8))
    nx.draw(graph, pos, node_size=70, node_color="blue", edge_color="orange", width=2, with_labels=False)

    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'splitter':
            plt.scatter(attributes['pos'][0], attributes['pos'][1], color='red', s=150, label='Splitter', edgecolor='black')
        elif attributes.get('type') == 'user':
            plt.scatter(attributes['pos'][0], attributes['pos'][1], color='blue', s=70, label='Usuario')

    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    plt.legend(loc="best")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()


def plot_splitter_olt_connections(graph, title="Conexión de Splitters a la OLT (Steiner Subóptimo)"):
    """
    Visualiza las conexiones entre splitters y la OLT en el Árbol de Steiner subóptimo.

    Args:
        graph (nx.Graph): Grafo con conexiones entre splitters y la OLT.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')

    if not pos:
        print("No hay posiciones definidas para los nodos. Verifique los atributos del grafo.")
        return

    plt.figure(figsize=(10, 8))

    # Dibujar todas las aristas
    for u, v, data in graph.edges(data=True):
        if data.get('steiner', False):
            # Aristas de Steiner: Color sólido y grosor fijo
            color = "purple"
            linewidth = 1.5
            alpha = 1.0
        else:
            # Aristas originales: Color tenue y grosor estándar
            color = "gray"
            linewidth = 1
            alpha = 0.5
        x_coords = [pos[u][0], pos[v][0]]
        y_coords = [pos[u][1], pos[v][1]]
        plt.plot(x_coords, y_coords, color=color, linewidth=linewidth, alpha=alpha)

    # Destacar nodos (splitters y OLT)
    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'splitter':
            plt.scatter(attributes['pos'][0], attributes['pos'][1], color='red', s=150, label='Splitter', edgecolor='black')
        elif attributes.get('type') == 'OLT':
            olt_pos = attributes['pos']
            rect = plt.Rectangle((olt_pos[0] - 50, olt_pos[1] - 50), 100, 100, color='red', alpha=0.7, label='OLT')
            plt.gca().add_patch(rect)

    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    plt.legend(loc="best")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()



def plot_mst_with_new_routes(graph, mst, title="MST con Nuevas Rutas"):
    """
    Visualiza el MST generado con nuevas rutas junto con el grafo original.

    Args:
        graph (nx.Graph): Grafo original con nodos y aristas.
        mst (nx.Graph): Árbol de Mínima Expansión (MST) generado.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')

    if not pos:
        print("No hay posiciones definidas para los nodos. Verifique los atributos del grafo.")
        return

    plt.figure(figsize=(12, 10))

    # Dibujar todas las aristas originales en gris
    for u, v, data in graph.edges(data=True):
        x_coords = [pos[u][0], pos[v][0]]
        y_coords = [pos[u][1], pos[v][1]]
        plt.plot(x_coords, y_coords, color="gray", linewidth=1, alpha=0.5, label="Arista Original")

    # Dibujar las aristas del MST en azul
    for u, v, data in mst.edges(data=True):
        x_coords = [pos[u][0], pos[v][0]]
        y_coords = [pos[u][1], pos[v][1]]
        plt.plot(x_coords, y_coords, color="blue", linewidth=2, alpha=0.8, label="Arista MST")

    # Dibujar nodos (splitters y OLT)
    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'splitter':
            plt.scatter(attributes['pos'][0], attributes['pos'][1], color='red', s=150, label='Splitter', edgecolor='black')
        elif attributes.get('type') == 'OLT':
            olt_pos = attributes['pos']
            rect = plt.Rectangle((olt_pos[0] - 50, olt_pos[1] - 50), 100, 100, color='blue', alpha=0.7, label='OLT')
            plt.gca().add_patch(rect)

    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    plt.legend([],[],loc="center", frameon=False)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

def plot_users_to_splitters(graph, user_splitter_graph, clusters, title="Conexiones de Usuarios a Splitters"):
    """
    Visualiza las conexiones entre usuarios y splitters, diferenciando por colores de clústeres.

    Args:
        graph (nx.Graph): Grafo original con nodos y aristas.
        user_splitter_graph (nx.Graph): Grafo con conexiones entre usuarios y splitters.
        clusters (dict): Diccionario de clústeres.
        title (str): Título del gráfico.
    """
    pos = nx.get_node_attributes(graph, 'pos')
    
    if not pos:
        print("No hay posiciones definidas para los nodos. Verifique los atributos del grafo.")
        return

    plt.figure(figsize=(12, 10))

    # Colores para los clústeres
    colors = plt.cm.tab20.colors  # Colores predefinidos (20 posibles)

    # Dibujar las aristas del grafo de usuarios a splitters
    for u, v, data in user_splitter_graph.edges(data=True):
        x_coords = [pos[u][0], pos[v][0]]
        y_coords = [pos[u][1], pos[v][1]]
        plt.plot(x_coords, y_coords, color="green", linewidth=2, alpha=0.8)

    # Dibujar nodos (usuarios y splitters) con colores de clúster
    for cluster_id, user_indices in clusters.items():
        cluster_color = colors[cluster_id % len(colors)]  # Colores para cada clúster
        for user in user_indices:
            plt.scatter(pos[user][0], pos[user][1], color=cluster_color, s=50, label=f"O-S {cluster_id}")
    
    # Dibujar splitters y OLT
    for node, attributes in graph.nodes(data=True):
        if attributes.get('type') == 'splitter':
            plt.scatter(attributes['pos'][0], attributes['pos'][1], color='red', s=150, edgecolor='black', label='Splitter')
        elif attributes.get('type') == 'OLT':
            olt_pos = attributes['pos']
            rect = plt.Rectangle((olt_pos[0] - 50, olt_pos[1] - 50), 100, 100, color='blue', alpha=0.7, label='OLT')
            plt.gca().add_patch(rect)

    # Configuración del gráfico
    plt.title(title)
    plt.xlabel("X (metros)")
    plt.ylabel("Y (metros)")
    # Agregar una leyenda única para los clústeres y elementos clave
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Evitar duplicados en la leyenda
    plt.legend(by_label.values(), by_label.keys(), loc="best")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

