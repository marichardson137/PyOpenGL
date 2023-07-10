import time

import pygame as pg
from OpenGL.GL import *
# import OpenGL.GLUT as glut
import numpy as np
import pyrr

from src.camera import Camera
from src.graphics_api import draw_mesh
from src.model import Model, Texture, Mesh
from src.shader import Shader
from src.verlet import VerletObject, Solver


class Window:
    WIDTH = 1400
    HEIGHT = 900

    GLOBAL_X = np.array([1, 0, 0], dtype=np.float64)
    GLOBAL_Y = np.array([0, 1, 0], dtype=np.float64)
    GLOBAL_Z = np.array([0, 0, 1], dtype=np.float64)

    def __init__(self):

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_STENCIL_SIZE, 8)
        pg.display.set_mode((Window.WIDTH, Window.HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

        self.clock = pg.time.Clock()
        self.dt = 17

        glClearColor(0.08, 0.08, 0.08, 1.0)
        glClearStencil(0)

        # Render settings
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glPointSize(2.0)

        # glEnable(GL_STENCIL_TEST)
        # glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
        # glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)


        self.font = pg.font.Font("assets/Monocode.ttf", 30)

        self.num_balls = 0
        self.container = Model("models/sphere.obj", position=(0, 0, 0), scale=4)
        # self.container = Model("models/cube.obj", position=(0, 0, 0), scale=5)

        self.solver = self.instantiate_verlets()
        self.sphere_mesh = Mesh("models/ico_sphere.obj")

        self.camera_radius = 12
        self.camera_speed = 8
        self.camera = Camera(position=(0, 0, self.camera_radius))
        self.fix_camera = True

        self.setup_shader()
        self.run()

    def run(self):

        self.num_frames = 0
        self.global_time = time.time()

        running = True
        while running:
            self.global_time = time.time()

            # Poll events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            if pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False

            # Handle input
            if self.fix_camera:
                self.animate_camera()
            else:
                self.handle_keyboard()
                self.handle_mouse()

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

            # Update camera
            self.shader.use()
            self.camera.update_view(self.viewMatrixLocation)
            self.shader.detach()
            self.outline_shader.use()
            self.camera.update_view(self.viewMatrixLocationOutline)
            self.outline_shader.detach()

            # Render container
            draw_mesh(self.outline_shader, self.container.mesh, self.modelMatrixLocationOutline,
                      self.container.position, scale=self.container.scale, method=GL_POINTS)

            # Add balls to the simulation
            if self.num_frames >= 15:
                x = np.cos(np.deg2rad(360 * np.random.rand()))
                y = np.sin(np.deg2rad(360 * np.random.rand()))
                self.solver.verlet_objects.append(VerletObject(position=(x * 2.5, 0, y * 2.5), radius=0.15))

                self.num_balls += 1
                self.num_frames = 0

            # Update the positions of all the balls
            self.solver.update()

            # Render the balls
            for verlet in self.solver.verlet_objects:
                draw_mesh(self.shader, self.sphere_mesh, self.modelMatrixLocation, verlet.pos_curr, scale=verlet.radius)

            pg.display.flip()

            # Timing
            self.dt = self.clock.tick(60)
            pg.display.set_caption(f'FPS: {int(self.clock.get_fps())} | Balls: {self.num_balls}')
            self.num_frames += 1

        self.quit()

    def handle_keyboard(self):
        keys = pg.key.get_pressed()

        speed = 0.05
        if keys[pg.K_w]:
            self.camera.position += self.camera.forwards * speed
        if keys[pg.K_a]:
            self.camera.position -= self.camera.right * speed
        if keys[pg.K_s]:
            self.camera.position -= self.camera.forwards * speed
        if keys[pg.K_d]:
            self.camera.position += self.camera.right * speed
        if keys[pg.K_q]:
            self.camera.position += self.camera.up * speed
        if keys[pg.K_e]:
            self.camera.position -= self.camera.up * speed

    def handle_mouse(self):
        (dx, dy) = pg.mouse.get_rel()
        dx *= 0.1
        dy *= 0.1
        self.camera.yaw += dx
        self.camera.pitch -= dy
        if self.camera.pitch > 89:
            self.camera.pitch = 89
        if self.camera.pitch < -89:
            self.camera.pitch = -89
        pg.mouse.set_pos(Window.WIDTH / 2, Window.HEIGHT / 2)
        pg.mouse.set_visible(False)

    def quit(self):
        self.sphere_mesh.destroy()
        # self.texture.destroy()
        self.shader.destroy()
        self.outline_shader.destroy()
        pg.quit()

    def instantiate_verlets(self):
        verlets = []
        for v in range(self.num_balls):
            x = np.cos(np.deg2rad(360 / self.num_balls * v))
            y = np.sin(np.deg2rad(360 / self.num_balls * v))
            verlet = VerletObject(position=(x * 3, 0, y * 3), radius=0.10)
            verlets.append(verlet)
        return Solver(self.container)

    def setup_shader(self):
        self.shader = Shader("shaders/phong_vertex.glsl", "shaders/phong_fragment.glsl")
        self.shader.use()

        # glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        # self.texture = Material("textures/leet.png")

        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=Window.WIDTH / Window.HEIGHT,
            near=0.1, far=100, dtype=np.float32
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader.shader_id, "projection"),
            1, GL_FALSE, projection
        )
        self.modelMatrixLocation = glGetUniformLocation(self.shader.shader_id, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader.shader_id, "view")
        self.shader.detach()

        # Outline shader
        self.outline_shader = Shader("shaders/outline_vertex.glsl", "shaders/outline_fragment.glsl")
        self.outline_shader.use()
        glUniformMatrix4fv(
            glGetUniformLocation(self.outline_shader.shader_id, "projection"),
            1, GL_FALSE, projection
        )
        glUniform1f(glGetUniformLocation(self.outline_shader.shader_id, "outline"), 0.00)
        self.modelMatrixLocationOutline = glGetUniformLocation(self.outline_shader.shader_id, "model")
        self.viewMatrixLocationOutline = glGetUniformLocation(self.outline_shader.shader_id, "view")
        self.outline_shader.detach()

    def animate_camera(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.camera_radius -= 0.1
        if keys[pg.K_s]:
            self.camera_radius += 0.1

        x = np.cos(np.deg2rad(self.global_time * self.camera_speed))
        z = np.sin(np.deg2rad(self.global_time * self.camera_speed))
        self.camera.position[0] = x * self.camera_radius
        self.camera.position[2] = z * self.camera_radius
        self.camera.yaw = self.global_time * self.camera_speed + 180

        # height = 3
        # oscillation_speed = 10
        # y = np.cos(np.deg2rad(self.global_time * oscillation_speed))
        # self.camera.position[1] = y * height
        # self.camera.pitch = -y * oscillation_speed / height


if __name__ == '__main__':
    Window()
