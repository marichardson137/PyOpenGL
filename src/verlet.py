import numpy as np


class VerletObject:

    def __init__(self, position=(0.0, 0.0, 0.0), radius=1):
        self.pos_curr = np.array(position, dtype=np.float64)
        self.pos_old = np.array(position, dtype=np.float64)
        self.acceleration = np.zeros(3)
        self.radius = radius


class Solver:
    time_step = 0.0015
    sub_steps = 2

    gravity = np.array([0.0, -1000, 0.0])
    damping = 0.8

    def __init__(self, container, verlet_objects=[]):
        self.container = container
        self.verlet_objects = verlet_objects

    def update(self):
        sub_dt = Solver.time_step / Solver.sub_steps
        for step in range(Solver.sub_steps):
            self.apply_forces()
            self.check_collisions()
            self.apply_constraints()
            self.update_positions(sub_dt)

    def update_positions(self, dt):
        for obj in self.verlet_objects:
            displacement = obj.pos_curr - obj.pos_old
            obj.pos_old = obj.pos_curr
            obj.pos_curr = obj.pos_curr + displacement + obj.acceleration * dt * dt
            obj.acceleration = np.zeros(3, dtype=np.float64)



    def apply_forces(self,):
        for obj in self.verlet_objects:
            obj.acceleration += Solver.gravity

    def check_collisions(self):
        for a in self.verlet_objects:
            for b in self.verlet_objects:
                axis = a.pos_curr - b.pos_curr
                dist = np.sqrt(axis.dot(axis))
                if dist == 0:
                    continue
                if dist < a.radius + b.radius:
                    n = axis / dist
                    delta = a.radius + b.radius - dist
                    a.pos_curr += 0.5 * delta * n
                    b.pos_curr -= 0.5 * delta * n


    def apply_constraints(self):
        # Floor
        # for obj in self.verlet_objects:
        #     if obj.pos_curr[1] <= -2:
        #         displacement = obj.pos_curr[1] - obj.pos_old[1]
        #         obj.pos_curr[1] = -2
        #         obj.pos_old[1] = obj.pos_curr[1] + displacement

        c_radius = self.container.scale[0]
        c_position = self.container.position

        # Circle (Convex)
        for obj in self.verlet_objects:
            disp = obj.pos_curr - c_position
            dist = np.sqrt(disp.dot(disp))
            if dist > c_radius - obj.radius:
                n = disp / dist
                obj.pos_curr = c_position + n * (c_radius - obj.radius)
