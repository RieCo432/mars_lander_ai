import pygame
from random import uniform
from math import sin, cos, radians

class Lander(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load("resources/lander.png")
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.x = 600
        self.y = self.rect.height / 2
        self.rect.center = (self.x, self.y)
        self.x_vel = uniform(-1, 1)
        self.y_vel = uniform(0, 1)
        self.damage = 0
        self.angle = 0
        self.dead = False
        self.fuel = 500

    def update(self):
        self.y_vel += 0.1
        self.x += self.x_vel
        self.y += self.y_vel
        if self.x < 0:
            self.x = 1200
        if self.x > 1200:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if (self.y + self.rect.height / 2) > 750 :
            self.dead = True
            self.damage = 1
        self.rect.center = (self.x, self.y)

    def thrust(self):
        if self.fuel >= 5:
            self.x_vel += 1 * sin(radians(-self.angle))
            self.y_vel -= 1 * cos(radians( self.angle))
            self.fuel -= 5

    def rotate(self, change):
        self.angle += change
        if self.angle > 180:
            self.angle -= 360
        if self.angle < -180:
            self.angle += 360
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.rect = self.image.get_rect()

    def pad_collide(self,pad):
        if self.x_vel > 5 or self.y_vel > 5:
            self.dead = True
            self.damage = 1
            return False
        elif self.y > pad.y:
            self.dead = True
            self.damage = 1
            return False
        elif self.angle != 0:
            self.dead = True
            self.damage = 1
            return False
        else:
            return True

    def reset(self):
        self.x = 600
        self.y = self.rect.height / 2
        self.rect.center = (self.x, self.y)
        self.x_vel = uniform(-1, 1)
        self.y_vel = uniform(0, 1)