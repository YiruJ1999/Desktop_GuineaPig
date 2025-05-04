import os
import numpy as np
from PySide6.QtWidgets import QLabel,QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer


class Carpet(QWidget):
    def __init__(self,width = 20, height = 20, x=0, y=0, parent=None):
        super().__init__(parent)

#        carpet_image_path = os.path.join(os.path.dirname(__file__), 'frames\carpet', '2.png')
#        pixmap = QPixmap(carpet_image_path)

        # 设置大小和位置
        #self.setPixmap(pixmap)
        self.width = width
        self.height = height
        self.currentPosition = 2 # currentPosition = 0 ... 4 . 2 = MID
    
        #self.allPositions = [mid, left, right, midleft, midright]
        #self.allStatus = [mid, left, right, midleft, midright, leftmid, rightmid]

        # 导入贴图，设置动画
        self.preloadImages()

        self.label = QLabel(self)
        self.label.setGeometry(0,0,100,100)
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.updateAnimation)
        self.animationTimer.start(100)

        self.move(x,y)

    def preloadImages(self):

        self.images = {}

        for status in range(0,5):
            folderPath = f"./frames/carpet"
            filename = f"{status}.png"

            if os.path.exists(folderPath):
                pixmap = QPixmap(os.path.join(folderPath, filename))
                if pixmap.isNull():
                    continue

            # 缩放原图
            scaled = pixmap.scaled(
                self.width,
                self.height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.images[status] = scaled


    def updateAnimation(self):
        self.label.setPixmap(self.images[self.currentPosition])    


    def carpetMove(self,direction):
        if direction > 0 :
            self.currentPosition = min(self.currentPosition+1,4) 
        elif direction < 0:
            self.currentPosition = max(self.currentPosition-1,0) 
        elif direction == 0:
            self.currentPosition = np.sign(2-self.currentPosition) + self.currentPosition
