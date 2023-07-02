import numpy as np


class VerletObject:

    def __init__(self, position=(0.0, 0.0, 0.0)):
        self.pos_curr = np.array(position)
        self.pos_old = np.array(position)
        self.acceleration = np.zeros(3)


class Solver:
    SLOW_FACTOR = 1/1000

    gravity = np.array([0.0, -9.8, 0.0])

    def __init__(self, verlet_objects):
        self.verlet_objects = verlet_objects

    def update(self, dt):
        dt = dt * Solver.SLOW_FACTOR
        print(dt)
        # ss = 5
        # sub_dt = dt / ss
        # for s in range(ss):
        self.apply_forces()
        self.apply_constraints()
        self.update_positions(0.017)

    def update_positions(self, dt):
        for obj in self.verlet_objects:
            displacement = obj.pos_curr - obj.pos_old
            obj.pos_old = obj.pos_curr
            obj.pos_curr = obj.pos_curr + displacement + obj.acceleration * dt * dt
            obj.acceleration = np.zeros(3, dtype=np.float64)



    def apply_forces(self,):
        for obj in self.verlet_objects:
            obj.acceleration += Solver.gravity

    def apply_constraints(self):
        for obj in self.verlet_objects:
            if obj.pos_curr[1] <= -3:
                obj.pos_old[1] = obj.pos_curr[1] + (obj.pos_curr[1] - obj.pos_old[1])

