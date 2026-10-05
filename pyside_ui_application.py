import sys
from PySide2 import QtCore, QtWidgets, QtOpenGL, QtGui
from OpenGL.GL import *
import PySide2.QtGui

from renderer import GraphicEngine
from scene import Scene

import numpy as np

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_x = 0
        self._last_y = 0

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.NoButton:
                pos = event.pos()
                print(pos)
            else:
                pass
        return QtGui.QMainWindow.eventFilter(self, source, event)


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self._spin_camera(event.x(), event.y())
            self._last_x = event.x()
            self._last_y = event.y()

    def mouseReleaseEvent(self, event):
        pass

    def _spin_camera(self, x, y):
        ''''''
        rate = 1000 / 16.667
        theta_inc = rate * (1920 / 2 - x)
        phi_inc = rate * (1080 / 2 - y)
        eulers = np.array([0, phi_inc, theta_inc], dtype=np.float32)
        self.scene.spin_camera(eulers)

    def mouseMoveEvent(self, event):
        dx = event.x() - self._last_x
        dy = event.y() - self._last_y

        dfact = 0.005
        rate = 1000 / 16.667

        dpos = dfact * rate * np.array([dx / 10, -dy / 10, 0], dtype=np.float32)
        self.scene.move_camera(dpos)

        self._last_x = event.x()
        self._last_y = event.y()

        self.updateGL()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        sensitivity = 0.01
        zoom = delta * sensitivity

        dfact = 0.005
        rate = 1000 / 16.667
        dpos = dfact * rate * np.array([0, 0, -zoom], dtype=np.float32)
        self.scene.move_camera(dpos)
        self.updateGL()
    
    def initializeGL(self):
        """Set up the rendering context, define display lists etc."""
        glEnable(GL_PROGRAM_POINT_SIZE)
        glClearColor(0.1, 0.1, 0.2, 1.0)

        self.graphic_eng = GraphicEngine()
        self.scene = Scene()

    def paintGL(self):
        """draw the scene:"""
        self.scene.update(1000 / 16.667)
        self.graphic_eng.render(self.scene)

    def resizeGL(self, width, height):
        """setup viewport"""
        glViewport(0, 0, 1920, 1080)

    def free_resources(self):
        """Helper to clean up resources."""
        self.graphic_eng.terminate()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1920, 1080)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.glWidget = GLWidget()
        self.glWidgetArea = QtWidgets.QScrollArea()
        self.glWidgetArea.setWidget(self.glWidget)
        self.glWidgetArea.setWidgetResizable(True)
        self.glWidgetArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.glWidgetArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.glWidgetArea.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.glWidgetArea.setMinimumSize(50, 50)

        central_layout = QtWidgets.QVBoxLayout()
        central_layout.addWidget(self.glWidgetArea)
        central_widget.setLayout(central_layout)

        button_insert = QtWidgets.QPushButton('Klikaj')
        central_layout.addWidget(button_insert)
        button_insert.clicked.connect(self._button_clicked)

        self.setWindowTitle("Hello OpenGL")
        self.resize(1920, 1080)

    def _button_clicked(self):
        print('kurwa a co')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    res = app.exec_()
    mainWin.glWidget.free_resources()
    sys.exit(res)


from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
