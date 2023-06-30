import pygame as pg
import pyrr
from OpenGL.GL import *
import numpy as np


class Model:

    def __init__(self, filename, position=(0, 0, 0), rotation=(0, 0, 0), scale=1):
        self.mesh = Mesh(filename)
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array([scale] * 3, dtype=np.float32)
        self.model = None

    def update_transformation(self):
        self.model = pyrr.matrix44.create_identity(dtype=np.float32)
        self.model = pyrr.matrix44.multiply(
            m1=self.model,
            m2=pyrr.matrix44.create_from_scale(self.scale)
        )
        self.model = pyrr.matrix44.multiply(
            m1=self.model,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.rotation),
                dtype=np.float32
            )
        )
        self.model = pyrr.matrix44.multiply(
            m1=self.model,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),
                dtype=np.float32
            )
        )

    def draw(self, modelMatrixLocation):
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_FALSE, self.model)
        # self.texture.use()
        glBindVertexArray(self.mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count)

    def destroy(self):
        self.mesh.destroy()


class Mesh:
    def __init__(self, filename):
        self.vertices = []
        self.load_mesh(filename)
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

    def load_mesh(self, filename):
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
