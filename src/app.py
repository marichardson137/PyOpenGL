import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
# import OpenGL.GLUT as glut
import numpy as np
import pyrr

from src.graphics_api import draw_sphere
from src.model import Model, Texture, Mesh
from src.shader import Shader
from src.verlet import VerletObject, Solver


class Window:
    WIDTH = 900
    HEIGHT = 600

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

        self.solver = self.instantiate_verlets()
        self.sphere_mesh = Mesh("models/sphere.obj")


        self.setup_shader()
        self.run()

    def run(self):

        running = True
        while running:
            # Poll events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.shader.use()

            # Update the positions of all the balls
            self.solver.update(self.dt)

            # Render the balls
            for verlet in self.solver.verlet_objects:
                draw_sphere(self.sphere_mesh, self.modelMatrixLocation, verlet.pos_curr)

            pg.display.flip()

            # Timing
            self.dt = self.clock.tick(60)
            pg.display.set_caption(f'FPS: {int(self.clock.get_fps())} | MS: {self.dt}')

        self.quit()

    def quit(self):
        self.sphere_mesh.destroy()
        # self.texture.destroy()
        self.shader.destroy()
        pg.quit()

    def instantiate_verlets(self):
        verlets = []
        # for x in range(20):
        #     verlet = VerletObject(position=((x-10.0) / 2.0, x / 2, -10.0))
        #     verlets.append(verlet)
        verlets.append(VerletObject(position=(0, 0, -10)))
        return Solver(verlets)

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


if __name__ == '__main__':
    Window()
