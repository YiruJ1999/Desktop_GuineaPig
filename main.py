from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QGuiApplication
from DesktopPet import DesktopPet

import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.fixedHeight = 150
        self.setupWindow()
        self.loadComponents()
        self.addCloseButton()

    def setupWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setFixedHeight(self.fixedHeight)

        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        self.setGeometry(0, screen_height - self.fixedHeight - 30, screen_width, self.fixedHeight)

    def loadComponents(self):
        # 只给 DesktopPet 用 layout
        self.desktopPet = DesktopPet(self)
        self.desktopPet.setFixedSize(self.desktopPet.label.size())
        self.desktopPet.raise_() 
        self.initPetPosition() 
        
    def initPetPosition(self):
        pet_width = self.desktopPet.width()
        pet_height = self.desktopPet.height()
        window_width = self.width()
        window_height = self.height()
        # 计算初始宠物生成位置
        new_x = (window_width - pet_width) // 1
        new_y = 0
        self.desktopPet.move(new_x, new_y)
        
    def addCloseButton(self):
        # 不放入 layout，而是手动放置
        self.closeBtn = QPushButton("❌", self)
        self.closeBtn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border: none;
                font-size: 16px;
                border-radius: 8px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 180);
                color: white;
            }
        """)
        self.closeBtn.setFixedSize(30, 30)
        self.closeBtn.move(self.width() - 40, 10)
        self.closeBtn.raise_()  # 保证在 DesktopPet 上面
        self.closeBtn.clicked.connect(QApplication.quit)

    def resizeEvent(self, event):
        self.closeBtn.move(self.width() - 40, 10)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
