# PoopManager.py
# 集中管理 poop 控件，提供添加与清除功能

class PoopManager:
    def __init__(self, parentWidget):
        self.parent = parentWidget
        self.poops = []

    def addPoop(self, x, y):
        from PoopWidget import PoopWidget
        poop = PoopWidget(self.parent, x, y)
        self.poops.append(poop)

    def clearPoops(self):
        for poop in self.poops:
            poop.deleteLater()
        self.poops.clear()
