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
        self.scale_factor = 0.1
        self.preloadImages()
        
        # 设定初始状态
        self.initState()
        
    def preloadImages(self):
        #预加载所有状态的图片并缓存到字典中
        self.image_cache = {}
        for status in self.allStatus:
            folder_path = f"./frames/{status}"
            images = []
            if os.path.exists(folder_path):
                for filename in sorted(os.listdir(folder_path)):
                    if filename.endswith(".png"):
                        pixmap = QPixmap(os.path.join(folder_path, filename))
                        if pixmap.isNull():
                            continue
                        scaled = pixmap.scaled(
                            pixmap.width() * self.scale_factor,
                            pixmap.height() * self.scale_factor,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        images.append(scaled)
            self.image_cache[status] = images

    def initState(self):
        # 初始状态：速度，睡觉，向左
        self.speed = 1
        self.direction = -1  # 提前设定方向
        
        # 初始化 label 和动画定时器
        self.label = QLabel(self)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.updateAnimation)

        # 设置初始状态为 sleep
        self.petSleep(direction=self.direction)

        # 设置窗口尺寸
        self.pet_images = self.image_cache[self.status]
        self.current_frame = 0
        self.label.resize(self.pet_images[self.current_frame].size())
        self.resize(self.pet_images[self.current_frame].size())
        
        # 动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.updateAnimation)
        self.animation_timer.start(300)

        # 移动计数器和拖动初始化
        self.move_counter = 0
        self.drag_position = QPoint()

        # 初始放在屏幕右边
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.move(screen_geometry.width() - self.width(), 300)
        
    
    def flipImages(self):
        """翻转图片，模拟掉头效果"""
        flipped_images = []
        for img in self.pet_images:
            transform = QTransform().scale(-1, 1)  # 水平翻转
            flipped_img = img.transformed(transform)
            flipped_images.append(flipped_img)
        self.pet_images = flipped_images
        self.current_frame = 0  # 重置帧数
        

    # Events
    def mousePressEvent(self, event):
        # 鼠标点击事件，触发petWalk
        if self.status == 'sleep':
            self.petWalk(self.direction, speed=5)
        self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        # 拖动窗口事件，触发petDrag
            if event.buttons() == Qt.LeftButton:
                self.petDrag()
                self.move(event.globalPos() - self.drag_position)
    # Status
    def petWalk(self, direction, speed):
        self.status = 'walk'
        self.direction = direction
        self.speed = speed

         # 加载图片并根据方向翻转
        self.pet_images = self.image_cache[self.status]
        if self.direction == 1:
            self.flipImages()

        self.current_frame = 0
        self.label.setPixmap(self.pet_images[self.current_frame])
        self.animation_timer.setInterval(speed)

        # 初始化移动控制
        self.max_moves = np.random.randint(50, 100)
        self.move_counter = 0

        # 停止之前的移动定时器（如果存在）
        if hasattr(self, 'move_timer') and self.move_timer.isActive():
            self.move_timer.stop()

        self.move_timer = QTimer(self)

        def autoMove():
            self.move_counter += 1

            if self.move_counter >= self.max_moves:
                self.move_timer.stop()
                self.petSleep(direction=self.direction)
                return

            x = self.x()
            y = self.y()
            step = speed

            screen_width = QApplication.primaryScreen().size().width()

            if self.direction == -1:
                new_x = x - step
                if new_x <= 0:
                    new_x = 0
                    self.direction = 1
                    self.flipImages()
            else:
                new_x = x + step
                if new_x + self.width() >= screen_width:
                    new_x = screen_width - self.width()
                    self.direction = -1
                    self.flipImages()

            self.move(new_x, y)

        self.move_timer.timeout.connect(autoMove)
        self.move_timer.start(10)
        return
        
    
    def petSleep(self, direction):
        self.status = 'sleep'
        self.direction = direction
        self.pet_images = self.image_cache[self.status]
        if self.direction == 1:
            self.flipImages()
        self.current_frame = 0
        self.label.setPixmap(self.pet_images[self.current_frame])
        self.animation_timer.setInterval(300)
        return
    def petDrag(self):
        return

    # Animation
    def updateAnimation(self):
        return





if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())