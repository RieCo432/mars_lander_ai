import pygame
import sys
from lander import Lander
from object import Pad, Obstacle, Meteor
from telemetry import display_text
from datetime import datetime
from time import sleep
from random import random, randint
from math import sqrt
from ai.population import Population
from ai.config import ActivationFunctions


WIDTH = 1200
HEIGHT = 750
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
my_font = pygame.font.SysFont("Ariel", 16)
screen.fill(0)

background_image = pygame.image.load("resources/mars_background_instr.png")

pygame.display.set_caption("Mars Lander")

clock = pygame.time.Clock()

class Game:

    def __init__(self, neural_net=None):
        self.lander = Lander()
        self.lives = 2
        self.allsprites = pygame.sprite.Group()
        self.allsprites.add(self.lander)
        self.maxipads = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        # for i in range(5):
        #    newobj = Obstacle()
        #    while pygame.sprite.spritecollideany(newobj, self.obstacles) is not None or pygame.sprite.spritecollideany(newobj, self.maxipads) is not None:
        #        newobj = Obstacle()
        #    self.obstacles.add(newobj)
        #    self.allsprites.add(newobj)
        for i in range(3):
            newpad = Pad(low=True)
            while pygame.sprite.spritecollideany(newpad, self.maxipads) is not None or pygame.sprite.spritecollideany(newpad, self.obstacles) is not None:
                newpad = Pad(low=True)
            self.maxipads.add(newpad)
            self.allsprites.add(newpad)
        self.score = 0
        self.gameover = False
        self.starttime = datetime.now()
        self.thrust_img = pygame.image.load("resources/thrust.png")
        self.thrust_img_rect = self.thrust_img.get_rect()
        self.control_blocked = [False,False,False]
        self.control_blocked_start = datetime.now()
        self.meteors = pygame.sprite.Group()
        self.neural_network = neural_net
        self.drawing = False
        self.slow_down_learned = False
        self.straight_angle_learned = False
        self.gain_xvel_learned = False
        self.point_against_xvel_learned = False
        self.xvel_slowdown_learned = False
        self.cancel_xvel_learned = False

    def show_telemetry(self, screen):
        elapsed_time = (datetime.now() - self.starttime).total_seconds()
        if self.drawing:
            display_text(screen, str(self.lander.fuel) + "kg", 110, 45)
            display_text(screen, str(round(self.lander.x_vel*100)/100) + "ms", 305, 45)
            display_text(screen, str(round(self.lander.y_vel * 100) / 100) + "ms", 305, 66)
            display_text(screen, str(round(1000 / 750 * (750 - self.lander.y))) + "m", 305, 22)
            display_text(screen, str(round(self.lander.damage*100)) + "%", 110, 66)
            s_passed = int(elapsed_time % 60)
            m_passed = int(elapsed_time // 60)
            display_text(screen, str(m_passed) +":" + str(f"{s_passed:02d}"), 110, 22)
            display_text(screen, str(f"{self.score:03d}"), 110, 95)

    def create_failure(self):
        if any(self.control_blocked) and (datetime.now() - self.control_blocked_start).total_seconds() >= 2:
            self.control_blocked = [False, False, False]
        elif not any(self.control_blocked) and random() < 0.002:
            self.control_blocked[randint(0, 2)] = True
            self.control_blocked_start = datetime.now()

    def wait_key(self):
        keypressed = True
        while not keypressed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    keypressed = True


    def create_storm(self):
        if len(self.meteors) == 0 and random() < 0.001:
            for i in range(randint(5, 10)):
                new_meteor = Meteor(randint(3, 5), randint(2, 3))
                while pygame.sprite.spritecollideany(new_meteor, self.meteors) is not None:
                    new_meteor = Meteor(randint(3, 5), randint(2, 3))
                self.meteors.add(new_meteor)
                self.allsprites.add(new_meteor)
        else:
            collided_meteor = pygame.sprite.spritecollideany(self.lander, self.meteors)
            if collided_meteor is not None:
                self.lander.damage += 0.25
                self.meteors.remove(collided_meteor)
            for meteor in self.meteors:
                if meteor.y >= HEIGHT:
                    self.meteors.remove(meteor)
                    self.allsprites.remove(meteor)

    def play(self):
        thrusting = False
        thrust_counter = 0
        if not self.gameover:
            # self.create_failure()
            # self.create_storm()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit("0")
                if event.type == pygame.KEYDOWN and self.lander.damage < 1 and self.neural_network is None:
                    if event.key ==  pygame.K_SPACE and not self.control_blocked[1]:
                        self.lander.thrust()
                        if self.lander.fuel >= 5:
                            thrusting = True
                            thrust_counter = 5
                    if event.key == pygame.K_RIGHT and not self.control_blocked[2]:
                        self.lander.rotate(-5)
                    if event.key == pygame.K_LEFT and not self.control_blocked[0]:
                        self.lander.rotate(5)

            if self.neural_network is not None:

                controls = self.neural_network.get_outputs()

                if controls[0] >= 0.4:  # right
                    self.lander.rotate(-5)
                if controls[0] <= -0.4:
                    self.lander.rotate(5)  # left
                if controls[1] >= 0.5:
                    self.lander.thrust()
                    if self.lander.fuel >= 5:
                        thrusting = True
                        thrust_counter = 5


            self.allsprites.update()
            collidedobj = pygame.sprite.spritecollideany(self.lander, self.obstacles)
            if collidedobj is not None:
                self.lander.damage += 0.1
                old_distance = sqrt((self.lander.x - collidedobj.rect.centerx) ** 2 + (self.lander.y - collidedobj.rect.centery) ** 2)
                self.lander.x = collidedobj.rect.centerx + ((self.lander.x - collidedobj.rect.centerx) / old_distance) * (old_distance + 5)
                self.lander.y = collidedobj.rect.centery + ((self.lander.y - collidedobj.rect.centery) / old_distance) * (old_distance + 5)

            collidedpad = pygame.sprite.spritecollideany(self.lander, self.maxipads)
            if collidedpad is not None:
                self.neural_network.fitness_boosts.append(40)
                if self.lander.pad_collide(collidedpad):
                    self.score += 50
                    display_text(screen, "Landed!", 600, 375)
                    # print("landed")
                    # pygame.display.flip()
                    # sleep(0.5)
                    # self.wait_key()

                    for landing_pad in self.maxipads:
                        # remove all landing pads
                        self.allsprites.remove(landing_pad)
                        self.maxipads.remove(landing_pad)

                    for i in range(3):
                        newpad = Pad(low=True)
                        while pygame.sprite.spritecollideany(newpad,
                                                             self.maxipads) is not None or pygame.sprite.spritecollideany(
                                newpad, self.obstacles) is not None:
                            newpad = Pad(low=True)
                        self.maxipads.add(newpad)
                        self.allsprites.add(newpad)

                    self.lander.reset()
                    self.starttime = datetime.now()

            if self.lander.dead:
                if self.lives > 0:
                    self.lives -= 1
                    self.allsprites.remove(self.lander)
                    self.lander = Lander()
                    self.allsprites.add(self.lander)
                    display_text(screen, "You crashed!", 600, 375)
                    #pygame.display.flip()
                    #sleep(0.5)
                    #self.wait_key()

                    for landing_pad in self.maxipads:
                        # remove all landing pads
                        self.allsprites.remove(landing_pad)
                        self.maxipads.remove(landing_pad)

                    for i in range(3):
                        newpad = Pad(low=True)
                        while pygame.sprite.spritecollideany(newpad,
                                                             self.maxipads) is not None or pygame.sprite.spritecollideany(
                                newpad, self.obstacles) is not None:
                            newpad = Pad(low=True)
                        self.maxipads.add(newpad)
                        self.allsprites.add(newpad)

                    self.starttime = datetime.now()
                else:
                    display_text(screen, "Game over!", 600, 375)
                    #pygame.display.flip()
                    #sleep(0.5)
                    #self.wait_key()
                    if self.slow_down_learned:
                        self.neural_network.fitness_boosts.append(150)
                    if self.straight_angle_learned:
                        self.neural_network.fitness_boosts.append(150)
                    if self.gain_xvel_learned:
                        self.neural_network.fitness_boosts.append(40)
                    if self.point_against_xvel_learned:
                        self.neural_network.fitness_boosts.append(50)
                    if self.xvel_slowdown_learned:
                        self.neural_network.fitness_boosts.append(50)
                    if self.cancel_xvel_learned:
                        self.neural_network.fitness_boosts.append(30)
                    self.gameover = True

            if self.drawing:
                if any(self.control_blocked):
                    display_text(screen, "Alert!", 215 ,95)
                self.allsprites.draw(screen)
                if thrusting:
                    thrust_counter -= 1
                    screen.blit(self.thrust_img, (self.lander.rect.centerx-self.thrust_img_rect.width / 2, self.lander.rect.centery + (self.lander.rect.height / 2) ))
                    if thrust_counter == 0:
                        thrusting = False

            self.show_telemetry(screen)

            if self.lander.y > 680 and self.lander.x_vel < 5 and self.lander.y_vel < 5:
                self.slow_down_learned = True

            if self.lander.y > 680 and self.lander.angle == 0:
                self.straight_angle_learned = True

            if self.lander.x_vel != 0:
                self.gain_xvel_learned = True

            if self.lander.angle > 0 and self.lander.x_vel > 0:
                self.point_against_xvel_learned = True
            elif self.lander.angle < 0 and self.lander.x_vel < 0:
                self.point_against_xvel_learned = True

            if self.gain_xvel_learned and self.point_against_xvel_learned and self.lander.x_vel < 5:
                self.xvel_slowdown_learned = True

            if self.gain_xvel_learned and self.point_against_xvel_learned and self.lander.x_vel == 0:
                self.cancel_xvel_learned = True


            if self.neural_network is not None:

                left_down = 0
                middle_down = 0
                right_down = 0

                for landing_pad in self.maxipads:
                    if abs(self.lander.x - landing_pad.rect.centerx) - landing_pad.rect.width / 2 < 750 - self.lander.y < abs(self.lander.x - landing_pad.rect.centerx)  + landing_pad.rect.width / 2:
                        if left_down < 1-(sqrt((self.lander.x - landing_pad.rect.centerx)**2 + (self.lander.y - landing_pad.rect.centery)**2)/800):
                            left_down = 1-(sqrt((self.lander.x - landing_pad.rect.centerx)**2 + (self.lander.y - landing_pad.rect.centery)**2)/800)
                    if abs(landing_pad.rect.centerx - self.lander.x)  - landing_pad.rect.width / 2 > 750 - self.lander.y > abs(landing_pad.rect.centerx - self.lander.x) + landing_pad.rect.width / 2:
                        if right_down < 1-(sqrt((self.lander.x - landing_pad.rect.centerx)**2 + (self.lander.y - landing_pad.rect.centery)**2)/800):
                            right_down = 1-(sqrt((self.lander.x - landing_pad.rect.centerx)**2 + (self.lander.y - landing_pad.rect.centery)**2)/800)
                    if landing_pad.rect.centerx - landing_pad.rect.width / 2 + self.lander.rect.width / 2 < self.lander.x < landing_pad.rect.centerx + landing_pad.rect.width / 2 - self.lander.rect.width / 2 :
                        if middle_down < 1-((landing_pad.rect.centery - self.lander.y)/750):
                            middle_down = 1-((landing_pad.rect.centery - self.lander.y)/750)

                inputs = [1/(751 - self.lander.y),
                                                self.lander.x_vel/100, self.lander.y_vel/100,
                                                self.lander.angle / 180, left_down, middle_down, right_down]
                self.neural_network.set_inputs(inputs)
                #print(inputs)

                self.neural_network.feed_forward()


if __name__ == "__main__":
    pop = Population(input_nodes=7, output_nodes=2, bias_node=True, init_random_connections=0, filename="pop_test13.json",
                 population_size=1000, num_of_bests=1, activation_function=ActivationFunctions.sigmoid, sigmoid_factor=-4.9)

    all_games = []
    active_game = 0
    all_games_over = False
    while True:
        all_games = []
        games_over = [False] * pop.population_size
        pop.save_to_file()
        for network in pop.all_networks:
            all_games.append(Game(neural_net=network))
        all_games[active_game].drawing=True
        while not all(games_over):
            clock.tick(FPS)
            screen.blit(background_image, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        all_games[active_game].drawing = False
                        active_game -= 1
                        active_game %= len(all_games)
                        all_games[active_game].drawing = True
                    elif event.key == pygame.K_3:
                        all_games[active_game].drawing = False
                        active_game += 1
                        active_game %= len(all_games)
                        all_games[active_game].drawing = True
                    elif event.key == pygame.K_RETURN:
                        if all_games[active_game].drawing:
                            for game in all_games:
                                game.drawing = False
                        else:
                            for game in all_games:
                                game.drawing = True
            for game in all_games:
                game.play()
            games_over = []
            for game in all_games:
                games_over.append(game.gameover)
            for i in range(len(games_over)):
                if all_games[0].gameover and not all_games[i].gameover:
                    all_games[active_game].drawing = False
                    active_game = i
                    all_games[active_game].drawing = True
                    break
                elif all(games_over):
                    active_game = 0
            pygame.display.set_caption("Mars Lander, Active game: %d, Gen %d" % (active_game, pop.generation))
            pygame.display.flip()
        print("evolving, gen %d" % pop.generation)
        for game in all_games:
            game.neural_network.calculate_fitness([game.score])
        pop.evolve()
