import math

import numpy as np
from scipy.spatial import KDTree


class VerletObject:

    def __init__(self, position=(0.0, 0.0, 0.0), radius=1, tag=0):
        self.pos_curr = np.array(position, dtype=np.float64)
        self.pos_old = np.array(position, dtype=np.float64)
        self.acceleration = np.zeros(3)
        self.radius = radius
        self.tag = tag  # 0=Free | 1=Rigid


class Link:

    def __init__(self, a, b, target):
        self.a = a
        self.b = b
        self.target = target

    def apply(self):
        disp = self.a.pos_curr - self.b.pos_curr
        dist = np.sqrt(disp.dot(disp))
        if dist != 0:
            n = disp / dist
            delta = self.target - dist
            percent = 0.5
            if self.a.tag == 1:
                percent = 0
            elif self.b.tag == 1:
                percent = 1
            if self.b.tag == 1 and self.a.tag == 1:
                return
            self.a.pos_curr += percent * delta * n
            self.b.pos_curr -= (1 - percent) * delta * n


class Solver:
    time_step = 0.0015
    sub_steps = 1

    # gravity = np.array([0.0, 0, 0.0])
    gravity = np.array([0.0, -1000, 0.0])  # -1000

    friction = -100

    grid_size = 10

    def __init__(self, container, verlet_objects=[]):
        self.container = container
        self.verlet_objects = verlet_objects
        self.links = []

    def update(self):
        sub_dt = Solver.time_step / Solver.sub_steps
        for step in range(Solver.sub_steps):
            self.apply_forces()
            # self.brute_collisions()
            if self.verlet_objects:
                self.kd_collisions()
            self.apply_constraints()
            self.update_positions(sub_dt)
            self.update_links()

    def update_positions(self, dt):
        for obj in self.verlet_objects:
            if obj.tag != 1:
                displacement = obj.pos_curr - obj.pos_old
                obj.pos_old = obj.pos_curr
                obj.pos_curr = obj.pos_curr + displacement + obj.acceleration * dt * dt
            obj.acceleration = np.zeros(3, dtype=np.float64)

    def apply_forces(self):
        for obj in self.verlet_objects:
            obj.acceleration += Solver.gravity
            disp = obj.pos_curr - obj.pos_old
            dist = np.sqrt(disp.dot(disp))
            if dist > 0:
                n = disp / dist
                obj.acceleration += n * Solver.friction

    def handle_collision(self, a, b):
        axis = a.pos_curr - b.pos_curr
        dist = np.sqrt(axis.dot(axis))
        if dist == 0:
            return
        if dist < a.radius + b.radius:
            n = axis / dist
            delta = a.radius + b.radius - dist
            a.pos_curr += 0.5 * delta * n
            b.pos_curr -= 0.5 * delta * n

    def brute_collisions(self):
        for a in self.verlet_objects:
            for b in self.verlet_objects:
                self.handle_collision(a, b)

    def kd_collisions(self):
        data = [obj.pos_curr for obj in self.verlet_objects]
        kd = KDTree(data)
        pairs = kd.query_pairs(r=0.4)
        for (i, j) in pairs:
            self.handle_collision(self.verlet_objects[i], self.verlet_objects[j])

    def apply_constraints(self):
        # Floor
        # for obj in self.verlet_objects:
        #     if obj.pos_curr[1] <= -2:
        #         displacement = obj.pos_curr[1] - obj.pos_old[1]
        #         obj.pos_curr[1] = -2
        #         obj.pos_old[1] = obj.pos_curr[1] + displacement

        # Circle (Convex)
        c_radius = self.container.scale
        c_position = self.container.position
        for obj in self.verlet_objects:
            disp = obj.pos_curr - c_position
            dist = np.sqrt(disp.dot(disp))
            if dist > c_radius - obj.radius:
                n = disp / dist
                obj.pos_curr = c_position + n * (c_radius - obj.radius)

        # Cube
        # for obj in self.verlet_objects:
        #     dim = 2.5 - obj.radius
        #
        #     for i in range(3):
        #         if obj.pos_curr[i] < -dim:
        #             disp = obj.pos_curr[i] - obj.pos_old[i]
        #             obj.pos_curr[i] = -dim
        #             obj.pos_old[i] = obj.pos_curr[i] + disp
        #         if obj.pos_curr[i] > dim:
        #             disp = obj.pos_curr[i] - obj.pos_old[i]
        #             obj.pos_curr[i] = dim
        #             obj.pos_old[i] = obj.pos_curr[i] + disp

    def update_links(self):
        for link in self.links:
            link.apply()

    def add_object(self, obj):
        self.verlet_objects.append(obj)

    def add_link(self, target, obj_a, obj_b):
        for link in self.links:
            if link.b is obj_a and link.a is obj_b:
                return
            if link.b is obj_b and link.a is obj_a:
                return
        link = Link(obj_a, obj_b, target)
        self.links.append(link)

    def expanding_force(self, center, strength):
        for obj in self.verlet_objects:
            disp = obj.pos_curr - center
            dist = np.sqrt(disp.dot(disp))
            if dist > 0:
                n = disp / dist
                obj.acceleration += n * strength


