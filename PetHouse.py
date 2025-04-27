from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtCore import QRect, QPoint
import os


class PetHouse(QWidget):
    def __init__(self, width, height,x=0, y=0, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.setFixedSize(width, height)
        self.move(x, y)

        # 主房子层
        self.main_layer = QLabel(self)
        self.main_layer.setGeometry(0, 0, width, height)
        self.main_layer.raise_()

        # 阴影层（在主房子上面）
        self.shadow_layer = QLabel(self)
        self.shadow_layer.setGeometry(0, 0, width, height)

        # 加载PNG图像
        image_path = os.path.join(os.path.dirname(__file__), 'frames\\house\\')
        self.layers = []
        self.layers.append(QPixmap(image_path + 'back').scaled(self.width, self.height))
        self.layers.append(QPixmap(image_path + 'front').scaled(self.width, self.height))

    def paintEvent(self, event):
        painter = QPainter(self)
        # 绘制PNG图像作为房子外观
        for pixmap in self.layers:
            painter.drawPixmap(0, 0, pixmap)

        # 画阴影层 (可选，保持半透明遮罩)
        #painter.setBrush(QColor(50, 50, 50, 100))
        #painter.setPen(QColor(50, 50, 50, 100))
        #painter.drawRect(QRect(0, int(self.height * 0.7), self.width, int(self.height * 0.3)))


    