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
        self.basketSize = 80
        self.space = pymunk.Space()
        self.space.gravity = (0.0, self.gravity * (-100))
        self.classification = None

        self.makeCourt()
        self.makeBasket()

        ch = self.space.add_collision_handler(0, 0)
        ch.begin = self.processCollision

    def processCollision(self, arbiter, space, data):

        if self.classification != None:
            return True

        hitPoint = True
        for shape in arbiter.shapes:

            # Verifica se tocou o chão
            if shape == self.floor:
                self.classification = "longe"
                return True

            # Verifica se algum shape não é sensor (bola e cesta são)
            if shape.sensor == False:
                hitPoint = False

        # Se for um caso sensor <-> sensor, inspeciona
        if hitPoint == True:

            # Acha o shape que é nossa bola
            for shape in arbiter.shapes:
                if shape.body == self.currentBall and shape.body.velocity.y < 0:

                    deltaDistance = abs(self.currentBall.position.x - self.basketCenter)

                    if deltaDistance < 30:
                        #print "HIT!"
                        self.classification = "acertou"
                    elif deltaDistance < 60:
                        #print "MUITO PERTO!"
                        self.classification = "muito perto"
                    elif deltaDistance < 120:
                        #print "PERTO!"
                        self.classification = "perto"
                    else:
                        #print "LONGEE!"
                        self.classification = "longe"

        return True

    def linkDebugDraw(self, screen):
        self.drawOptions = pymunk.pygame_util.DrawOptions(screen)

    def debugDraw(self):
        self.space.debug_draw(self.drawOptions)

    def step(self):
        dt = 1.0/60.0
        self.space.step(dt)

    def makeCourt(self):

        segments = []
        staticBody = self.space.static_body
        self.floor = pymunk.Segment(staticBody, (0.0, 10), (self.sw*10, 10), 0.0)
        segments.append(self.floor)
        #segments.append(pymunk.Segment(staticBody, (self.sw, -100), (self.sw, self.sh+10), 0.0))
        segments.append(pymunk.Segment(staticBody, (0, -100), (0, self.sh+10), 0.0))

        for segment in segments:
            segment.elasticity = 0.95
            segment.friction = 0.9
            self.space.add(segment)

    def makeBasket(self):
        # Cesta = dois circulos, corte vertical do aro
        radius  = 6  # espessura do aro
        size    = self.basketSize # tamanho da abertura

        # Cria os dois shapes circulares
        # e adiciona ao cenário
        for delta in [0,size]:
            staticBody = self.space.static_body
            shape = pymunk.Circle(staticBody, radius, (self.sw*0.8 + delta, self.sh*0.4))
            shape.elasticity = 0.95
            shape.friction = 0.9
            #self.space.add(shape)

        # Cria o sensor para marcar ponto
        staticBody = self.space.static_body
        line =  pymunk.Segment(staticBody,
            (0, self.sh*0.4 ),
            (self.sw*2, self.sh*0.4 ), 0.0)
        line.sensor = True
        self.basketCenter = self.sw*0.8 + size/2
        self.space.add(line)

    def throwRandomBall(self):
        self.throwBall( 45, 0.5 + random.random()/2)

    def throwBall(self, theta, force):

        # tamanho da bola: 22px
        ball_mass   = 9
        ball_radius = 22

        self.theta      = theta
        self.force      = force
        self.success    = False

        #decomposição vetorial
        force = force * self.sw * 720
        fx = force * math.cos(math.radians(theta))
        fy = force * math.sin(math.radians(theta))

        # Criamos um corpo e associamos dois circulos
        # O primeiro, maior, é para colisão com a cesta e cenário
        # O segundo, pequena, é para o sensor de passagem na cesta
        ball_moment = pymunk.moment_for_circle(ball_mass, 0, ball_radius, (0,0))
        body = pymunk.Body(ball_mass, ball_moment)
        collision_shape = pymunk.Circle(body, ball_radius, (0,0))
        collision_shape.sensor = True
        sprite_shape = pymunk.Circle(body, ball_radius, (0,0))
        sprite_shape.elasticity = 0.62
        sprite_shape.friction = 0.9

        # Posicionamos e aplicamos a força
        body.position = self.sw*0.2, self.sh*0.4
        self.currentBall = body
        self.space.add(body, sprite_shape, collision_shape)
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

            print self.world.classification

            if tick%120 == 0:
                self.world.classification = None
                self.world.throwRandomBall()

            tick += 1


#CourtGame(960, 540)

for dtheta in range(30,50):
    for df in range(500,800):

        court = CourtWorld(960, 540)
        ff = df/1000.0
        court.throwBall(dtheta, ff)

        while court.classification == None:
            court.step()

        normTheta = (dtheta-30.0)/20.0
        normff    = ((df - 500.0)/300)
        print str(normTheta) + ";" + str(normff) + ";" + str(court.classification)
