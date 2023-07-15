import numpy as np


class VerletObject:

    def __init__(self, position=(0.0, 0.0, 0.0), radius=1):
        self.pos_curr = np.array(position, dtype=np.float64)
        self.pos_old = np.array(position, dtype=np.float64)
        self.acceleration = np.zeros(3)
        self.radius = radius


class Link:

    def __init__(self, obj_1, obj_2, target):
        self.a = obj_1
        self.b = obj_2
        self.target = target

    def apply(self):
        disp = self.a.pos_curr - self.b.pos_curr
        dist = np.sqrt(disp.dot(disp))
        n = disp / dist
        delta = self.target - dist
        self.a.pos_curr += 0.5 * delta * n
        self.b.pos_curr -= 0.5 * delta * n


class Solver:
    time_step = 0.0015
    sub_steps = 1

    gravity = np.array([0.0, -1000, 0.0])
    friction = -40

    grid_size = 10

    def __init__(self, container, verlet_objects=[]):
        self.container = container
        self.verlet_objects = verlet_objects
        self.grid = np.empty((Solver.grid_size, Solver.grid_size, Solver.grid_size), dtype=object)
        self.grid.fill([])
        self.links = []

    def update(self):
        sub_dt = Solver.time_step / Solver.sub_steps
        for step in range(Solver.sub_steps):
            self.apply_forces()
            # self.update_grid()
            # self.evaluate_grid()
            self.brute_collisions()
            self.apply_constraints()
            self.update_positions(sub_dt)
            self.update_links()

    def update_grid(self):
        for x in range(Solver.grid_size):
            for y in range(Solver.grid_size):
                for z in range(Solver.grid_size):
                    self.grid[x][y][z] = []

        ran = 10
        for obj in self.verlet_objects:
            grid_x = int((obj.pos_curr[0] + ran / 2) / ran * Solver.grid_size)
            grid_y = int((obj.pos_curr[1] + ran / 2) / ran * Solver.grid_size)
            grid_z = int((obj.pos_curr[2] + ran / 2) / ran * Solver.grid_size)
            self.grid[grid_x][grid_y][grid_z].append(obj)

    def update_positions(self, dt):
        for obj in self.verlet_objects:
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

    def evaluate_grid(self):
        for x in range(1, Solver.grid_size - 1):
            for y in range(1, Solver.grid_size - 1):
                for z in range(1, Solver.grid_size - 1):
                    curr_cell = self.grid[x][y][z]
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            for dz in range(-1, 2):
                                other_cell = self.grid[x + dx][y + dy][z + dz]
                                self.check_cell_collisions(curr_cell, other_cell)

    def check_cell_collisions(self, c1, c2):
        for a in c1:
            for b in c2:
                if a is not b:
                    self.handle_collision(a, b)

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
        link = Link(obj_a, obj_b, target)
        self.links.append(link)
