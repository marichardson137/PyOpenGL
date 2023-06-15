import pygame as pg
from OpenGL.GL import *


class App:

    def __init__(self):
        pg.init()
        pg.display.set_mode((900, 500), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.1, 0.3, 0.2, 1.0)

        self.run()

    def run(self):

        running = True
        while running:
            # Poll events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            pg.display.flip()

            # Timing
            self.clock.tick(60)

        self.quit()

    def quit(self):
        pg.quit()

class Triangle:
    # X Y Z R G B
    def __init__(self):
        self.vertices = {

        }

if __name__ == '__main__':
    app = App()
