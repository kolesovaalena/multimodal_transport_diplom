from os import path

import networkx as nx

class RouteFinder:

    def __init__(self, graph):

        self.graph = graph

    # =====================================
    # Проверка пути
    # =====================================

    def is_valid_path(self, path):

        # =====================================
        # Запрет старта с пересадки
        # =====================================

        if len(path) >= 2:
            if path[0][0] == path[1][0]:
                return False

        # =====================================
        # Запрет конца с пересадки
        # =====================================

        if len(path) >= 2:
            if path[-1][0] == path[-2][0]:
                return False

        # =====================================
        # Запрет длинных пересадок подряд
        # =====================================

        same_city_count = 1

        for i in range(1, len(path)):

            prev_city = path[i - 1][0]
            current_city = path[i][0]

            if prev_city == current_city:
                same_city_count += 1

            else:
                same_city_count = 1

            if same_city_count > 2:
                return False

        # =====================================
        # Проверка повторов городов
        # =====================================

        visited = []

        for node in path:
            city = node[0]

            # допускаем повтор только для пересадки
            if city in visited:

                # повтор подряд = пересадка
                prev_city = visited[-1]

                if city != prev_city:
                    return False

            visited.append(city)

        return True

    # =====================================
    # Поиск маршрутов
    # =====================================

    def find_top_routes(
            self,
            start_city,
            end_city,
            criterion="balanced",
            top_n=3
    ):

        start_nodes = [
            node for node in self.graph.nodes
            if node[0] == start_city
        ]

        end_nodes = [
            node for node in self.graph.nodes
            if node[0] == end_city
        ]
        print("START NODES:", start_nodes)
        print("END NODES:", end_nodes)

        routes = []

        for u, v, data in self.graph.edges(data=True):
            cost = data["cost"]
            time = data["time"]

            transfer_penalty = 0

            if data["transport"] == "transfer":
                transfer_penalty = 2500

            if criterion == "cost":
                data["weight"] = cost + transfer_penalty
            elif criterion == "time":
                data["weight"] = time * 100 + transfer_penalty
            else:
                data["weight"] = cost + time * 250 + transfer_penalty

        for start in start_nodes:
            for end in end_nodes:
                try:
                    path = nx.bellman_ford_path(
                        self.graph,
                        start,
                        end,
                        weight="weight"
                    )
                    if not self.is_valid_path(path):
                        continue

                    route_data = self.calculate_route(path)
                    routes.append(route_data)

                except:
                    continue

        # =====================================
        # Удаление дублей
        # =====================================

        unique_routes = []
        seen = set()
        for route in routes:
            key = tuple(route["path"])
            if key not in seen:
                seen.add(key)
                unique_routes.append(route)

        # =====================================
        # Сортировка
        # =====================================

        if criterion == "cost":
            unique_routes.sort(
                key=lambda x: x["total_cost"]
            )

        elif criterion == "time":
            unique_routes.sort(
                key=lambda x: x["total_time"]
            )

        else:
            unique_routes.sort(
                key=lambda x: x["balanced_score"]
            )

        return unique_routes[:top_n]


    # =====================================
    # Подсчёт параметров
    # =====================================

    def calculate_route(self, path):

        total_cost = 0
        total_time = 0
        transfers = 0

        used_transports = []
        formatted_path = []

        # =====================================
        # Проход по маршруту
        # =====================================

        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            edge = self.graph[u][v]
            transport = edge["transport"]
            total_cost += edge["cost"]
            total_time += edge["time"]

            # =====================================
            # Пересадки
            # =====================================

            if transport == "transfer":
                transfers += 1

            # =====================================
            # Использованный транспорт
            # =====================================

            if transport != "transfer":
                used_transports.append(transport)

        # =====================================
        # Форматирование пути
        # =====================================

        for i, node in enumerate(path):
            city, transport = node

            if i > 0:
                prev_transport = path[i - 1][1]
                if prev_transport != transport:
                     formatted_path.append(
                        f"Пересадка:\n"
                        f"{city}: "
                        f"{prev_transport} → "
                        f"{transport}"
                     )
            formatted_path.append(
                f"{city} ({transport})"
            )
        # =====================================
        # Итоговый score
        # =====================================

        balanced_score = (
            total_cost +
            total_time * 250 +
            transfers * 2500
        )

        return {
            "path": path,
            "formatted_path": formatted_path,
            "total_cost": round(total_cost, 2),
            "total_time": round(total_time, 2),
            "transfers": transfers,
            "balanced_score": round(balanced_score, 2),
            "used_transports": list(set(used_transports))
        }