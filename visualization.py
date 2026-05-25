from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QFont,
    QPainterPath,
    QRadialGradient
)
from PySide6.QtCore import Qt, QPointF

class GraphWidget(QWidget):

    def __init__(self, graph):

        super().__init__()

        self.graph = graph
        self.route = []

        self.setMinimumSize(1200, 800)

        # =====================================
        # Координаты городов
        # =====================================

        self.city_x = {

            "Санкт-Петербург": 100,
            "Москва": 220,
            "Нижний Новгород": 360,
            "Казань": 520,
            "Самара": 680,
            "Екатеринбург": 900,
            "Омск": 1120,
            "Новосибирск": 1320
        }

        # =====================================
        # Слои
        # =====================================

        self.layer_y = {

            "plane": 140,
            "train": 420,
            "car": 700
        }

        # =====================================
        # Цвета
        # =====================================

        self.transport_colors = {

            "plane": QColor("#ff5252"),
            "train": QColor("#40c4ff"),
            "car": QColor("#69f0ae"),
            "transfer": QColor("#ffd740")
        }

    # =====================================
    # Установка маршрута
    # =====================================

    def set_routes(self, routes):

        self.routes = routes
        self.update()

    # =====================================
    # Отрисовка дуги
    # =====================================

    def draw_curved_edge(
            self,
            painter,
            x1,
            y1,
            x2,
            y2,
            color,
            width=3,
            glow=False,
            dashed=False
    ):

        path = QPainterPath()

        path.moveTo(x1, y1)

        # =====================================
        # Контрольная точка дуги
        # =====================================

        ctrl_x = (x1 + x2) / 2

        # высота изгиба
        curve_height = abs(x2 - x1) * 0.15

        if y1 == y2:
            ctrl_y = y1 - curve_height
        else:
            ctrl_y = (y1 + y2) / 2 - 60

        path.quadTo(
            QPointF(ctrl_x, ctrl_y),
            QPointF(x2, y2)
        )

        # =====================================
        # Glow
        # =====================================

        if glow:

            glow_pen = QPen(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    80
                ),
                width + 8
            )

            glow_pen.setCapStyle(Qt.RoundCap)

            painter.setPen(glow_pen)
            painter.drawPath(path)

        # =====================================
        # Основная линия
        # =====================================

        pen = QPen(color, width)

        if dashed:
            pen.setStyle(Qt.DashLine)

        pen.setCapStyle(Qt.RoundCap)

        painter.setPen(pen)

        painter.drawPath(path)

    # =====================================
    # Paint
    # =====================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # =====================================
        # Фон
        # =====================================

        painter.fillRect(
            self.rect(),
            QColor("#0d1117")
        )

        # =====================================
        # Масштаб
        # =====================================

        scale_x = self.width() / 1600
        scale_y = self.height() / 900

        # =====================================
        # Layer panels
        # =====================================

        layer_panels = [

            ("plane", "#311b1b"),
            ("train", "#13293d"),
            ("car", "#132d20")
        ]

        for layer, color in layer_panels:

            y = self.layer_y[layer] * scale_y

            painter.fillRect(
                40,
                int(y - 80),
                int(1400 * scale_x),
                160,
                QColor(color)
            )

        # =====================================
        # Названия слоев
        # =====================================

        painter.setFont(
            QFont("Arial", 16, QFont.Bold)
        )

        painter.setPen(
            QColor("#ffffff")
        )

        painter.drawText(
            40,
            int(100 * scale_y),
            "AVIATION LAYER"
        )

        painter.drawText(
            40,
            int(380 * scale_y),
            "RAILWAY LAYER"
        )

        painter.drawText(
            40,
            int(660 * scale_y),
            "CAR LAYER"
        )

        # =====================================
        # Неактивные рёбра
        # =====================================

        for u, v, data in self.graph.edges(data=True):

            city1, transport1 = u
            city2, transport2 = v

            x1 = self.city_x[city1] * scale_x
            y1 = self.layer_y[transport1] * scale_y

            x2 = self.city_x[city2] * scale_x
            y2 = self.layer_y[transport2] * scale_y

            transport = data["transport"]

            color = QColor(
                self.transport_colors[
                    transport
                ]
            )

            color.setAlpha(70)

            dashed = False

            if transport == "transfer":
                dashed = True

            self.draw_curved_edge(
                painter,
                x1,
                y1,
                x2,
                y2,
                color,
                width=2,
                dashed=dashed
            )

        # =====================================
        # Активные маршруты
        # =====================================

        route_nodes = set()

        route_colors = [

            QColor("#ffff00"),
            QColor("#ff00ff"),
            QColor("#00ffff")
        ]

        if self.routes:

            for route_index, route in enumerate(self.routes):

                color = route_colors[
                    route_index % len(route_colors)
                    ]

                for i in range(len(route) - 1):

                    city1, transport1 = route[i]
                    city2, transport2 = route[i + 1]

                    route_nodes.add(
                        (city1, transport1)
                    )

                    route_nodes.add(
                        (city2, transport2)
                    )

                    x1 = self.city_x[city1] * scale_x
                    y1 = self.layer_y[transport1] * scale_y

                    x2 = self.city_x[city2] * scale_x
                    y2 = self.layer_y[transport2] * scale_y

                    edge = self.graph[
                        route[i]
                    ][
                        route[i + 1]
                    ]

                    transport = edge["transport"]

                    dashed = False

                    if transport == "transfer":
                        dashed = True

                    self.draw_curved_edge(
                        painter,
                        x1,
                        y1,
                        x2,
                        y2,
                        color,
                        width=6,
                        glow=True,
                        dashed=dashed
                    )

        # =====================================
        # Вершины
        # =====================================

        for node in self.graph.nodes:

            city, transport = node

            x = self.city_x[city] * scale_x
            y = self.layer_y[transport] * scale_y

            color = self.transport_colors[
                transport
            ]

            # =====================================
            # Активная вершина
            # =====================================

            active = False

            if node in route_nodes:
                active = True

            # =====================================
            # Glow
            # =====================================

            radius = 18

            if active:
                radius = 28

            gradient = QRadialGradient(QPointF(x, y),
                radius
            )

            gradient.setColorAt(
                0,
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    255
                )
            )

            gradient.setColorAt(
                1,
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    0
                )
            )

            painter.setBrush(gradient)

            painter.setPen(Qt.NoPen)

            painter.drawEllipse(
                QPointF(x, y),
                radius,
                radius
            )

            # =====================================
            # Core
            # =====================================

            painter.setBrush(color)

            core_size = 8

            if active:
                core_size = 12

            painter.drawEllipse(
                QPointF(x, y),
                core_size,
                core_size
            )

            # =====================================
            # Подписи
            # =====================================

            painter.setPen(
                QColor("#ffffff")
            )

            painter.setFont(
                QFont("Arial", 9)
            )

            painter.drawText(
                int(x - 45),
                int(y - 25),
                city
            )

        # =====================================
        # Легенда
        # =====================================

        legend_y = 820 * scale_y

        legends = [

            ("plane", "Авиация"),
            ("train", "Железная дорога"),
            ("car", "Автомобильный"),
            ("transfer", "Пересадка")
        ]

        x_pos = 80

        painter.setFont(
            QFont("Arial", 11)
        )

        for key, text in legends:

            color = self.transport_colors[key]

            painter.setBrush(color)

            painter.setPen(Qt.NoPen)

            painter.drawRect(
                int(x_pos),
                int(legend_y),
                28,
                28
            )

            painter.setPen(
                QColor("#ffffff")
            )

            painter.drawText(
                int(x_pos + 40),
                int(legend_y + 20),
                text
            )

            x_pos += 260