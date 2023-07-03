import pygame as pg
from OpenGL.GL import *
# import OpenGL.GLUT as glut
import numpy as np
import pyrr

from src.camera import Camera
from src.graphics_api import draw_sphere
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
        pg.display.set_mode((Window.WIDTH, Window.HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

        self.clock = pg.time.Clock()
        self.dt = 17

        glClearColor(0.1, 0.1, 0.1, 1.0)

        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        # glFrontFace(GL_CW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.ball_count = 0
        self.font = pg.font.Font("assets/Monocode.ttf", 30)

        self.container = Model("models/sphere.obj", position=(0, 0, 0), scale=4)
        self.container.render_method = GL_LINES

        self.solver = self.instantiate_verlets()
        self.sphere_mesh = Mesh("models/sphere.obj")

        self.camera = Camera(position=(0, 0, 10))

        self.setup_shader()
        self.run()

    def run(self):

        running = True
        while running:

            # Poll events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            if pg.key.get_pressed()[pg.K_ESCAPE]:
                running = False

            # Handle input
            self.handle_keyboard()
            self.handle_mouse()

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Load shader
            self.shader.use()

            # Update camera
            self.camera.update_view(self.viewMatrixLocation)

            # Update the positions of all the balls
            self.solver.update()

            # Render the balls
            for verlet in self.solver.verlet_objects:
                draw_sphere(self.sphere_mesh, self.modelMatrixLocation, verlet.pos_curr, scale=verlet.radius)

            # Render container
            self.container.render(self.modelMatrixLocation)

            pg.display.flip()

            # Timing
            self.dt = self.clock.tick(60)
            pg.display.set_caption(f'FPS: {int(self.clock.get_fps())}')

        self.quit()

    def handle_keyboard(self):
        keys = pg.key.get_pressed()

        speed = 0.1
        if keys[pg.K_w]:
            self.camera.position += self.camera.forwards * speed
        if keys[pg.K_a]:
            self.camera.position -= self.camera.right * speed
        if keys[pg.K_s]:
            self.camera.position -= self.camera.forwards * speed
        if keys[pg.K_d]:
            self.camera.position += self.camera.right * speed


    def handle_mouse(self):
        (dx, dy) = pg.mouse.get_rel()
        dx *= 0.2
        dy *= 0.2
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
        pg.quit()

    def instantiate_verlets(self):
        verlets = []
        for x in range(5):
            verlet = VerletObject(position=((x - 5) / 2.0, x / 10, (x - 5) / 5), radius=0.5)
            verlets.append(verlet)
        return Solver(verlets, self.container)

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


if __name__ == '__main__':
    Window()
