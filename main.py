from config import Config
from utils.graph_utils import generate_graph
from utils.clustering import perform_clustering
from utils.routing import  connect_splitters_to_olt_with_steiner, connect_splitters_to_olt, connect_users_to_splitters
from utils.visualization import plot_graph, plot_clusters, plot_splitter_olt_connections, plot_mst_with_new_routes, plot_users_to_splitters

def main():
    # Configuración
    config = Config()

    # Paso 1: Generar el grafo inicial con la OLT incluida
    print("Generando el grafo inicial con la OLT...")
    graph, nodes = generate_graph(config)

    # Paso 2: Realizar clustering con restricciones
    print("Realizando clustering basado en nodos existentes del grafo...")
    clusters, splitters, graph = perform_clustering(graph, nodes, config)

    # Paso 3: Conectar usuarios a splitters


    # Visualización
    print("Generando visualizaciones...")
    plot_graph(graph, nodes, "Grafo Inicial con OLT")
    plot_clusters(graph, nodes, clusters, splitters, "Clustering de nodos con Splitters")

    # Paso 4: Conectar splitters a la OLT utilizando Árbol de Steiner con todos los nodos
    print("Conectando splitters a la OLT utilizando Árbol de Steiner...")
    splitter_olt_graph = connect_splitters_to_olt_with_steiner(graph, splitters, config)

    # Visualización
    print("Generando visualización del Árbol de Steiner...")
    plot_splitter_olt_connections(splitter_olt_graph, "Conexión de Splitters a la OLT (Steiner Subóptimo)")

# Generar nuevas rutas
    print("Generando nuevas rutas para el Árbol de Steiner...")
    new_routes_graph = connect_splitters_to_olt(graph, splitters, config)

    # Visualizar el grafo original y las nuevas rutas
    print("Visualizando las nuevas rutas junto con el grafo original...")
    plot_mst_with_new_routes(graph, new_routes_graph, title="Grafo de rutas para el Árbol de MST")

    # Conectar usuarios a splitters
    print("Conectando usuarios a splitters...")
    user_splitter_graph = connect_users_to_splitters(graph, clusters, config)

    # Visualizar las conexiones entre usuarios y splitters
    print("Visualizando conexiones de usuarios a splitters...")
    plot_users_to_splitters(graph, user_splitter_graph, clusters, title="Conexiones de Usuarios a Splitters")


    print("Proceso completado con éxito.")

if __name__ == "__main__":
    main()
