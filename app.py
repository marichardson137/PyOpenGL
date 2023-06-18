import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
# import OpenGL.GLUT as glut
import numpy as np
import pyrr


class Cube:

    def __init__(self, position, rotations):
        self.position = np.array(position, dtype=np.float32)
        self.rotations = np.array(rotations, dtype=np.float32)


class App:

    def __init__(self):

        self.WIDTH = 900
        self.HEIGHT = 600

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

        self.clock = pg.time.Clock()

        glClearColor(0.1, 0.1, 0.1, 1.0)

        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        # glFrontFace(GL_CW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.cube = Cube(
            position=[0, 0, -10],
            rotations=[0, 0, 0]
        )

        self.cube_mesh = Mesh("models/monkey.obj")

        self.shader = self.create_shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        glUseProgram(self.shader)

        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.texture = Material("textures/leet.png")

        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=self.WIDTH / self.HEIGHT,
            near=0.1, far=100, dtype=np.float32
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

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

            # Update cube

            self.cube.rotations[2] += 0.5

            model = pyrr.matrix44.create_identity(dtype=np.float32)
            model = pyrr.matrix44.multiply(
                m1=model,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.rotations),
                    dtype=np.float32
                )
            )
            model = pyrr.matrix44.multiply(
                m1=model,
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(self.cube.position),
                    dtype=np.float32
                )
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model)
            self.texture.use()
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_LINES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()

            # Timing
            self.clock.tick(60)

        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class CubeMesh:
    def __init__(self):
        self.vertices = (
            # positions - normals - texture
            # Back face
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0,
            # Front face
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0,
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
            # Left face
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 1.0, 1.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
            -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 0.0, 0.0,
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,
            # Right face
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0,
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
            # Bottom face
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0,
            0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1.0, 1.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
            -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0,
            # Top face
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 1.0,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0
        )

        self.vertex_count = len(self.vertices) // 8

        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        stride = (3 + 3 + 2) * 4
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))




class Mesh:
    def __init__(self, filename):
        self.vertices = []
        self.loadMesh(filename)
        self.vertex_count = len(self.vertices) // 8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        stride = (3 + 3 + 2) * 4
        # Position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        # Normal
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        # Texture
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

    def loadMesh(self, filename):
        v = []
        vt = []
        vn = []
        with open(filename, "r") as file:
            line = file.readline()
            while line:
                words = line.split(" ")
                if words[0] == "v":
                    v.append([float(words[1]), float(words[2]), float(words[3])])
                elif words[0] == "vt":
                    vt.append([float(words[1]), float(words[2])])
                elif words[0] == "vn":
                    vn.append([float(words[1]), float(words[2]), float(words[3])])
                elif words[0] == "f":
                    v1 = words[1].split("/")
                    v2 = words[2].split("/")
                    v3 = words[3].strip().split("/")
                    self.process_vertex(v1, v, vt, vn)
                    self.process_vertex(v2, v, vt, vn)
                    self.process_vertex(v3, v, vt, vn)

                line = file.readline()

    def process_vertex(self, vertex_data, v, vt, vn):
        vertex_ptr = int(vertex_data[0]) - 1
        texture_ptr = int(vertex_data[1]) - 1
        normal_ptr = int(vertex_data[2]) - 1
        self.vertices = self.vertices + v[vertex_ptr]
        self.vertices = self.vertices + vn[normal_ptr]
        self.vertices = self.vertices + vt[texture_ptr]

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Material:

    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))


if __name__ == '__main__':
    app = App()
