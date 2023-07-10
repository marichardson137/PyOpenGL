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
        pg.display.set_mode((Window.WIDTH, Window.HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

        self.clock = pg.time.Clock()
        self.dt = 17

        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Render settings
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        # glFrontFace(GL_CW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Outlines
        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

        self.font = pg.font.Font("assets/Monocode.ttf", 30)

        self.num_balls = 0
        self.container = Model("models/sphere.obj", position=(0, 0, 0), scale=4)
        # self.container = Model("models/cube.obj", position=(0, 0, 0), scale=5)
        self.container.render_method = GL_LINES

        self.solver = self.instantiate_verlets()
        self.sphere_mesh = Mesh("models/sphere.obj")

        self.camera = Camera(position=(0, 0, 10))

        self.setup_shader()
        self.run()

    def run(self):

        self.num_frames = 0

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
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

            # Update camera
            self.shader.use()
            self.camera.update_view(self.viewMatrixLocation)
            self.shader.detach()
            self.outline_shader.use()
            self.camera.update_view(self.viewMatrixLocationOutline)
            self.outline_shader.detach()

            # Update outline shader
            self.outline_shader.use()
            glUniform1f(self.outlineLocationOutline, 1.08)
            self.outline_shader.detach()

            # Render container
            glStencilFunc(GL_ALWAYS, 1, 0xFF)
            glStencilMask(0xFF)
            draw_mesh(self.shader, self.container.mesh, self.modelMatrixLocation, self.container.position,
                      scale=self.container.scale)

            glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
            glStencilMask(0x00)
            # glDisable(GL_DEPTH_TEST)

            draw_mesh(self.outline_shader, self.container.mesh, self.modelMatrixLocationOutline,
                      self.container.position, scale=self.container.scale)

            glStencilMask(0xFF)
            glStencilFunc(GL_ALWAYS, 0, 0xFF)
            # glEnable(GL_DEPTH_TEST)

            # Add balls to the simulation
            if self.num_frames >= 30:
                # x = np.cos(np.deg2rad(360 / 8 * self.num_balls))
                # y = np.sin(np.deg2rad(360 / 8 * self.num_balls))
                # self.solver.verlet_objects.append(VerletObject(position=(x * 3, 0, y * 3), radius=0.15))

                self.solver.verlet_objects.append(
                    VerletObject(position=(np.random.rand() * 2, 0, np.random.rand() * 2), radius=0.2))

                self.num_balls += 1
                self.num_frames = 0

            # Update the positions of all the balls
            self.solver.update()

            # Render the balls
            for verlet in self.solver.verlet_objects:
                draw_mesh(self.shader, self.sphere_mesh, self.modelMatrixLocation, verlet.pos_curr, scale=verlet.radius)

            # Unbind the VAO and detach the shader programs
            glBindVertexArray(0)

            pg.display.flip()

            # Timing
            self.dt = self.clock.tick(60)
            pg.display.set_caption(f'FPS: {int(self.clock.get_fps())}')
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
        self.modelMatrixLocationOutline = glGetUniformLocation(self.outline_shader.shader_id, "model")
        self.viewMatrixLocationOutline = glGetUniformLocation(self.outline_shader.shader_id, "view")
        self.outlineLocationOutline = glGetUniformLocation(self.outline_shader.shader_id, "outline")
        self.outline_shader.detach()


if __name__ == '__main__':
    Window()
