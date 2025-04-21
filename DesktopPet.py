import sys
import os

import numpy as np
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QWidget, QLabel

class DesktopPet(QWidget):

    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        # 设置无边框 & 始终置顶 & 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 所有状态
        self.allStatus = ['sleep', 'walk', 'drag']
        
        # 缩放比例，预读取图片
        self.scaleFactor = 0.1
        self.preloadImages()
        
        # 设定初始状态
        self.initState()
        
    def preloadImages(self):
        #预加载所有状态的图片并缓存到字典中
        self.imageCache = {}
        for status in self.allStatus:
            folderPath = f"./frames/{status}"
            images = []
            if os.path.exists(folderPath):
                for filename in sorted(os.listdir(folderPath)):
                    if filename.endswith(".png"):
                        pixmap = QPixmap(os.path.join(folderPath, filename))
                        if pixmap.isNull():
                            continue
                        scaled = pixmap.scaled(
                            pixmap.width() * self.scaleFactor,
                            pixmap.height() * self.scaleFactor,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        images.append(scaled)
            self.imageCache[status] = images

    def initState(self):
        # 初始状态：速度，睡觉，向左
        self.speed = 1
        self.direction = -1  # 提前设定方向
        
        # 初始化 label 和动画定时器
        self.label = QLabel(self)
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.updateAnimation)
        self.animationTimer.start(300) #初始interval不影响动画播放

        # 设置初始状态为 sleep
        self.petSleep(direction=self.direction)

        # 设置窗口尺寸
        self.currentAnimation = self.imageCache[self.status]
        self.currentFrame = 0
        self.label.resize(self.currentAnimation[self.currentFrame].size())
        self.resize(self.currentAnimation[self.currentFrame].size())

        # 移动计数器和拖动初始化
        self.moveCounter = 0


        # 初始放在屏幕右边
        screen = QApplication.primaryScreen()
        screenGeometry = screen.geometry()
        self.move(screenGeometry.width() - self.width(), 300)
        self.dragPosition = QPoint()

    def flipImages(self):
        """翻转图片，模拟掉头效果"""
        flippedImages = []
        for img in self.currentAnimation:
            transform = QTransform().scale(-1, 1)  # 水平翻转
            flippedImg = img.transformed(transform)
            flippedImages.append(flippedImg)
        self.currentAnimation = flippedImages
        self.currentFrame = 0  # 重置帧数
        

    # Events
    def mousePressEvent(self, event):
        # 鼠标点击事件，触发petWalk
        if self.status == 'sleep':
            self.petWalk(self.direction, speed=5)
        self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        # 拖动窗口事件，触发petDrag
            if event.buttons() == Qt.LeftButton:
                #self.petDrag()
                self.move(event.globalPos() - self.dragPosition)
        # Status
    def petWalk(self, direction, speed):
        self.status = 'walk'
        self.direction = direction
        self.speed = speed

         # 加载图片并根据方向翻转
        self.currentAnimation = self.imageCache[self.status]
        if self.direction == 1:
            self.flipImages()

        # 初始化移动控制
        self.maxMoves = np.random.randint(50, 100)
        self.moveCounter = 0

        # 停止之前的移动定时器（如果存在）
        if hasattr(self, 'moveTimer') and self.moveTimer.isActive():
            self.moveTimer.stop()

        self.moveTimer = QTimer(self)

        def autoMove():
            self.moveCounter += 1

            if self.moveCounter >= self.maxMoves:
                self.moveTimer.stop()
                self.petSleep(direction=self.direction)
                return

            x = self.x()
            y = self.y()
            step = speed

            screenWidth = QApplication.primaryScreen().size().width()

            if self.direction == -1:
                new_x = x - step
                if new_x <= 0:
                    new_x = 0
                    self.direction = 1
                    self.flipImages()
            else:
                new_x = x + step
                if new_x + self.width() >= screenWidth:
                    new_x = screenWidth - self.width()
                    self.direction = -1
                    self.flipImages()

            self.move(new_x, y)

        self.moveTimer.timeout.connect(autoMove)
        self.moveTimer.start(10)
        return


    def petSleep(self, direction):
        self.status = 'sleep'
        self.currentAnimation = self.imageCache[self.status]
        self.direction = direction
        return
    def petDrag(self):
        return

    # Animation
    def updateAnimation(self):
        if not self.currentAnimation :
            return


        if self.status == 'sleep':
            self.animationTimer.start(300)
        elif self.status == 'walk':
            self.animationTimer.start(100)

        self.currentFrame = (self.currentFrame + 1) % len(self.currentAnimation)
        self.label.setPixmap(self.currentAnimation[self.currentFrame])






if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())