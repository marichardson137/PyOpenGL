import pygame as pg
from OpenGL.GL import *

from src.app import Window
from src.model import Model
from src.shader import Shader


class GUIText:

    def __init__(self):
        self.shader = Shader("shaders/gui_vertex.glsl", "shaders/gui_fragment.glsl")
        self.quad = Model("models/square.obj", position=[0, 0, 0])
        self.offscreen_surface = pg.Surface((Window.WIDTH, Window.HEIGHT))
        self.texID = glGenTextures(1)

    def surfaceToTexture(pygame_surface):
        global texID
        rgb_surface = pg.image.tostring(pygame_surface, 'RGB')
        glBindTexture(GL_TEXTURE_2D, texID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        surface_rect = pygame_surface.get_rect()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                     rgb_surface)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def render_text(self, font, string, location=(0, 0), color=pg.Color(255, 255, 255)):
        text = font.render(string, True, color)
        offscreen_surface.blit(text, location)

