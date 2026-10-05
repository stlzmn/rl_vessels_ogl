import pyrr
import numpy as np
from geographic import GeoObject

class Entity:
    # __slots__ = 'position', 'eulers', 'scale'
    def __init__(self, position, eulers, scale=[1, 1, 1]):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)

    @property
    def model_transform(self):
        transform = pyrr.matrix44.create_identity(dtype=np.float32)
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_scale(self.scale, dtype=np.float32))
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_eulers(np.radians(self.eulers), dtype=np.float32))
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_translation(self.position, dtype=np.float32))
        return transform

class Camera(Entity):
    def __init__(self, position, eulers):
        super().__init__(position, eulers)

        self.l_up = np.array([0, 0, 1], dtype=np.float32)
        self.l_right = np.array([0, 1, 0], dtype=np.float32)
        self.l_forward = np.array([1, 0, 0], dtype=np.float32)

        self.up = np.array([0, 0, 1], dtype=np.float32)
        self.right = np.array([0, 1, 0], dtype=np.float32)
        self.forward = np.array([1, 0, 0], dtype=np.float32)

    def _vector_cross_prod(self):
        self.forward = np.array([
            np.cos(np.radians(self.eulers[2])) * np.cos(np.radians(self.eulers[1])),
            np.sin(np.radians(self.eulers[2])) * np.cos(np.radians(self.eulers[1])),
            np.sin(np.radians(self.eulers[1]))
        ], dtype=np.float32)
        self.right = pyrr.vector.normalise(np.cross(self.forward, self.l_up))
        self.up = pyrr.vector.normalise(np.cross(self.right, self.forward))

    def update(self):
        self._vector_cross_prod()

    @property
    def view_transform(self):
        return pyrr.matrix44.create_look_at(eye=self.position, target=self.position+self.forward, up=self.up, dtype=np.float32)
    
class EncChart(Entity, GeoObject):
    def __init__(self, position, eulers, scale=[1, 1, 1]):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.scale = np.array([10, 10, 1], dtype=np.float32)

class Vessel(Entity):
    @classmethod
    def create_from_ais_report(cls, report):
        pass

    def __init__(self, position, eulers):
        super().__init__(position, eulers)
        self.scale = [0.001, 0.001, 0.001]

    @property
    def model_transform(self):
        transform = pyrr.matrix44.create_identity(dtype=np.float32)
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_scale(self.scale, dtype=np.float32))
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_eulers(np.radians(self.eulers), dtype=np.float32))
        transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_translation(self.position, dtype=np.float32))
        return transform
    
    def update_transform(self, report):
        pass
     
    

