import json
import networkx as nx

class GraphModel:

    def __init__(self):

        self.graph = nx.Graph()

    # =====================================
    # Загрузка данных
    # =====================================

    def load_data(self, filename):

        with open(
                filename,
                "r",
                encoding="utf-8"
        ) as file:

            routes = json.load(file)

        # =====================================
        # Добавление маршрутов
        # =====================================

        for route in routes:

            city_from = route["from"]
            city_to = route["to"]

            transport = route["transport"]

            node_from = (
                city_from,
                transport
            )

            node_to = (
                city_to,
                transport
            )

            self.graph.add_edge(

                node_from,
                node_to,

                transport=transport,

                distance=route["distance"],

                time=route["time"],

                cost=route["cost"]
            )

        # =====================================
        # Межслойные перегрузки
        # =====================================

        self.add_transfer_edges()

    # =====================================
    # Transfer edges
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

        transfer_count = 0

        for city in cities:

            for t1 in transports:

                for t2 in transports:

                    if t1 == t2:
                        continue

                    node1 = (city, t1)
                    node2 = (city, t2)

                    if (
                            node1 in self.graph.nodes
                            and
                            node2 in self.graph.nodes
                    ):

                        self.graph.add_edge(

                            node1,
                            node2,

                            transport="transfer",

                            distance=0,

                            time=1.5,

                            cost=1200
                        )

                        transfer_count += 1

        print(
            f"TRANSFER EDGES: {transfer_count}"
        )

    # =====================================
    # Получение графа
    # =====================================

    def get_graph(self):

        return self.graph