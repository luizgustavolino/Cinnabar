#!/usr/bin/python
# -*- coding: utf8 -*-

import math, sys, random

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

class CourtWorld(object):

    def __init__(self, sw, sh):

        self.sw = sw
        self.sh = sh
        self.gravity = 9.0
        self.space = pymunk.Space()
        self.space.gravity = (0.0, self.gravity * (-100))

        self.makeFloor()
        self.makeBasket()

    def linkDebugDraw(self, screen):
        self.drawOptions = pymunk.pygame_util.DrawOptions(screen)

    def debugDraw(self):
        self.space.debug_draw(self.drawOptions)

    def step(self):
        dt = 1.0/60.0
        self.space.step(dt)

    def makeFloor(self):

        staticBody = self.space.static_body
        line =  pymunk.Segment(staticBody, (0.0, 10), (self.sw, 10), 0.0)
        line.elasticity = 0.95
        line.friction = 0.9
        self.space.add(line)

        wall =  pymunk.Segment(staticBody, (self.sw, -100), (self.sw, self.sh+10), 0.0)
        wall.elasticity = 0.95
        wall.friction = 0.9
        self.space.add(wall)

    def makeBasket(self):

        for delta in [0,80]:
            staticBody = self.space.static_body
            shape = pymunk.Circle(staticBody, 6, (self.sw*0.8 + delta, self.sh*0.4))
            shape.elasticity = 0.95
            shape.friction = 0.9
            self.space.add(shape)

    def throwRandomBall(self):
        self.makeBall(
            199000 + random.randint(-10000,10000),
            414200 + random.randint(-10000,10000)
        )

    def makeBall(self, vx, vy):

        ball_mass   = 9
        ball_radius = 22
        ball_moment = pymunk.moment_for_circle(ball_mass, 0, ball_radius, (0,0))
        body = pymunk.Body(ball_mass, ball_moment)
        body.position = self.sw*0.2, self.sh*0.4

        shape = pymunk.Circle(body, ball_radius, (0,0))
        shape.elasticity = 0.62
        shape.friction = 0.9
        self.space.add(body, shape)

        body.apply_force_at_local_point( (vx, vy), (0,0))

class CourtGame(object):

    def __init__(self, sw, sh):

        pygame.init()
        self.sw = sw
        self.sh = sh
        self.screen = pygame.display.set_mode((sw, sh))
        self.running = True
        self.clock = pygame.time.Clock()
        self.makeWorld()
        self.gameLoop()

    def makeWorld(self):
        self.world = CourtWorld(self.sw, self.sh)
        self.world.linkDebugDraw(self.screen)

    def gameLoop(self):

        print("SHOW TIME!")
        tick = 0

        while True:

            for event in pygame.event.get():
                if event.type == QUIT:
                    return

            self.world.step()
            self.screen.fill(THECOLORS["white"])
            self.world.debugDraw()
            pygame.display.flip()
            self.clock.tick(50)

            tick += 1
            if tick%120 == 0:
                self.world.throwRandomBall()

c = CourtGame(960,540)
