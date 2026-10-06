import sys
import os

import numpy as np
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QWidget, QLabel

from PoopWidget import PoopWidget


class DesktopPet(QWidget):

    def __init__(self, parent=None, direction=-1):
        super().__init__(parent)
        self.initDirection = direction
        self.init()

    def init(self):
        
        # 所有状态
        self.allStatus = ['idle','sleep', 'walk', 'drag', 'fall', 'sleepwalk', 'walksleep','fallidle']
        self.animationInterval = {'idle':100, 
                                  'sleep':200,
                                    'walk':50, 
                                    'drag':100,
                                    'fall':50,
                                    'fallidle':100,
                                    'sleepwalk':100,
                                    'walksleep':100}
        # 缩放比例，预读取图片
        self.scaleFactor = 0.1
        self.preloadImages()
        # 设定初始状态
        self.initState()

    def preloadImages(self):

        self.scaleFactor = 0.1
        self.imageCache = {}

        for status in self.allStatus:
            folderPath = f"./frames/{status}"
            images_left = []
            images_right = []

            if os.path.exists(folderPath):
                for filename in sorted(os.listdir(folderPath)):
                    if filename.endswith(".png"):
                        pixmap = QPixmap(os.path.join(folderPath, filename))
                        if pixmap.isNull():
                            continue

                        # 缩放原图（向左）
                        scaled = pixmap.scaled(
                            pixmap.width() * self.scaleFactor,
                            pixmap.height() * self.scaleFactor,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        images_left.append(scaled)

                        # 水平翻转生成向右图片
                        flipped = scaled.transformed(QTransform().scale(-1, 1))
                        images_right.append(flipped)

            self.imageCache[f"{status}_l"] = images_left
            self.imageCache[f"{status}_r"] = images_right

    def loadImage(self):

        # 按照direction和status加载currentAnimation
        if self.direction < 0 :
            self.currentAnimation = self.imageCache[f"{self.status}_l"]
        else:
            self.currentAnimation = self.imageCache[f"{self.status}_r"]
        
        # 立即从头播放当前动画    
        self.currentFrame = 0    
        self.animationTimer.start()

    def initState(self):
        # 默认值
        self.defaultSpeed = 5

        # 初始状态：速度，睡觉，向左
        self.speed = self.defaultSpeed
        self.direction = self.initDirection  # 提前设定方向
        self.dragPosition = 0
        self.wantToPoop = False

        # 初始化 label 和动画定时器
        self.label = QLabel(self)
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.updateAnimation)
        self.animationTimer.start(300) #初始interval不影响动画播放

        # 设置初始状态为 idle
        self.petIdle()

        # 设置窗口尺寸
        self.loadImage()
        self.currentFrame = 0
        self.label.resize(self.currentAnimation[self.currentFrame].size())
        self.resize(self.currentAnimation[self.currentFrame].size())
        
        

        # 移动计数器和拖动初始化
        self.moveCounter = 0
        self.idleIntervalCounter = 0
        
        self.petOffsetY = int(self.height() * 0.4)  # 40% 为脚下空白区域
        
        # 定义小猪图片左上角的坐标范围
        self.ceilY = - self.petOffsetY
        self.floorY =  self.parent().height()-self.height()+ self.petOffsetY -10 #10为地毯厚度

    def flipImages(self):
        # 翻转图片，模拟掉头效果
        flippedImages = []
        for img in self.currentAnimation:
            transform = QTransform().scale(-1, 1)  # 水平翻转
            flippedImg = img.transformed(transform)
            flippedImages.append(flippedImg)
        self.currentAnimation = flippedImages
        self.currentFrame = 0  # 重置帧数

    # Events
    def mouseReleaseEvent(self, event):
        # 鼠标点击事件，触发petWalk
        if self.status == 'drag':
            #self.releaseMouse()
            self.petFall()
        elif self.status == 'sleep':
            self.petSleepWalk(self.direction, speed=5)
        elif self.status == 'idle':
            self.petWalk(self.direction, speed=5)


    def mousePressEvent(self, event):
        # 点击记录dragPosition
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            print("self.frameGeometry().topLeft()",self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        # 拖动窗口事件，触发petDrag
        if event.buttons() == Qt.LeftButton:
            if self.status != 'drag':
                self.petDrag()

            parentRect = self.parent().geometry()
            petWidth = self.width()
            petHeight = self.height() - self.petOffsetY

            # 鼠标相对于父窗口的坐标
            mouseX = event.globalPos().x()
            mouseY = event.globalPos().y()

            newX = mouseX - self.dragPosition.x()
            newY = mouseY - self.dragPosition.y()
            
            # 限制 X
            if newX < parentRect.left():
                newX = parentRect.left()
            elif newX + petWidth > parentRect.right():
                newX = parentRect.right() - petWidth

            # 限制 Y
            if newY < self.ceilY:
                newY = self.ceilY
            elif newY  > self.floorY:
                newY = self.floorY

            self.move(newX, newY)


    
    # Status
    def petWalk(self, direction, speed, nextStatus='idle'):
        self.status = 'walk'
        self.direction = direction
        self.speed = speed

        # 加载walk的图片
        self.loadImage()

        self.maxMoves = np.random.randint(50, 100)
        self.moveCounter = 0

        if hasattr(self, 'moveTimer') and self.moveTimer.isActive():
            self.moveTimer.stop()

        self.moveTimer = QTimer(self)

        def autoMove():
            self.moveCounter += 1

            if np.random.rand() < 0.05:  # 概率
                self.wantToPoop = True

            # 正常移动逻辑
            if self.moveCounter >= self.maxMoves:
                self.moveTimer.stop()
                self.petIdle()
                return

            x = self.x()
            y = self.y()
            step = speed

            screenWidth = QApplication.primaryScreen().size().width()

            if self.direction == -1:
                new_x = x - step
                if new_x < 0:
                    new_x = 0
                    self.petTurn()
            else:
                new_x = x + step
                if new_x + self.width() >= screenWidth:
                    new_x = screenWidth - self.width()
                    self.petTurn()

            self.move(new_x, y)

        self.moveTimer.timeout.connect(autoMove)
        self.moveTimer.start(10)

    def petWalkSleep(self,direction):
        self.status = 'walksleep'
        # 加载图片
        self.loadImage()

        self.currentFrame = 0

    def petSleepWalk(self,direction,speed):
        self.status = 'sleepwalk'
        self.speed = speed
        # 加载图片
        self.loadImage()
        self.currentFrame = 0

    def petSleep(self):
        self.status = 'sleep'
        # 加载图片
        self.loadImage()


    def petDrag(self):
        self.status = 'drag'
        # 加载图片
        self.loadImage()
        return

    def petIdle(self):
        self.status = 'idle'
        self.animationTimer.start()
        self.loadImage()
        # idle 计时
        idleTimerInterval = 10 # milisecond
        idleTimeMax = np.random.randint(500,1000)
        idleIntervalMax = idleTimeMax / idleTimerInterval
        
        def callbackIdleTimer():
            self.idleIntervalCounter = self.idleIntervalCounter + 1
            if self.idleIntervalCounter > idleIntervalMax:
                self.petWalkSleep(direction=self.direction)
                self.idleIntervalCounter = 0
                idleTimer.stop()

        idleTimer = QTimer()
        idleTimer.timeout.connect(callbackIdleTimer)
        idleTimer.start(idleTimerInterval)

    def petFall(self):

        self.status = 'fall'
        self.loadImage()

        # 自由落体参数
        self.fallSpeed = 0
        self.gravity = 1.2
        self.maxFallSpeed = 5

        # 屏幕底部位置
               
        self.hasLanded = False

        if hasattr(self, 'fallTimer') and self.fallTimer.isActive():
            self.fallTimer.stop()

        self.fallTimer = QTimer(self)

        def fallStep():
            if self.hasLanded:
                return
            
            self.fallSpeed = min(self.fallSpeed + self.gravity, self.maxFallSpeed)
            new_y = self.y() + self.fallSpeed

            if new_y >= self.floorY: #提早开始进入衔接动画，但是移动继续
                
                new_y = self.floorY
                self.move(self.x(), new_y)
                self.hasLanded = True
                self.fallSpeed = 0 
                self.fallTimer.stop()

            elif new_y >= self.floorY-30 and self.status != 'fallidle':
                self.petFallIdle()   
                self.move(self.x(), new_y)
            else:
                self.move(self.x(), new_y)
            
        self.fallTimer.timeout.connect(fallStep)
        self.fallTimer.start(30)

    def petFallIdle(self):
        self.status = 'fallidle'

        self.loadImage()


    # 未分类


    def petTurn(self):
        self.flipImages()
        self.animationTimer.start(1)
        self.direction = -self.direction

    # Animation
    def updateAnimation(self):
        if not self.currentAnimation:
            return
        if self.status != 'fall':
            self.animationTimer.start(self.animationInterval.get(self.status, 100))
        self.currentFrame = (self.currentFrame + 1) % len(self.currentAnimation)
        self.label.setPixmap(self.currentAnimation[self.currentFrame])

        if self.currentFrame + 1 >= len(self.currentAnimation):
            self.currentFrame = 0
            self.onAnimationFinished()


    def onAnimationFinished(self):
        if self.status == 'sleepwalk':
            self.petWalk(self.direction, self.speed)
        elif self.status == 'walksleep':
            self.petSleep()
        elif self.status == 'fallidle':
            self.petIdle()
        elif self.status == 'poop':
            self.petWalk(self.direction, self.speed)



