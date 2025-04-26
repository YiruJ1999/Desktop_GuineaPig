from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize, QPoint


class Carpet(QLabel):
    def __init__(self, width, height, x=0, y=0, parent=None):
        super().__init__(parent)

        carpet_image_path = 'componentsPic\carpet.png'
        pixmap = QPixmap(carpet_image_path)

        # 设置大小和位置
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.resize(width, height)
        self.move(x, y)
