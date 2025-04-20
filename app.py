import sys
import os
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

        self.scale_factor = 0.1

        # 默认状态是 sleep
        self.status = 'sleep'
        self.pet_images = []
        self.loadImages(self.status)

        self.current_frame = 0

        self.label = QLabel(self)
        self.label.setPixmap(self.pet_images[self.current_frame])
        self.label.resize(self.pet_images[self.current_frame].size())
        self.resize(self.pet_images[self.current_frame].size())

        # 动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.updateAnimation)
        self.animation_timer.start(300)  # 睡觉动画速度

        # 移动定时器
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.autoMove)

        # 初始放在屏幕右边
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.move(screen_geometry.width() - self.width(), 300)

        self.drag_position = QPoint()

        # 初始方向：向左走
        self.direction = 'left'

    def loadImages(self, status):
        """加载指定状态的图片"""
        self.pet_images.clear()
        folder_path = f"./frames/{status}"
        if not os.path.exists(folder_path):
            print(f"Warning: Folder not found: {folder_path}")
            return

        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                pixmap = QPixmap(os.path.join(folder_path, filename))
                if pixmap.isNull():
                    print(f"Warning: Failed to load {filename}")
                    continue
                scaled = pixmap.scaled(
                    pixmap.width() * self.scale_factor,
                    pixmap.height() * self.scale_factor,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.pet_images.append(scaled)

    def updateAnimation(self):
        """更新当前的动画帧"""
        if not self.pet_images:
            return
        self.current_frame = (self.current_frame + 1) % len(self.pet_images)
        self.label.setPixmap(self.pet_images[self.current_frame])

    def autoMove(self):
        """控制宠物移动"""
        x = self.x()
        y = self.y()
        step = 5

        screen_width = QApplication.primaryScreen().size().width()

        if self.direction == 'left':
            new_x = x - step
            if new_x <= 0:
                new_x = 0
                self.direction = 'right'
                self.flipImages()  # 翻转图片，改变方向
        else:
            new_x = x + step
            if new_x + self.width() >= screen_width:
                new_x = screen_width - self.width()
                self.direction = 'left'
                self.flipImages()  # 翻转图片，改变方向

        self.move(new_x, y)

    def flipImages(self):
        """翻转图片，模拟掉头效果"""
        flipped_images = []
        for img in self.pet_images:
            transform = QTransform().scale(-1, 1)  # 水平翻转
            flipped_img = img.transformed(transform)
            flipped_images.append(flipped_img)
        self.pet_images = flipped_images
        self.current_frame = 0  # 重置帧数

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            if self.status == 'sleep':
                # 切换为 walk
                self.status = 'walk'
                self.loadImages(self.status)
                self.current_frame = 0

                # 加快动画
                self.animation_timer.setInterval(100)

                # 启动移动
                self.move_timer.start(50)

                # 初始向左走
                self.direction = 'left'

            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """拖动窗口事件"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
