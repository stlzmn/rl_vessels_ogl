from entity import Camera, EncChart, Vessel
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import numpy as np
import pyrr

class Scene:
    def __init__(self):
        self.fovy = 45
        self._init_actors()

    @property
    def projection_transform(self):
        return pyrr.matrix44.create_perspective_projection(fovy=self.fovy, aspect=SCREEN_WIDTH/SCREEN_HEIGHT, near=0.02, far=1000, dtype=np.float32)
    
    def _init_actors(self):
        self.camera = Camera(position=[0, 0, 10], eulers=[0, -89, 270])
        self.chart = EncChart(position=[0, 0, 0], eulers=[90, 90, 90])
        self.own_ship = Vessel(position=[0, 0, 0], eulers=[0, 0, 0])
        self.target_ships = dict()

    def update(self, rate):
        self.camera.update()

    def move_camera(self, dpos):
        self.camera.position += dpos
    
    def spin_camera(self, deulers):
        self.camera.eulers += deulers

        if self.camera.eulers[2] < 0:
            self.camera.eulers[2] += 360
        elif self.camera.eulers[2] > 360:
            self.camera.eulers[2] -= 360
        self.camera.eulers[1] = min(89, max(-89, self.camera.eulers[1]))