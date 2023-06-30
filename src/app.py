import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
# import OpenGL.GLUT as glut
import numpy as np
import pyrr

from src.model import Model, Material


class Window:

    def __init__(self):

        self.WIDTH = 900
        self.HEIGHT = 600

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_caption("ball simulation")

        self.clock = pg.time.Clock()

        glClearColor(0.1, 0.1, 0.1, 1.0)

        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        # glFrontFace(GL_CW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.models = None
        self.shader = None
        self.modelMatrixLocation = None

        self.instantiate_models()
        self.setup_shader()

        self.run()

    def create_shader(self, vertex_filepath, fragment_filepath):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader

    def run(self):

        running = True
        while running:
            # Poll events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)

            # Update and draw models
            for model in self.models:
                model.rotation[2] += 0.5
                model.update_transformation()
                model.draw(self.modelMatrixLocation)

            pg.display.flip()

            # Timing
            self.clock.tick(60)

        self.quit()

    def quit(self):
        for model in self.models:
            model.destroy()
        # self.texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

    def instantiate_models(self):
        self.models = []
        for x in range(5):
            sphere = Model("models/sphere.obj", position=[x-2, 0, -5])
            self.models.append(sphere)

    def setup_shader(self):
        self.shader = self.create_shader("shaders/phong_vertex.glsl", "shaders/phong_fragment.glsl")
        glUseProgram(self.shader)

        # glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        # self.texture = Material("textures/leet.png")

        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=self.WIDTH / self.HEIGHT,
            near=0.1, far=100, dtype=np.float32
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")


if __name__ == '__main__':
    Window()
