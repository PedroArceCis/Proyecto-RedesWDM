class Config:
    def __init__(self):
        # Parámetros de generación de grafo
        self.num_nodes = 50                # Reducir a 50 nodos para mantener el grafo manejable
        self.area = (1000, 1000)           # Dimensiones del área en metros (menor tamaño para reducir dispersión)
        self.input_type = 'random'         # Tipo de entrada: 'random' o 'manual'
        self.manual_nodes = [              # Coordenadas definidas manualmente (si es necesario usar 'manual')
            (200, 300),
            (400, 600),
            (800, 200)
        ]

        # Parámetros de clustering
        self.num_clusters = 5              # Número de clústeres (splitters de segunda etapa)
        self.max_distance_splitters = 300  # Distancia máxima permitida para splitters (en metros)

        # Restricciones adicionales
        self.max_users_per_splitter = 10   # Capacidad máxima de usuarios por splitter
