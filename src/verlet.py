import numpy as np


class VerletObject:

    gravity = np.array([0.0, -9.8, 0.0])

    def __init__(self, model, position=(0.0, 0.0, 0.0), velocity=(0.0, 0.0, 0.0)):
        self.model = model
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.acceleration = np.zeros(3)

    def update(self, dt):
        new_position = self.position + self.velocity * dt + 0.5 * self.acceleration * dt * dt
        new_acceleration = self.apply_forces()
        new_velocity = self.velocity + 0.5 * (self.acceleration + new_acceleration) * dt

        self.position = new_position
        self.velocity = new_velocity
        self.acceleration = new_acceleration

        self.apply_constraints()

        self.model.position = self.position

    def apply_constraints(self):
        if self.position[1] <= -2.5:
            self.acceleration = np.zeros(3)
            self.velocity = np.array([0.0, 5.0, 0.0])

    def apply_forces(self):
        return VerletObject.gravity
