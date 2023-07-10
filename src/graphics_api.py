import numpy as np
import pyrr
from OpenGL.GL import *


def draw_mesh(shader, mesh, model_location, position, rotation=(0, 0, 0), scale=1, method=GL_TRIANGLES):
    position = np.array(position, dtype=np.float32)
    rotation = np.array(rotation, dtype=np.float32)
    scale = np.array([scale] * 3, dtype=np.float32)
    model = pyrr.matrix44.create_identity(dtype=np.float32)
    model = pyrr.matrix44.multiply(
        m1=model,
        m2=pyrr.matrix44.create_from_scale(scale)
    )
    model = pyrr.matrix44.multiply(
        m1=model,
        m2=pyrr.matrix44.create_from_eulers(
            eulers=np.radians(rotation),
            dtype=np.float32
        )
    )
    model = pyrr.matrix44.multiply(
        m1=model,
        m2=pyrr.matrix44.create_from_translation(
            vec=np.array(position),
            dtype=np.float32
        )
    )
    shader.use()

    glUniformMatrix4fv(model_location, 1, GL_FALSE, model)
    glBindVertexArray(mesh.vao)
    glDrawArrays(method, 0, mesh.vertex_count)

    shader.detach()

