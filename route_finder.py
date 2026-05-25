import networkx as nx
import copy

class RouteFinder:

    def __init__(self, graph):

        self.graph = graph

    # =====================================
    # Проверка пути
    # =====================================

    def is_valid_path(self, path):

        visited = []

        for node in path:

            city = node[0]

            # =====================================
            # Повтор разрешён только подряд
            # =====================================

            if city in visited:

                prev_city = visited[-1]

                if city != prev_city:
                    return False

            visited.append(city)

        # =====================================
        # Запрет длинных пересадок
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

        return True

    # =====================================
    # Вес ребра
    # =====================================

    def calculate_edge_weight(
            self,
            edge,
            alpha,
            beta,
            gamma
    ):

        cost = edge["cost"]
        time = edge["time"]

        transfer_penalty = 0

        if edge["transport"] == "transfer":
            transfer_penalty = 1

        weight = (

                alpha * cost +

                beta * time +

                gamma * transfer_penalty
        )

        return weight

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

        routes = []

        # =====================================
        # Коэффициенты
        # =====================================

        if criterion == "cost":

            alpha = 1.0
            beta = 10
            gamma = 3000

        elif criterion == "time":

            alpha = 0.05
            beta = 1000
            gamma = 1500

        else:

            alpha = 0.6
            beta = 400
            gamma = 2500

        # =====================================
        # Вес рёбер
        # =====================================

        for u, v, data in self.graph.edges(data=True):

            data["weight"] = self.calculate_edge_weight(
                data,
                alpha,
                beta,
                gamma
            )

        # =====================================
        # Стартовые вершины
        # =====================================

        start_nodes = [

            node for node in self.graph.nodes

            if node[0] == start_city
        ]

        # =====================================
        # Конечные вершины
        # =====================================

        end_nodes = [

            node for node in self.graph.nodes

            if node[0] == end_city
        ]

        # =====================================
        # Временный граф
        # =====================================

        temp_graph = copy.deepcopy(self.graph)

        # =====================================
        # Top маршруты
        # =====================================

        for _ in range(top_n):

            best_route = None
            best_score = float("inf")

            for start in start_nodes:

                for end in end_nodes:

                    try:

                        # =====================================
                        # Bellman-Ford
                        # =====================================

                        path = nx.bellman_ford_path(

                            temp_graph,

                            start,
                            end,weight="weight"
                        )

                        # =====================================
                        # Проверка пути
                        # =====================================

                        if not self.is_valid_path(path):
                            continue

                        # =====================================
                        # Подсчёт параметров
                        # =====================================

                        route_data = self.calculate_route(path)

                        # =====================================
                        # Критерий выбора
                        # =====================================

                        if criterion == "cost":

                            route_score = (
                                route_data["total_cost"]
                            )

                        elif criterion == "time":

                            route_score = (
                                route_data["total_time"]
                            )

                        else:

                            route_score = (
                                route_data["balanced_score"]
                            )

                        # =====================================
                        # Лучший маршрут
                        # =====================================

                        if route_score < best_score:

                            best_score = route_score

                            best_route = route_data

                    except:
                        continue

            # =====================================
            # Если найден маршрут
            # =====================================

            if best_route:

                routes.append(best_route)

                path = best_route["path"]

                # =====================================
                # Удаляем одно ребро
                # =====================================

                removed = False

                for i in range(len(path) - 1):

                    u = path[i]
                    v = path[i + 1]

                    edge = temp_graph[u][v]

                    # не удаляем transfer
                    if edge["transport"] != "transfer":

                        if temp_graph.has_edge(u, v):

                            temp_graph.remove_edge(u, v)

                            removed = True
                            break

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

        return unique_routes

    # =====================================
    # Подсчёт маршрута
    # =====================================

    def calculate_route(self, path):

        total_cost = 0
        total_time = 0

        transfers = 0

        used_transports = []

        formatted_path = []

        # =====================================
        # Подсчёт параметров
        # =====================================

        for i in range(len(path) - 1):

            u = path[i]
            v = path[i + 1]

            edge = self.graph[u][v]

            transport = edge["transport"]

            edge_cost = edge["cost"]
            edge_time = edge["time"]

            # =====================================
            # Стоимость
            # =====================================

            total_cost += edge_cost

            # =====================================
            # Время
            # =====================================

            total_time += edge_time

            # =====================================
            # Самолёт
            # =====================================

            if transport == "plane":

                total_time +=1.5

            # =====================================
            # Поезд
            # =====================================

            elif transport == "train":

                total_time += 0.3

            # =====================================
            # Пересадки
            # =====================================

            if transport == "transfer":

                transfers += 1

                total_cost += 1200
                total_time += 1.0

            # =====================================
            # Использованный транспорт
            # =====================================

            if transport != "transfer":

                used_transports.append(
                    transport
                )

        # =====================================
        # Бонус мультимодальности
        # =====================================

        multimodal_bonus = 0

        if len(set(used_transports)) >= 2:

            multimodal_bonus = -1000

        # =====================================
        # Balanced score
        # =====================================

        balanced_score = (

                total_cost +

                total_time * 250 +

                transfers * 2500 +

                multimodal_bonus
        )

        # =====================================
        # Формирование пути
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
        # Удаление дублей
        # =====================================

        cleaned_path = []

        for item in formatted_path:

            if len(cleaned_path) == 0:

                cleaned_path.append(item)

                continue

            if item != cleaned_path[-1]:

                cleaned_path.append(item)

        return {

            "path": path,

            "formatted_path": cleaned_path,

            "total_cost": round(
                total_cost,
                2
            ),

            "total_time": round(
                total_time,
                2
            ),

            "transfers": transfers,

            "balanced_score": round(
                balanced_score,
                2
            ),

            "used_transports": list(
                set(used_transports)
            )
        }