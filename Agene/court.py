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

        self.makeCourt()
        self.makeBasket()

        ch = self.space.add_collision_handler(0, 0)
        ch.begin = self.processCollision

    def processCollision(self, arbiter, space, data):

        trues = 0
        for shape in arbiter.shapes:
            if shape.sensor == True:
                trues += 1

        if trues == 2:
            print("BANG!")

        return True

    def linkDebugDraw(self, screen):
        self.drawOptions = pymunk.pygame_util.DrawOptions(screen)

    def debugDraw(self):
        self.space.debug_draw(self.drawOptions)

    def step(self):
        dt = 1.0/60.0
        self.space.step(dt)

    def makeCourt(self):

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
        radius  = 6
        size    = 80

        for delta in [0,size]:
            staticBody = self.space.static_body
            shape = pymunk.Circle(staticBody, radius, (self.sw*0.8 + delta, self.sh*0.4))
            shape.elasticity = 0.95
            shape.friction = 0.9
            self.space.add(shape)

        staticBody = self.space.static_body
        line =  pymunk.Segment(staticBody,
            (self.sw*0.8, self.sh*0.4 - radius),
            (self.sw*0.8 + size, self.sh*0.4 - radius), 0.0)
        line.sensor = True
        self.space.add(line)

    def throwRandomBall(self):
        self.throwBall( 45, random.random())

    def throwBall(self, theta, force):

        #decomposição vetorial
        force = force * self.sw * 500
        fx = force * math.cos(math.radians(theta))
        fy = force * math.sin(math.radians(theta))

        ball_mass   = 9
        ball_radius = 22

        ball_moment = pymunk.moment_for_circle(ball_mass, 0, ball_radius, (0,0))
        body = pymunk.Body(ball_mass, ball_moment)
        shape = pymunk.Circle(body, ball_radius, (0,0))
        shape.elasticity = 0.62
        shape.friction = 0.9
        body.position = self.sw*0.2, self.sh*0.4

        collision_ball_moment = pymunk.moment_for_circle(1, 0, 2, (0,0))
        collision_body = pymunk.Body(1, collision_ball_moment)
        collision_shape = pymunk.Circle(collision_body, 2, (0,0))
        collision_shape.sensor = True
        collision_body.position = self.sw*0.2, self.sh*0.4

        balls = pymunk.PinJoint(body, collision_body, (0,0))
        balls.distance = 0

        self.space.add(body, shape, collision_body, collision_shape)
        self.space.add(balls)

        body.apply_force_at_local_point( (fx, fy), (0,0))

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
            if tick%40 == 0:
                self.world.throwRandomBall()

c = CourtGame(960,540)

## for i in range(0,1000):
##    print("test", i)
##    court = CourtWorld(960, 540)
##    court.throwRandomBall()
##    for i in range(0,300):
##        court.step()
