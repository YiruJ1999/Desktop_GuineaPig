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

    # Events
    def mousePressEvent(self, event):

       if self.status == 'sleep':
           self.petWalk(self,direction,speed)

    def mouseMoveEvent(self, event):
            """拖动窗口事件"""
            if event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)

    # Status
    def petWalk(self,direction,speed):
        return
    def petSleep(self,direction):
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