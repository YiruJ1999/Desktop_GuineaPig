from PySide6.QtWidgets import QWidget, QPushButton, QApplication
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QGuiApplication, QPixmap, QIcon
import math

import os

from DesktopPet import DesktopPet
from PoopWidget import PoopWidget
from PoopManager import PoopManager
from PetHouse import PetHouse
from Carpet import Carpet

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.groundHeight = 150  # 底部地面区域（地毯、猪窝、按钮）的高度
        # 每只荷兰猪的皮肤，None 为原版，'tricolor' 为白/黑/棕三色（左右花色不同）
        self.petSkins = [None, 'tricolor']
        self.setupWindow()
        self.loadComponents()

        self.poopManager = PoopManager(self, self.desktopPets)
        
        self.addCloseButton()
        self.addClearPoopButton()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerFcn)
        self.timer.start(50)

    def setupWindow(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 透明背景：完全透明的像素不会拦截鼠标，点击会穿透到下面的窗口
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 窗口覆盖整个屏幕（不含任务栏），这样宠物可以被拖到屏幕任意位置
        self.setGeometry(QGuiApplication.primaryScreen().availableGeometry())

    def groundTop(self):
        # 地面区域在窗口中的顶部 y 坐标
        return self.height() - self.groundHeight

    def loadComponents(self):
        # 加载荷兰猪
        self.desktopPets = []
        for i, skin in enumerate(self.petSkins):
            direction = -1 if i % 2 == 0 else 1
            pet = DesktopPet(self, direction=direction, skin=skin)
            pet.setFixedSize(pet.label.size())
            pet.raise_()
            self.desktopPets.append(pet)
        self.initPetPosition()
        
        #加载猪窝
        self.petHouse = PetHouse(200, 230, x=self.width()-200, y=self.groundTop()-10, parent=self)
        self.petHouse.show()
        self.petHouse.lower()  
        
        # 加载地毯
        carpetSize = 20
        numCarpet = self.width() // carpetSize + 1
        self.carpets = []
        for i in range (numCarpet):
            self.carpets.append(Carpet(carpetSize,carpetSize,x = i*carpetSize, y = self.groundTop() + 90, parent=self))
            self.carpets[i].show()
            self.carpets[i].lower()
    

    def initPetPosition(self):
        # 计算初始宠物生成位置，每只间隔开
        spacing = 200
        for i, pet in enumerate(self.desktopPets):
            new_x = 100 + i * spacing
            pet.move(new_x, pet.floorY)
        
      
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
        self.closeBtn.move(self.width() - 40, self.groundTop() + 10)
        self.closeBtn.raise_()  # 保证在 DesktopPet 上面
        self.closeBtn.clicked.connect(QApplication.quit)

    def resizeEvent(self, event):
        self.closeBtn.move(self.width() - 40, self.groundTop() + 10)
        # self.petHouse.move(self.width() - self.petHouse.width(), 0)
        self.clearPoopBtn.move(10, self.groundTop() + 10)
  
    
    def addClearPoopButton(self):
        self.clearPoopBtn = QPushButton(self)
        poopManagerPath = os.path.join(os.path.dirname(__file__), 'componentsPic', 'poopCleanBtn.png')
        poopManagerPixmap = QPixmap(poopManagerPath)

        if poopManagerPixmap.isNull():
            print(f"⚠️ 图片加载失败: {poopManagerPath}")
            self.clearPoopBtn.setText("🧹")
        else:
            maxSize = 60
            scaledPixmap = poopManagerPixmap.scaled(
                maxSize, maxSize,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.clearPoopBtn.setIcon(QIcon(scaledPixmap))
            self.clearPoopBtn.setIconSize(scaledPixmap.size())
            self.clearPoopBtn.setFixedSize(scaledPixmap.size())
            
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

        self.clearPoopBtn.move(10, self.groundTop() + 10)  # 地面区域左上角
        self.clearPoopBtn.raise_()
        self.clearPoopBtn.clicked.connect(self.poopManager.clearPoops)

    def timerFcn(self):
        # Pet压Carpet逻辑
        for carpet in self.carpets:
            direction = 0
            for pet in self.desktopPets:
                if pet.y() < pet.floorY - 30:  # 宠物在空中时不压地毯
                    continue
                if carpet.x() + carpet.width > pet.x() and carpet.x() < pet.x() + pet.width():
                    direction = pet.direction
                    break
            carpet.carpetMove(direction)
        
    def clearPoops(self):
        for poop in self.poops:
            poop.deleteLater()
        self.poops.clear()
