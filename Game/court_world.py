#!/usr/bin/python
# -*- coding: utf8 -*-

import math, sys, random

import pymunk
import pymunk.pyglet_util
from pymunk import Vec2d

class CourtWorld(object):

    def __init__(self, sw, sh):

        self.sw = sw
        self.sh = sh
        self.gravity = 9.0
        self.basketSize = 50
        self.space = pymunk.Space()
        self.space.gravity = (0.0, self.gravity * (-100))
        self.classification = None
        self.holographicBasket = False
        self.drawOptions = None
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
                        self.classification = "acertou"
                    elif deltaDistance < 60:
                        self.classification = "muito perto"
                    elif deltaDistance < 120:
                        self.classification = "perto"
                    else:
                        self.classification = "longe"

        return True

    def linkDebugDraw(self):
        if self.drawOptions == None:
            self.drawOptions = pymunk.pyglet_util.DrawOptions()

    def debugDraw(self):
        self.space.debug_draw(self.drawOptions)

    def step(self):
        dt = 1.0/80.0
        self.space.step(dt)

    def makeCourt(self):

        segments = []
        staticBody = self.space.static_body
        self.floor = pymunk.Segment(staticBody, (0.0, 115), (self.sw*10, 115), 0.0)
        segments.append(self.floor)
        segments.append(pymunk.Segment(staticBody, (self.sw, -100), (self.sw, self.sh+10), 0.0))
        segments.append(pymunk.Segment(staticBody, (0, -100), (0, self.sh+10), 0.0))

        for segment in segments:
            segment.elasticity  = 0.60
            segment.friction    = 0.90
            self.space.add(segment)

    def makeBasket(self):
        # Cesta = dois circulos, corte vertical do aro
        radius  = 3  # espessura do aro
        size    = self.basketSize # tamanho da abertura

        # Cria os dois shapes circulares
        # e adiciona ao cenário
        if self.holographicBasket == False:
            for delta in [0,size]:
                staticBody = self.space.static_body
                shape = pymunk.Circle(staticBody, radius, (759 + delta, 310))
                shape.elasticity = 0.95
                shape.friction = 0.9
                self.space.add(shape)

        # Cria o fundo da cesta
        staticBody = self.space.static_body
        backboard = pymunk.Poly(staticBody, [
              (826, 540-258),
              (834, 540-258),
              (834, 540-124),
              (826, 540-124)
        ])

        backboard.elasticity = 0.95
        backboard.friction = 0.9
        self.space.add(backboard)

        # Cria o sensor para marcar ponto
        staticBody = self.space.static_body
        line =  pymunk.Segment(staticBody,
            (0, 310 ),
            (self.sw*2, 310), 0.0)
        line.sensor = True
        self.basketCenter = 759 + size/2
        self.space.add(line)

    def throwRandomBall(self):
        return self.throwBall( 45, 0.5 + random.random()/2)

    def throwBall(self, theta, force):

        # tamanho da bola: 18px
        ball_mass   = 10
        ball_radius = 18

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

        return body
