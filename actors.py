from typing import Tuple

import pygame as pg
import numpy as np


class Player(pg.sprite.Sprite):
    def __init__(self, path: str,
                 mask: str,
                 size: pg.math.Vector2,
                 origin: pg.math.Vector2):
        self.health = 10
        self.ammo = 1000
        pg.sprite.Sprite.__init__(self)
        img = pg.image.load(path)
        img = pg.transform.scale(img, size)
        self.image = img.convert_alpha()
        # self.surf = pg.Surface(size)
        mask_surf = pg.image.load(mask)
        mask_surf = pg.transform.scale(mask_surf, size)
        mask_surf = mask_surf.convert_alpha()
        self.mask = pg.mask.from_surface(mask_surf)
        self.rect = self.image.get_rect(topleft=-size / 2)
        # self.rect = self.image.get_rect(topleft=-size / 2)
        self.gun = Gun(size=pg.math.Vector2(5, 5),
                       origin=origin,
                       offset=pg.math.Vector2(size.x, 0))
        self.set(origin)

    def take_hit(self):
        self.health = max(self.health - 1, 0)

    @property
    def dead(self):
        return self.health <= 0

    def set(self, pos: Tuple[int, int]):
        self.rect.move_ip(pos)
        self.gun.set(self.rect)

    def move(self, pos: Tuple[int, int]):
        self.rect.move_ip(pos)
        self.gun.move(pos, pg.math.Vector2(self.rect.center))

    def update(self, mvmt_keys, mouse_pos, *args, **kwargs):
        # moveX, moveY = 0, 0
        # sprint = 1.1 if pg.K_LSHIFT in mvmt_keys else 1
        # if mvmt_keys:
        #     if pg.K_a in mvmt_keys and pg.K_d not in mvmt_keys:
        #         moveX = -10
        #     elif pg.K_d in mvmt_keys and pg.K_a not in mvmt_keys:
        #         moveX = 10
        #     if pg.K_w in mvmt_keys and pg.K_s not in mvmt_keys:
        #         moveY = -10
        #     elif pg.K_s in mvmt_keys and pg.K_w not in mvmt_keys:
        #         moveY = 10
        # self.move((moveX * sprint, moveY * sprint), mouse_pos)
        self.gun.rotate(mouse_pos)

    def render(self, screen):
        screen.blit(self.image, self.rect)
        self.gun.render(screen)

    def shoot(self, groups):
        if self.ammo:
            self.ammo = max(0, self.ammo - 1)
            bullet = Bullet('sprites/bullet.png', speed=800,
                            pos=self.gun.center,
                            angle=self.gun.angle,
                            range=200,
                            vel=(self.gun.center - self.rect.center),
                            size=pg.math.Vector2(30, 30))
            for g in groups:
                bullet.add(g)


class Bullet(pg.sprite.Sprite):
    def __init__(self, path: str,
                 speed: int,
                 range: int,
                 pos: pg.math.Vector2,
                 vel: pg.math.Vector2,
                 angle: int, size: pg.math.Vector2,):
        pg.sprite.Sprite.__init__(self)
        # self.surf.fill((255, 255, 0))

        self.range = range
        self.vel = vel.normalize() * speed
        self.origin, self.pos = pos - size / 2, pos - size / 2
        img = pg.image.load(path)
        img = pg.transform.rotate(
            pg.transform.scale(img, size), angle + 0)
        self.image = img.convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

    def update(self, dt, *args, **kwargs):
        self.pos += self.vel * dt
        self.rect = self.image.get_rect(topleft=self.pos)
        if self.origin.distance_to(self.pos) > self.range:
            self.kill()

    def render(self, screen):
        screen.blit(self.image, self.rect)
        # screen.blit(self.surf, self.pos)


class Gun(pg.sprite.Sprite):
    def __init__(self, size: pg.math.Vector2,
                 origin: pg.math.Vector2, offset: pg.math.Vector2):
        pg.sprite.Sprite.__init__(self)
        self.offset = offset
        img = pg.image.load('sprites/shotgun.png')
        img = pg.transform.scale(img, size)
        self.image = img.convert_alpha()
        if True:
            self.image = pg.Surface(size)
            self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rimage = self.image
        self.origin = origin - pg.math.Vector2(self.rect.size) / 2
        self.center = origin + offset
        # self.surf.fill((255, 0, 0))
        self.angle = 0

    def move(self, pos, origin):
        self.rect.move_ip(pos)
        self.origin = origin

    def set(self, rect):
        self.origin = pg.math.Vector2(rect.center)
        x = self.offset.x + \
            rect.center[0] - self.rect.size[0] / 2
        y = self.offset.y + \
            rect.center[1] - self.rect.size[1] / 2
        self.center = pg.math.Vector2(x, y)
        self.rect.update(pg.Rect(x, y, *self.rect.size))

    def rotate(self, pos):
        point = pos - self.origin
        self.angle = angle = np.arctan2(point.x, point.y) * (180 / np.pi) - 90
        self.center = self.origin + point.normalize() * self.offset.x

        if pos.x < self.origin.x:
            self.rimage = pg.transform.rotate(
                pg.transform.flip(self.image, False, True), angle)
        else:
            self.rimage = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.center)

    def render(self, screen):
        # screen.blit(self.rimage, self.center)
        screen.blit(self.image, self.center)


class Enemy(Player):
    def __init__(self, path: str,
                 mask: str,
                 size: pg.math.Vector2,
                 origin: pg.math.Vector2,
                 player_pos: pg.math.Vector2,
                 speed: float):
        super(Enemy, self).__init__(path, mask, size, origin)
        self.player_pos = player_pos
        self.health = 2
        self.speed = speed

    def shoot(self):
        ...

    def update(self, dt, cam_coords, *args, **kwargs):
        if self.dead:
            self.kill()
        self.move(cam_coords)
        self.gun.rotate(self.player_pos)


class Background(pg.sprite.Sprite):
    def __init__(self, path: str, mask: str, center):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(path).convert_alpha()
        self.rect = self.image.get_rect(center=center)
        mask_surf = pg.image.load(mask).convert_alpha()
        self.mask = pg.mask.from_surface(mask_surf)

    def update(self, cam_coords, *args, **kwargs):
        self.rect.move_ip(cam_coords)

    def render(self, screen):
        screen.blit(self.image, self.rect)
