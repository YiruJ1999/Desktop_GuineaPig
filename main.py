from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QRect, QTimer, QPoint
from PySide6.QtGui import QGuiApplication
from DesktopPet import DesktopPet
from PetHouse import PetHouse
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.fixedHeight = 150
        self.setupWindow()
        self.loadComponents()
        self.addCloseButton()
        self.startCollisionDetection()

    def setupWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setFixedHeight(self.fixedHeight)

        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        self.setGeometry(0, screen_height - self.fixedHeight - 30, screen_width, self.fixedHeight)

    def loadComponents(self):
        # 加载荷兰猪
        self.desktopPet = DesktopPet(self)
        self.desktopPet.setFixedSize(self.desktopPet.label.size())
        self.desktopPet.raise_() 
        self.initPetPosition() 
        
        #加载猪窝
        self.petHouse = PetHouse(200, 150, x=self.width()-200, y=0,parent=self)
        self.petHouse.show()
        self.petHouse.lower()  # 房子放在Pet下面（因为Pet要部分在房子后面）
        
    def initPetPosition(self):
        pet_width = self.desktopPet.width()
        pet_height = self.desktopPet.height()
        window_width = self.width()
        window_height = self.height()
        # 计算初始宠物生成位置
        new_x = 100
        new_y = 0
        self.desktopPet.move(new_x, new_y)
        
        
    def startCollisionDetection(self):
        # 创建一个定时器，每50ms检测一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkCollision)
        self.timer.start(50)

    def checkCollision(self):
        petPos = self.desktopPet.pos()
        petSize = self.desktopPet.width()  # 假设宽高一样
        petRect = QRect(petPos.x(), petPos.y(), petSize, petSize)
        houseRect = self.petHouse.geometry()

        if petRect.intersects(houseRect):
            self.desktopPet.petSleep()    
        
        
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
        # self.petHouse.move(self.width() - self.petHouse.width(), 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
