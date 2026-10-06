# PoopManager.py
# 集中管理 poop 控件，提供生成与清除功能
from PySide6.QtCore import QTimer
from PoopWidget import PoopWidget

class PoopManager:
    def __init__(self, parentWidget, desktopPets):
        self.parent = parentWidget
        self.desktopPets = desktopPets
        self.poops = []

        # 启动定时器，每50ms检查一次
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkAndAddPoop)
        self.timer.start(50)

    def checkAndAddPoop(self):
        for pet in self.desktopPets:
            if not pet.wantToPoop:
                continue
            # 根据方向计算 poop 的 x 坐标
            if pet.direction == -1:
                # 向左走，poop 出现在右侧屁股后
                poop_x = pet.x() + pet.width() + 10
            else:
                # 向右走，poop 出现在左侧屁股后
                poop_x = pet.x()  - 10

            poop_y = pet.y() + pet.height() // 2

            self.addPoop(poop_x, poop_y)
            pet.wantToPoop = False

    def addPoop(self, x, y):
        poop = PoopWidget(self.parent, x, y)
        self.poops.append(poop)

    def clearPoops(self):
        for poop in self.poops:
            poop.deleteLater()
        self.poops.clear()
