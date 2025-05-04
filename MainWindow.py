from PySide6.QtWidgets import QWidget, QPushButton, QApplication
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QGuiApplication, QPixmap

import os

from DesktopPet import DesktopPet
from PoopWidget import PoopWidget
from PoopManager import PoopManager
from PetHouse import PetHouse
from Carpet import Carpet

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.fixedHeight = 150
        self.setupWindow()
        self.loadComponents()
        self.poopManager = PoopManager(self)
        
        self.addCloseButton()
        self.addClearPoopButton()
        
        queryTimer50ms = QTimer(self)
        queryTimer50ms.timeout.connect(self.query50ms)
        queryTimer50ms.start(50)

    def query50ms(self):
        if self.desktopPet.wantToPoop:
            self.poopManager.addPoop(
                self.desktopPet.x() + self.desktopPet.width() // 2,
                self.desktopPet.y() + self.desktopPet.height() // 2
            )
            self.desktopPet.wantToPoop = False



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
        self.petHouse = PetHouse(200, 230, x=self.width()-200, y=-10,parent=self)
        self.petHouse.show()
        self.petHouse.lower()  
        
        # 加载地毯
        self.carpet = Carpet(self.width(), 150, 0, 0, parent=self)
        self.carpet.lower()

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
        self.clearPoopBtn.move(10, 10)
  
    
    def addClearPoopButton(self):
        self.clearPoopBtn = QPushButton(self)
        poopManagerPath = os.path.join(os.path.dirname(__file__), 'pics', 'poopManager.png')
        poopManagerPixmap = QPixmap(poopManagerPath)

        if poopManagerPixmap.isNull():
            print(f"⚠️ 图片加载失败: {poopManagerPath}")
            self.clearPoopBtn.setText("🧹")
        else:
            self.clearPoopBtn.setIcon(poopManagerPixmap)
            self.clearPoopBtn.setIconSize(poopManagerPixmap.size())

        self.clearPoopBtn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 128, 0, 180);
            }
        """)
        self.clearPoopBtn.setFixedSize(30, 30)
        self.clearPoopBtn.move(10, 10)  # 左上角
        self.clearPoopBtn.raise_()
        self.clearPoopBtn.clicked.connect(self.poopManager.clearPoops)

        
        
    def clearPoops(self):
        for poop in self.poops:
            poop.deleteLater()
        self.poops.clear()
