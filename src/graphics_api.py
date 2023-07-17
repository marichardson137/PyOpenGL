import numpy as np
import pyrr
from OpenGL.GL import *


def draw_mesh(shader, mesh, model_location, position, rotation=(0, 0, 0), rotation_matrix=None, scale=1,
              method=GL_TRIANGLES):
    position = np.array(position, dtype=np.float32)
    rotation = np.array(rotation, dtype=np.float32)
    scale = np.array([scale] * 3, dtype=np.float32)
    model = pyrr.matrix44.create_identity(dtype=np.float32)
    model = pyrr.matrix44.multiply(
        m1=model,
        m2=pyrr.matrix44.create_from_scale(scale)
    )

    if rotation_matrix is None:
        model = pyrr.matrix44.multiply(
            m1=model,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=rotation,
                dtype=np.float32
            )
        )
    else:
        model = pyrr.matrix44.multiply(
            m1=model,
            m2=pyrr.matrix44.create_from_matrix33(rotation_matrix)
        )

    model = pyrr.matrix44.multiply(
        m1=model,
        m2=pyrr.matrix44.create_from_translation(
            vec=position,
            dtype=np.float32
        )
    )
    shader.use()
    glUniformMatrix4fv(model_location, 1, GL_FALSE, model)
    glBindVertexArray(mesh.vao)
    glDrawArrays(method, 0, mesh.vertex_count)
    shader.detach()
    glBindVertexArray(0)


def normalize_vector(v):
    length = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return v[0] / length, v[1] / length, v[2] / length


def create_icosphere(radius, recursion_level):
    # Constants for icosahedron vertex positions
    t = (1.0 + np.sqrt(5.0)) / 2.0
    vertices = [
        normalize_vector((-1, t, 0)),
        normalize_vector((1, t, 0)),
        normalize_vector((-1, -t, 0)),
        normalize_vector((1, -t, 0)),
        normalize_vector((0, -1, t)),
        normalize_vector((0, 1, t)),
        normalize_vector((0, -1, -t)),
        normalize_vector((0, 1, -t)),
        normalize_vector((t, 0, -1)),
        normalize_vector((t, 0, 1)),
        normalize_vector((-t, 0, -1)),
        normalize_vector((-t, 0, 1))
    ]

    # Icosahedron face indices
    faces = [
        (0, 11, 5),
        (0, 5, 1),
        (0, 1, 7),
        (0, 7, 10),
        (0, 10, 11),
        (1, 5, 9),
        (5, 11, 4),
        (11, 10, 2),
        (10, 7, 6),
        (7, 1, 8),
        (3, 9, 4),
        (3, 4, 2),
        (3, 2, 6),
        (3, 6, 8),
        (3, 8, 9),
        (4, 9, 5),
        (2, 4, 11),
        (6, 2, 10),
        (8, 6, 7),
        (9, 8, 1)
    ]

    # Subdivide faces
    for _ in range(recursion_level):
        new_faces = []
        for face in faces:
            v1, v2, v3 = [vertices[i] for i in face]
            v12 = normalize_vector(((v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2, (v1[2] + v2[2]) / 2))
            v23 = normalize_vector(((v2[0] + v3[0]) / 2, (v2[1] + v3[1]) / 2, (v2[2] + v3[2]) / 2))
            v31 = normalize_vector(((v3[0] + v1[0]) / 2, (v3[1] + v1[1]) / 2, (v3[2] + v1[2]) / 2))
            vertices.append(v12)
            vertices.append(v23)
            vertices.append(v31)
            new_faces.append((face[0], len(vertices) - 3, len(vertices) - 1))
            new_faces.append((len(vertices) - 3, face[1], len(vertices) - 2))
            new_faces.append((len(vertices) - 1, len(vertices) - 2, face[2]))
            new_faces.append((len(vertices) - 3, len(vertices) - 2, len(vertices) - 1))
        faces = new_faces

    # Generate vertex positions with radius
    vertex_positions = [(vertex[0] * radius, vertex[1] * radius, vertex[2] * radius) for vertex in vertices]

    return vertex_positions

