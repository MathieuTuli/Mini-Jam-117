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
        print(self.health)

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


class Zombie(pg.sprite.Sprite):
    def __init__(self, path: str,
                 mask: str,
                 arm: str,
                 arm_mask: str,
                 size: pg.math.Vector2,
                 arm_size: pg.math.Vector2,
                 attack_interval: float,
                 origin: pg.math.Vector2,
                 player_pos: pg.math.Vector2,
                 speed: float):
        pg.sprite.Sprite.__init__(self)
        self.player_pos = player_pos
        self.health = 2
        self.speed = speed
        img = pg.image.load(path)
        img = pg.transform.scale(img, size)
        self.image = img.convert_alpha()
        self.can_attack = True
        self.time = 0.
        self.attack_interval = attack_interval
        # self.surf = pg.Surface(size)
        mask_surf = pg.image.load(mask)
        mask_surf = pg.transform.scale(mask_surf, size)
        mask_surf = mask_surf.convert_alpha()
        self.mask = pg.mask.from_surface(mask_surf)
        self.rect = self.image.get_rect(topleft=-size / 2)
        self.origin = origin - pg.math.Vector2(self.rect.size) / 2

        # ARMS
        # LEFT
        img = pg.image.load(arm)
        img = pg.transform.rotate(pg.transform.scale(img, arm_size), 0)
        self.left_arm = img.convert_alpha()
        self.left_arm_rect = self.left_arm.get_rect()
        self.rlarm = self.left_arm

        # LEFT MASK
        # mask_surf = pg.image.load(arm_mask)
        # mask_surf = pg.transform.scale(mask_surf, size)
        # mask_surf = mask_surf.convert_alpha()
        # self.left_arm_mask = pg.mask.from_surface(mask_surf)

        # RIGHT
        img = pg.image.load(arm)
        img = pg.transform.rotate(pg.transform.scale(img, arm_size), 0)
        self.right_arm = img.convert_alpha()
        self.right_arm_rect = self.right_arm.get_rect()
        self.rrarm = self.right_arm

        # RIGHT MASK
        # mask_surf = pg.image.load(arm_mask)
        # mask_surf = pg.transform.scale(mask_surf, size)
        # mask_surf = mask_surf.convert_alpha()
        # self.right_arm_mask = pg.mask.from_surface(mask_surf)

        self.set(origin)

    def attack(self):
        if self.can_attack:
            self.can_attack = False
            return True
        else:
            return False

    def take_hit(self):
        self.health = max(self.health - 1, 0)

    @property
    def dead(self):
        return self.health <= 0

    def move(self, pos: Tuple[int, int]):
        self.rect.move_ip(pos)
        self.origin = pg.math.Vector2(self.rect.center)
        self.left_arm_rect.move_ip(pos)
        self.right_arm_rect.move_ip(pos)

    def set(self, pos: Tuple[int, int]):
        self.rect.move_ip(pos)
        self.left_arm_rect.move_ip(
            pos - pg.math.Vector2(self.left_arm_rect.size[0] * 1.1,
                                  self.left_arm_rect.size[1] * 0.3))
        self.right_arm_rect.move_ip(
            pos + pg.math.Vector2(-self.right_arm_rect.size[0] * 0.8,
                                  -self.right_arm_rect.size[1] * .3))

    def rotate_arms(self, pos):
        point = pos - self.origin
        angle = np.arctan2(point.x, point.y) * (180 / np.pi) - 90
        # if pos.x > self.origin.x:
        #     self.llarm = pg.transform.rotate(
        #         pg.transform.flip(self.left_arm, False, True), angle)
        #     self.rlarm = pg.transform.rotate(
        #         pg.transform.flip(self.right_arm, False, True), angle)
        # else:
        self.rlarm = pg.transform.rotate(self.left_arm, angle)
        self.rrarm = pg.transform.rotate(self.right_arm, angle)

    def shoot(self):
        ...

    def update(self, dt, cam_coords, *args, **kwargs):
        if not self.can_attack and self.time < self.attack_interval:
            self.time += dt
        else:
            self.time = 0
            self.can_attack = True
        if self.dead:
            self.kill()
        self.move(cam_coords)
        # self.rotate_arms(self.player_pos)

    def render(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.rlarm, self.left_arm_rect)
        screen.blit(self.rrarm, self.right_arm_rect)


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
