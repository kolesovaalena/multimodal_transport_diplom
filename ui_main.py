from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QTextEdit
)

from graph_model import GraphModel
from route_finder import RouteFinder

from visualization import GraphWidget

class TransportApp(QWidget):

    def __init__(self):

        super().__init__()

        # =====================================
        # Загрузка графа
        # =====================================

        self.graph_model = GraphModel()

        self.graph_model.load_data(
            "data/routes.json"
        )

        self.graph = self.graph_model.get_graph()
        print("NODES: ")
        print(len(self.graph.nodes))
        print("EDGES: ")
        print(len(self.graph.edges))

        self.route_finder = RouteFinder(
            self.graph
        )

        # =====================================
        # Настройки окна
        # =====================================

        self.setWindowTitle(
            "Мультимодальная транспортная система"
        )

        self.resize(1600, 900)

        # =====================================
        # Стили
        # =====================================

        self.setStyleSheet("""

        QWidget {
            background-color: #1e1e1e;
            color: white;
            font-size: 14px;
        }
        
        QLabel {
            font-size: 14px;
        }
        
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 6px;
            min-width: 150px;
        }

        QPushButton {
            background-color: #0078d7;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #2893ff;
        }

        QTextEdit {
            background-color: #252526;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            font-family: Consolas;
            font-size: 13px;
        }

        """)

        self.init_ui()

    # =====================================
    # Интерфейс
    # =====================================

    def init_ui(self):

        main_layout = QHBoxLayout()

        # =====================================
        # Левая панель
        # =====================================

        left_panel = QVBoxLayout()

        title = QLabel(
            "Поиск оптимального маршрута"
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        """)

        left_panel.addWidget(title)

        # =====================================
        # Города
        # =====================================

        cities = sorted(list(set(
            node[0]
            for node in self.graph.nodes
        )))

        # =====================================
        # Выбор городов
        # =====================================

        controls = QVBoxLayout()
        controls.addWidget(
            QLabel("Начальный город")
        )

        self.start_combo = QComboBox()
        self.start_combo.addItems(cities)
        self.start_combo.setCurrentText("Москва")

        controls.addWidget(self.start_combo)
        controls.addWidget(
            QLabel("Конечный город")
        )

        self.end_combo = QComboBox()
        self.end_combo.addItems(cities)
        self.end_combo.setCurrentText("Новосибирск")

        controls.addWidget(self.end_combo)

        # ==========================================
        # Критерий
        # ==========================================

        controls.addWidget(
            QLabel("Критерий оптимизации")
        )
        self.criterion_combo = QComboBox()
        self.criterion_combo.addItems([
            "cost",
            "time",
            "balanced"
        ])
        self.criterion_combo.setCurrentText("balanced")
        controls.addWidget(self.criterion_combo)

        # ==========================================
        # Кнопка
        # ==========================================

        self.search_button = QPushButton(
            "Найти маршруты"
        )

        self.search_button.clicked.connect(
            self.find_routes
        )

        controls.addWidget(
            self.search_button
        )

        controls.addWidget(
            self.start_combo
        )

        left_panel.addLayout(controls)

        # ==========================================
        # Вывод маршрутов
        # ==========================================

        self.output = QTextEdit()

        self.output.setReadOnly(True)

        left_panel.addWidget(self.output)

        # ==========================================
        # Правая часть
        # ==========================================

        self.graph_widget = GraphWidget(self.graph)

        # ==========================================
        # Главный layout
        # ==========================================

        main_layout.addLayout(
            left_panel,
            1
        )

        main_layout.addWidget(
            self.graph_widget,
            2
        )

        self.setLayout(main_layout)

        # ==========================================
        # Первичная отрисовка
        # ==========================================



    # ==========================================
    # Поиск маршрутов
    # ==========================================

    def find_routes(self):

        start_city = (
            self.start_combo.currentText()
        )

        end_city = (
            self.end_combo.currentText()
        )

        criterion = (
            self.criterion_combo.currentText()
        )

        routes = self.route_finder.find_top_routes(

            start_city,
            end_city,
            criterion=criterion,
            top_n=3
        )

        self.output.clear()

        if not routes:
            self.output.append(
                "Маршруты не найдены"
            )
            return

        # ==========================================
        # Вывод маршрутов
        # ==========================================

        for i, route in enumerate(routes, 1):

            self.output.append(
                f"\n========== МАРШРУТ {i} ==========\n"
            )

            for step in route[
                "formatted_path"
            ]:

                self.output.append(
                    f"➜ {step}"
                )

            self.output.append(
                "\n------------------"
            )

            self.output.append(
                f"Стоимость: "
                f"{route['total_cost']} ₽"
            )

            self.output.append(
                f"Время: "
                f"{route['total_time']} ч"
            )

            self.output.append(
                f"Пересадки: "
                f"{route['transfers']}"
            )

            self.output.append(
                f"Balanced score: "
                f"{route['balanced_score']}"
            )

        # ==========================================
        # Рисуем лучший маршрут
        # ==========================================

        self.graph_widget.set_route(
            routes[0]["path"]
        )