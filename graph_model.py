import json
import networkx as nx

class GraphModel:

    def __init__(self):

        self.graph = nx.Graph()

    # =====================================
    # Загрузка данных
    # =====================================

    def load_data(self, filename):

        with open(filename, "r", encoding="utf-8") as file:

            routes = json.load(file)

        # =====================================
        # Добавление транспортных маршрутов
        # =====================================

        for route in routes:

            city_from = route["from"]
            city_to = route["to"]

            transport = route["transport"]

            node_from = (city_from, transport)
            node_to = (city_to, transport)

            edge_data = {
                "transport": transport,
                "distance": route["distance"],
                "time": route["time"],
                "cost": route["cost"]
            }

            self.graph.add_edge(
                node_from,
                node_to,
                **edge_data
            )

            self.graph.add_edge(
                node_to,
                node_from,
                **edge_data
            )

        # =====================================
        # Добавление пересадок
        # =====================================

        self.add_transfer_edges()

    # =====================================
    # Пересадки
    # =====================================

    def add_transfer_edges(self):

        cities = set()

        for node in self.graph.nodes:
            cities.add(node[0])

        transports = [
            "car",
            "train",
            "plane"
        ]

        for city in cities:
            for t1 in transports:
                for t2 in transports:
                    if t1 == t2:
                        continue

                    node1 = (city, t1)
                    node2 = (city, t2)

                    self.graph.add_node(node1)
                    self.graph.add_node(node2)

                    self.graph.add_edge(
                        node1,
                        node2,
                        transport="transfer",
                        distance=0,
                        time=1.5,
                        cost=1200
                    )
                    self.graph.add_edge(
                        node2,
                        node1,
                        transport="transfer",
                        distance=0,
                        time=1.5,
                        cost=1200
                    )
        print("TRANSFER EDGES:", sum(
            1 for _, _, d in self.graph.edges(data=True)
            if d["transport"] == "transfer"
        ))

    # =====================================
    # Получение графа
    # =====================================

    def get_graph(self):

        return self.graph