import pygame as pg


class Game:
    def __init__(self, w: int, h: int, fps: int = 30):
        self.dt = 0
        self.fps = fps
        self.running = 1
        self.screen = None
        self.clock = pg.time.Clock()
        self.size = self.w, self.h = w, h

    def on_init(self):
        pg.init()
        pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])
        self.display = pg.display.set_mode(
            self.size,
            pg.HWSURFACE | pg.DOUBLEBUF,
            16)
        self.running = 1

    def on_event(self, event):
        if event.type == pg.QUIT:
            self.running = 0

    def loop(self):
        pass

    def render(self):
        pg.display.update()

    def cleanup(self):
        pg.quit()

    def run(self):
        if self.on_init() is False:
            self.running = 0
        self.clock.tick(self.fps)
        while(self.running):
            self.dt = self.clock.tick(self.fps) / 1000.
            for event in pg.event.get():
                self.on_event(event)
            self.loop()
            self.render()
        self.cleanup()


if __name__ == "__main__":
    game = Game(w=500, h=500)
    game.run()
