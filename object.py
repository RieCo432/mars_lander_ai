from random import randint
import pygame


class Pad(pygame.sprite.Sprite):

    def __init__(self, low=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("resources/landingPads/pad.png")
        self.rect = self.image.get_rect()
        if not low:
            self.y = (750- randint(0,200)) - self.rect.height / 2
        else:
            self.y = 750 - self.rect.height / 2
        self.x = randint(self.rect.width / 2, 1200 - self.rect.width / 2)
        self.rect.center = (self.x, self.y)


class Obstacle(pygame.sprite.Sprite):

    def __init__(self):

        pygame.sprite.Sprite.__init__(self)
        obstacle_type = randint(0, 9)
        if obstacle_type == 0:
            self.image = pygame.image.load("resources/obstacles/building_dome.png")
        elif obstacle_type == 1:
            self.image = pygame.image.load("resources/obstacles/building_station_NE.png")
        elif obstacle_type == 2:
            self.image = pygame.image.load("resources/obstacles/building_station_SW.png")
        elif obstacle_type == 3:
            self.image = pygame.image.load("resources/obstacles/pipe_ramp_NE.png")
        elif obstacle_type == 4:
            self.image = pygame.image.load("resources/obstacles/pipe_stand_SE.png")
        elif obstacle_type == 5:
            self.image = pygame.image.load("resources/obstacles/rocks_NW.png")
        elif obstacle_type == 6:
            self.image = pygame.image.load("resources/obstacles/rocks_ore_SW.png")
        elif obstacle_type == 7:
            self.image = pygame.image.load("resources/obstacles/rocks_small_SE.png")
        elif obstacle_type == 8:
            self.image = pygame.image.load("resources/obstacles/satellite_SE.png")
        elif obstacle_type == 9:
            self.image = pygame.image.load("resources/obstacles/satellite_SW.png")

        self.rect = self.image.get_rect()
        self.y = 750 - self.rect.height / 2
        self.x = randint(round(self.rect.width / 2), 1200 - round(self.rect.width / 2))
        self.rect.center = (self.x, self.y)

class Meteor(pygame.sprite.Sprite):

    def __init__(self,velocityx, velocityy):

        pygame.sprite.Sprite.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        obstacle_type = randint(0, 3)
        if obstacle_type == 0:
            self.image = pygame.image.load("resources/meteors/spaceMeteors_001.png")
        elif obstacle_type == 1:
            self.image = pygame.image.load("resources/meteors/spaceMeteors_002.png")
        elif obstacle_type == 2:
            self.image = pygame.image.load("resources/meteors/spaceMeteors_003.png")
        elif obstacle_type == 3:
            self.image = pygame.image.load("resources/meteors/spaceMeteors_004.png")
        stormx = -100
        stormy = -100
        self.x = stormx + randint(-100, 100)
        self.y =  stormy + randint(-100, 100)
        self.vel_x = velocityx + randint(-1, 1)
        self.vel_y = velocityy + randint(-1, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)


