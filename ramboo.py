import pygame as pg
import numpy as np

from actors import Player, Enemy, Background


class Game:
    def __init__(self, w: int, h: int, fps: int = 30):
        # general
        self.dt = 0
        self.fps = fps
        self.running = 1
        self.screen = None
        self.score = 0
        self.clock = pg.time.Clock()
        self.size = pg.math.Vector2(w, h)
        self.mvmt_keys = list()
        self.moveX = 0
        self.moveY = 0

        # players
        self.player = None
        self.sprites = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

    def on_init(self):
        pg.init()
        self.running = 1
        # pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])
        self.screen = pg.display.set_mode(
            self.size, pg.HWSURFACE | pg.DOUBLEBUF, 16)
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_CROSSHAIR)
        self.font = pg.font.Font('freesansbold.ttf', 20)
        self.bg = Background(path='sprites/bg.png',
                             mask='sprites/bg_mask.png', center=self.size / 2)
        self.bg.add(self.sprites)
        self.setup_players()

    def setup_players(self):
        self.player = Player('sprites/ghost.png',
                             'sprites/ghost_mask.png',
                             pg.math.Vector2(30, 30) * 2,
                             origin=self.size / 2)
        self.player.add(self.sprites)
        for i in range(100):
            enemy = Enemy('sprites/zombie.png',
                          'sprites/zombie_mask.png',
                          pg.math.Vector2(15, 30) * 2,
                          origin=self.size / 3 + pg.math.Vector2(i, i),
                          player_pos=self.size / 2,
                          speed=1)
            enemy.add(self.sprites)
            enemy.add(self.enemies)

    def on_event(self, event):
        if event.type == pg.QUIT:
            self.running = 0
        elif event.type == pg.KEYDOWN:
            if event.key in {pg.K_a, pg.K_w, pg.K_s, pg.K_d, pg.K_LSHIFT}:
                self.mvmt_keys.append(event.key)
            if event.key == pg.K_SPACE:
                pass
        elif event.type == pg.KEYUP:
            if event.key in {pg.K_a, pg.K_w, pg.K_s, pg.K_d, pg.K_LSHIFT}:
                self.mvmt_keys.remove(event.key)
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.player.shoot([self.sprites, self.bullets])

    def update_camera_coords(self):
        moveX, moveY = 0, 0
        sprint = 1 if pg.K_LSHIFT in self.mvmt_keys else 1
        vel = 150
        if self.mvmt_keys:
            collision_coords = pg.sprite.collide_mask(self.player, self.bg)
            left, right, top, bottom = False, False, False, False
            if collision_coords is None:
                for enemy in self.enemies:
                    collision_coords = pg.sprite.collide_mask(
                        self.player, enemy)
                    if collision_coords is not None:
                        break
            if collision_coords is not None:
                collision_coords = (pg.math.Vector2(collision_coords))
                if collision_coords.x == 0:
                    left = True
                elif collision_coords.x == self.player.rect.size[0] - 1:
                    right = True
                if collision_coords.y == 0:
                    top = True
                elif collision_coords.y == self.player.rect.size[1] - 1:
                    bottom = True
                if not any([left, right, top, bottom]):
                    if (collision_coords.x < self.player.rect.size[0] / 2 and
                            collision_coords.y < self.player.rect.size[1] / 2):
                        left = True
                        top = True
                    elif (collision_coords.x < self.player.rect.size[0] / 2 and
                            collision_coords.y > self.player.rect.size[1] / 2):
                        left = True
                        bottom = True
                    elif (collision_coords.x > 2 + self.player.rect.size[0] / 2 and
                            collision_coords.y < self.player.rect.size[1] / 2):
                        right = True
                        top = True
                    elif (collision_coords.x > 2 + self.player.rect.size[0] / 2 and
                            collision_coords.y > self.player.rect.size[1] / 2):
                        right = True
                        bottom = True
            if (pg.K_a in self.mvmt_keys and pg.K_d not in self.mvmt_keys
                    and not left):
                moveX = vel if self.bg.rect.left < 0 else 0
            elif (pg.K_d in self.mvmt_keys and pg.K_a not in self.mvmt_keys
                    and not right):
                moveX = -vel if self.bg.rect.right > self.size.x else 0
            if (pg.K_w in self.mvmt_keys and pg.K_s not in self.mvmt_keys
                    and not top):
                moveY = vel if self.bg.rect.top < 0 else 0
            elif (pg.K_s in self.mvmt_keys and pg.K_w not in self.mvmt_keys
                    and not bottom):
                moveY = -vel if self.bg.rect.bottom > self.size.y else 0
        if moveY and moveX:
            moveY /= 1.2
            moveX /= 1.2
        self.moveX = moveX * sprint * self.dt
        self.moveY = moveY * sprint * self.dt

    def loop(self):
        self.update_camera_coords()
        # self.bg_rect.(pg.math.Vector2(self.moveX, self.moveY))
        # self.bg_mask.move_ip(pg.math.Vector2(self.moveX, self.moveY))
        self.sprites.update(
            dt=self.dt,
            cam_coords=pg.math.Vector2(self.moveX, self.moveY),
            mvmt_keys=self.mvmt_keys,
            mouse_pos=pg.math.Vector2(pg.mouse.get_pos()))
        for i, bullet in enumerate(self.bullets):
            sprites = pg.sprite.spritecollide(
                bullet, self.enemies, dokill=False)
            if sprites:
                bullet.kill()
                self.score += 1
                for sprite in sprites:
                    sprite.take_hit()

    def render(self):
        # self.screen.blit(self.bg, self.bg_rect)
        for sprite in self.sprites:
            sprite.render(self.screen)
        score = self.font.render(
            f"Points: {self.score}", True, (0, 255, 0))
        self.screen.blit(score, (10, 10))
        pg.display.flip()

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
    game = Game(w=750, h=500, fps=60)
    game.run()
