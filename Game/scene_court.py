#!/usr/bin/python
# -*- coding: utf8 -*-

import pyglet, math
from pyglet.gl import *
import cocos as cc
from cocos.sprite import Sprite
from court_world import CourtWorld
import engine 

class CourtScene(cc.layer.Layer):

    def __init__(self):

        sw = 960
        sh = 540
        hsw = 480
        hsh = 270

        super(CourtScene, self).__init__()
        self.world = CourtWorld(sw, sh)
        self.ball_body = None

        city_image = pyglet.resource.image('imgs/city.png')
        city_sprite = Sprite(city_image)
        city_sprite.position = hsw,hsh
        self.add(city_sprite)

        cout_bg_image = pyglet.resource.image('imgs/court_bg.png')
        court_bg_sprite = Sprite(cout_bg_image)
        court_bg_sprite.position = hsw,hsh
        self.add(court_bg_sprite)

        cout_image = pyglet.resource.image('imgs/court.png')
        court_sprite = Sprite(cout_image)
        court_sprite.position = hsw,hsh
        self.add(court_sprite)

        self.ball_image = pyglet.resource.image('imgs/ball.png')
        self.ball_sprite = Sprite(self.ball_image)
        self.ball_sprite.position = 100,100
        self.add(self.ball_sprite)

        cout_fg_image = pyglet.resource.image('imgs/court_fg.png')
        court_fg_sprite = Sprite(cout_fg_image)
        court_fg_sprite.position = hsw,hsh
        self.add(court_fg_sprite)

        self.world.linkDebugDraw()
        self.schedule(self.step)
        self.ageneShot()

    def ageneShot(self):
        theta, force = engine.findBestShot(15)
        self.ball_body = self.world.throwBall(theta, force)

    def step(self, dt):
        
        self.world.step()

        if self.ball_body != None:
            self.ball_sprite.position = self.ball_body.position
            self.ball_sprite.rotation = math.degrees(2 * 3.14 - self.ball_body.angle)
