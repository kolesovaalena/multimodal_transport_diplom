import random
import time
import tracemalloc
import matplotlib.pyplot as plt
import networkx as nx

from route_finder import RouteFinder

# =====================================
# Генерация мультимодального графа
# =====================================

def generate_multilayer_graph(
        num_cities,
        connectivity
):

    graph = nx.Graph()

    cities = [
        f"City_{i}"
        for i in range(num_cities)
    ]

    transports = [
        "car",
        "train",
        "plane"
    ]

    # =====================================
    # Создание вершин
    # =====================================

    for city in cities:

        for transport in transports:

            graph.add_node(
                (city, transport)
            )

    # =====================================
    # Создание транспортных рёбер
    # =====================================

    for transport in transports:

        for i in range(num_cities):

            for j in range(i + 1, num_cities):

                if random.random() < connectivity:

                    city1 = cities[i]
                    city2 = cities[j]

                    distance = random.randint(
                        100,
                        3000
                    )

                    if transport == "car":

                        speed = 80
                        cost_per_km = 12

                    elif transport == "train":

                        speed = 120
                        cost_per_km = 6

                    else:

                        speed = 700
                        cost_per_km = 15

                    time_value = round(
                        distance / speed,
                        2
                    )

                    cost_value = round(
                        distance * cost_per_km,
                        2
                    )

                    graph.add_edge(

                        (city1, transport),
                        (city2, transport),

                        transport=transport,

                        distance=distance,
                        time=time_value,
                        cost=cost_value
                    )

    # =====================================
    # Межслойные пересадки
    # =====================================

    for city in cities:

        for t1 in transports:

            for t2 in transports:

                if t1 == t2:
                    continue

                graph.add_edge(

                    (city, t1),
                    (city, t2),

                    transport="transfer",

                    distance=0,

                    time=1.5,
                    cost=1200
                )

    return graph

# =====================================
# Классический Bellman-Ford
# =====================================

def classic_bellman_ford(
        graph,
        start,
        end
):

    for u, v, data in graph.edges(data=True):

        data["weight"] = data["cost"]

    try:

        path = nx.bellman_ford_path(

            graph,
            start,
            end,

            weight="weight"
        )

        return path

    except:

        return None

# =====================================
# Модифицированный Bellman-Ford
# =====================================

def modified_bellman_ford(
        graph,
        start_city,
        end_city
):

    finder = RouteFinder(graph)

    routes = finder.find_top_routes(

        start_city,
        end_city,

        criterion="balanced",

        top_n=1
    )

    if routes:

        return routes[0]["path"]

    return None

# =====================================
# Benchmark
# =====================================

def benchmark():

    vertex_sizes = [
        10,
        50,
        100,
        300,
        500,
        1000
    ]

    connectivity_values = [
        0.25,
        0.5,
        0.75
    ]

    classic_times = []
    modified_times = []

    classic_memory = []
    modified_memory = []

    # =====================================
    # Эксперименты
    #======================================

    for size in vertex_sizes:

        connectivity = 0.5

        print(f"\nGRAPH SIZE: {size}")

        graph = generate_multilayer_graph(

            size,
            connectivity
        )

        cities = [
            f"City_{i}"
            for i in range(size)
        ]

        start_city = cities[0]
        end_city = cities[-1]

        start_node = (
            start_city,
            "car"
        )

        end_node = (
            end_city,
            "car"
        )

        # =====================================
        # CLASSIC
        # =====================================

        tracemalloc.start()

        start_time = time.perf_counter()

        classic_bellman_ford(

            graph,
            start_node,
            end_node
        )

        classic_elapsed = (
            time.perf_counter() - start_time
        )

        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        classic_times.append(
            classic_elapsed
        )

        classic_memory.append(
            peak / 1024 / 1024
        )

        # =====================================
        # MODIFIED
        # =====================================

        tracemalloc.start()

        start_time = time.perf_counter()

        modified_bellman_ford(

            graph,
            start_city,
            end_city
        )

        modified_elapsed = (
            time.perf_counter() - start_time
        )

        current, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        modified_times.append(
            modified_elapsed
        )

        modified_memory.append(
            peak / 1024 / 1024
        )

        print(
            f"Classic Time: "
            f"{classic_elapsed:.4f}"
        )

        print(
            f"Modified Time: "
            f"{modified_elapsed:.4f}"
        )

    # =====================================
    # ГРАФИК ВРЕМЕНИ
    # =====================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        vertex_sizes,
        classic_times,
        marker="o",
        label="Classic Bellman-Ford"
    )

    plt.plot(
        vertex_sizes,
        modified_times,
        marker="o",
        label="Modified Bellman-Ford"
    )

    plt.xlabel(
        "Количество вершин"
    )

    plt.ylabel(
        "Время выполнения (сек)"
    )

    plt.title(
        "Сравнение быстродействия алгоритмов"
    )

    plt.grid(True)

    plt.legend()

    plt.show()

    # =====================================
    # ГРАФИК ПАМЯТИ
    # =====================================

    plt.figure(figsize=(10, 6))

    plt.plot(
        vertex_sizes,
        classic_memory,
        marker="o",
        label="Classic Bellman-Ford"
    )

    plt.plot(
        vertex_sizes,
        modified_memory,
        marker="o",
        label="Modified Bellman-Ford"
    )

    plt.xlabel(
        "Количество вершин"
    )

    plt.ylabel(
        "Использование памяти (MB)"
    )

    plt.title(
        "Сравнение потребления памяти"
    )

    plt.grid(True)

    plt.legend()

    plt.show()

# =====================================
# Запуск
# =====================================

if __name__ == "__main__":

    benchmark()