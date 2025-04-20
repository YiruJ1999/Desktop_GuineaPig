import sys
import os
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        # 设置无边框 & 始终置顶 & 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 缩放比例
        self.scale_factor = 0.1

        # 默认状态：sleep
        self.status = 'sleep'
        self.pet_images = []
        self.loadImages(self.status)

        # 初始帧
        self.current_frame = 0

        # 显示 QLabel
        self.label = QLabel(self)
        self.label.setPixmap(self.pet_images[self.current_frame])
        self.label.resize(self.pet_images[self.current_frame].size())
        self.resize(self.pet_images[self.current_frame].size())

        # 定时器控制动画
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(300)  # sleep 动画速度稍慢

        # 拖动相关
        self.drag_position = QPoint()

    def loadImages(self, status):
        """根据状态加载不同的动画帧"""
        self.pet_images.clear()
        folder_path = f"./frames/{status}"
        if not os.path.exists(folder_path):
            print(f"Warning: Folder not found: {folder_path}")
            return

        # 加载图片
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
        if not self.pet_images:
            return
        self.current_frame = (self.current_frame + 1) % len(self.pet_images)
        self.label.setPixmap(self.pet_images[self.current_frame])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 切换状态：sleep → walk
            if self.status == 'sleep':
                self.status = 'walk'
                self.loadImages(self.status)
                self.current_frame = 0
                self.timer.setInterval(100)  # 走路动画更快
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
