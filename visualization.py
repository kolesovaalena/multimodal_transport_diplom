from PIL.ImageOps import scale
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QFont,
    QBrush
)
from PySide6.QtCore import Qt

class GraphWidget(QWidget):

    def __init__(self, graph):

        super().__init__()

        self.graph = graph

        self.route = None

        self.setMinimumSize(1200, 800)

        # =====================================
        # X-Координаты городов
        # =====================================

        self.city_x = {

            "Санкт-Петербург": 100,
            "Москва": 250,
            "Нижний Новгород": 420,
            "Казань": 600,
            "Самара": 760,
            "Екатеринбург": 980,
            "Омск": 1200,
            "Новосибирск": 1450
        }

        # =====================================
        # Y-Координаты слоёв
        # =====================================

        self.layer_y = {

            "plane": 120,
            "train": 360,
            "car": 620
        }
        # =====================================
        # Цвета транспорта
        # =====================================

        self.transport_colors = {

            "plane": QColor("#ff5252"),
            "train": QColor("#40c4ff"),
            "car": QColor("#69f0ae"),
            "transfer": QColor("#ffd740")
        }

    # =========================================
    # Установка маршрута
    # =========================================

    def set_route(self, route):

        self.route = route
        self.update()

    # =========================================
    # Рисование
    # =========================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # =====================================
        # Тёмный фон
        # =====================================

        painter.fillRect(
            self.rect(),
            QColor("#111111")
        )

        # =====================================
        # Масштаб
        # =====================================

        scale_x = self.width() / 1600
        scale_y = self.height() / 800

        # =====================================
        # Подписи слоёв
        # =====================================

        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.setPen(QColor("#ffffff"))

        painter.drawText(20, int(150 * scale_y), "AVIATION LAYER")
        painter.drawText(20, int(390 * scale_y), "RAILWAY LAYER")
        painter.drawText(20, int(650 * scale_y), "CAR LAYER")

        # =====================================
        # Горизонтальные линии слоёв
        # =====================================

        for layer, y in self.layer_y.items():
            pen = QPen(
                QColor("#333333"),
                2,
                Qt.DashLine
            )

            painter.setPen(pen)
            painter.drawLine(
                50,
                int(y * scale_y),
                int(1550 * scale_x),
                int(y * scale_y)
            )

        # =====================================
        # Рёбра графа
        # =====================================

        for u, v, data in self.graph.edges(data=True):
            city1, transport1 = u
            city2, transport2 = v

            x1 = self.city_x[city1]
            y1 = self.layer_y[transport1]

            x2 = self.city_x[city2]
            y2 = self.layer_y[transport2]

            x1 *= scale_x
            y1 *= scale_y

            x2 *= scale_x
            y2 *= scale_y

            transport = data["transport"]
            color = self.transport_colors[transport]

            # =====================================
            # Transfer edge
            # =====================================

            if transport == "transfer":
                pen = QPen(
                    color,
                    2,
                    Qt.DashLine
                )

            else:
                pen = QPen(
                    color,
                    4
                )
            painter.setPen(pen)
            painter.drawLine(
                int(x1),
                int(y1),

                int(x2),
                int(y2)
            )

        # =====================================
        # Подсветка маршрута
        # =====================================

        if self.route:

            # glow
            glow_pen = QPen(
                QColor("#fff176"),
                12
            )
            painter.setPen(glow_pen)

            for i in range(len(self.route) - 1):
                city1, transport1 = self.route[i]
                city2, transport2 = self.route[i + 1]

                x1 = self.city_x[city1]
                y1 = self.layer_y[transport1]

                x2 = self.city_x[city2]
                y2 = self.layer_y[transport2]

                x1 *= scale_x
                y1 *= scale_y

                x2 *= scale_x
                y2 *= scale_y

                painter.drawLine(

                    int(x1),
                    int(y1),

                    int(x2),
                    int(y2)
                )

            # основная линия
            route_pen = QPen(
                QColor("#ffff00"),
                6
            )
            painter.setPen(route_pen)

            for i in range(len(self.route) - 1):
                city1, transport1 = self.route[i]
                city2, transport2 = self.route[i + 1]

                x1 = self.city_x[city1]
                y1 = self.layer_y[transport1]

                x2 = self.city_x[city2]
                y2 = self.layer_y[transport2]

                x1 *= scale_x
                y1 *= scale_y

                x2 *= scale_x
                y2 *= scale_y

                painter.drawLine(
                    int(x1),
                    int(y1),

                    int(x2),
                    int(y2)
                )

        # =====================================
        # Вершины
        # =====================================

        for node in self.graph.nodes:
            city, transport = node

            x = self.city_x[city]
            y = self.layer_y[transport]

            x *= scale_x
            y *= scale_y

            color = self.transport_colors[transport]

            # glow
            painter.setBrush(
                QColor(
                    color.red(),
                    color.green(),
                    color.blue(),
                    120
                )
            )

            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(x - 16),
                int(y - 16),

                32,
                32
            )

            # core
            painter.setBrush(color)
            painter.drawEllipse(
                int(x - 8),
                int(y - 8),

                16,
                16
            )

            # подпись
            painter.setPen(
                QColor("#ffffff")
            )
            painter.setFont(
                QFont("Arial",9)
            )
            painter.drawText(
                int(x - 40),
                int(y - 20),
                f"{city}"
            )

        # =====================================
        # Легенда
        # =====================================

        legend_y = 720 * scale_y
        painter.setFont(
            QFont("Arial",10)
        )

        legends = [
            ("plane", "Авиация"),
            ("train", "Железная дорога"),
            ("car", "Автомобильный"),
            ("transfer", "Пересадка")
        ]

        x_pos = 80

        for key, text in legends:
            color = self.transport_colors[key]
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(
                int(x_pos),
                int(legend_y),
                25,
                25
            )

            painter.setPen(
                QColor("#ffffff")
            )

            painter.drawText(
                int(x_pos + 35),
                int(legend_y + 18),
                text
            )

            x_pos += 250