from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

class PoopWidget(QLabel):
    def __init__(self, x=0, y=0):
        super().__init__(None)   # 注意：这里 parent=None，真正无父窗口

        poop_path = os.path.join(os.path.dirname(__file__), "frames", "poop", "1.png")
        poopPixmap = QPixmap(poop_path)

        if poopPixmap.isNull():
            print(f"⚠️ 图片加载失败: {poop_path}")
            return

        poopPixmap = poopPixmap.scaled(
            poopPixmap.width() * 0.05,
            poopPixmap.height() * 0.05,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(poopPixmap)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # 👈 注意换成Qt.Tool！
        self.resize(poopPixmap.size())
        self.move(x, y)
        self.show()
        print(f"💩 poop created at ({x}, {y})")
