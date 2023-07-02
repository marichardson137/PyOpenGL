from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.raw.GL.VERSION.GL_2_0 import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, glUseProgram, glDeleteProgram


class Shader:

    def __init__(self, vertex_filepath, fragment_filepath):
        self.in_use = False
        self.shader_id = self.create_shader(vertex_filepath, fragment_filepath)

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

    def use(self):
        if not self.in_use:
            glUseProgram(self.shader_id)
            self.in_use = True

    def detach(self):
        glUseProgram(0)
        self.in_use = False

    def destroy(self):
        glDeleteProgram(self.shader_id)
