from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os
import random

class PoopWidget(QWidget):
    def __init__(self, parent, x=0, y=0):
        super().__init__(parent)

        self.label = QLabel(self)

        random_index = random.randint(1, 5)
        poop_path = os.path.join(os.path.dirname(__file__), "frames", "poop", f"{random_index}.png")
        poopPixmap = QPixmap(poop_path)

        if poopPixmap.isNull():
            print(f"⚠️ 图片加载失败: {poop_path}")
            return

        # 改为固定缩放大小（比如40x30像素）
        scaledPixmap = poopPixmap.scaled(
            40, 30,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.label.setPixmap(scaledPixmap)
        self.label.resize(scaledPixmap.size())
        # self.resize(scaledPixmap.size())
        self.move(x, y)
        self.show()
        print(f"💩 poop {random_index} created at ({x}, {y})")
