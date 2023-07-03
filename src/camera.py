import numpy as np
import pyrr
from OpenGL.GL import *


class Camera:

    def __init__(self, position=(0, 0, 0)):
        self.position = np.array(position, dtype=np.float64)
        self.yaw = -90
        self.pitch = 0
        self.update_vectors()

    def update_vectors(self):
        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.yaw)) * np.cos(np.deg2rad(self.pitch)),
                np.sin(np.deg2rad(self.pitch)),
                np.sin(np.deg2rad(self.yaw)) * np.cos(np.deg2rad(self.pitch))
            ]
        )
        self.forwards = self.forwards / np.linalg.norm(self.forwards)

        global_up = np.array([0, 1, 0])

        self.right = np.cross(self.forwards, global_up)
        self.right = self.right / np.linalg.norm(self.right)

        self.up = np.cross(self.right, self.forwards)
        self.up = self.up / np.linalg.norm(self.up)


    def update_view(self, viewMatrixLocation):
        self.update_vectors()
        view = pyrr.matrix44.create_look_at(
            eye=self.position,
            target=self.position + self.forwards,
            up=self.up,
            dtype=np.float32
        )
        glUniformMatrix4fv(viewMatrixLocation, 1, GL_FALSE, view)
