from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize, QPoint


class Carpet(QLabel):
    def __init__(self, x=0, y=0, parent=None):
        super().__init__(parent)

        carpet_image_path = 'frames\carpet\carpet.png'
        pixmap = QPixmap(carpet_image_path)

        # 设置大小和位置
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.resize(width, height)
        self.move(x, y)

        self.allPositions = [mid, left, right, midleft, midright]
        self.allStatus = [mid, left, right, midleft, midright, leftmid, rightmid]

        self.label = QLabel(self)
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.updateAnimation)
        self.animationTimer.start(300)

        self.scaleFactor = scaleFactor

    def preloadImages(self):

        
        self.images = {}

        for status in range(0,5):
            filename = f"./frames/carpet/{status}.png"

            if os.path.exists(filename):
                pixmap = QPixmap(filename)
                if pixmap.isNull():
                    continue

            # 缩放原图
            scaled = pixmap.scaled(
                pixmap.width() * self.scaleFactor,
                pixmap.height() * self.scaleFactor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.images[status] = scaled


    def updateAnimation(self):
        
        self.label.setPixmap(self.images[2])    


    def carpetMove(self):
        return