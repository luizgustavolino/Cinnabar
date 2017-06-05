#!/usr/bin/python
# -*- coding: utf8 -*-

import pyglet, math
from pyglet.gl import *
import cocos as cc
from cocos.sprite import Sprite
from court_world import CourtWorld
import engine 

S_AGENE_PREP                = 1
S_AGENE_SHOT                = 2
S_PLAYER_WAITING_COURT      = 3
S_PLAYER_PREP               = 4
S_PLAYER_SHOT               = 5
S_AGENE_WAITING_COURT       = 6

class CourtScene(cc.layer.Layer):

    def __init__(self):

        sw = 960
        sh = 540
        hsw = 480
        hsh = 270

        self.playerScore = 0
        self.iaScore     = 0
        self.state       = S_AGENE_PREP

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

        self.ball_shadow_image = pyglet.resource.image('imgs/shadow.png')
        self.ball_shadow_sprite = Sprite(self.ball_shadow_image)
        self.ball_shadow_sprite.position = 192,115
        self.add(self.ball_shadow_sprite)

        self.ball_image = pyglet.resource.image('imgs/ball.png')
        self.ball_sprite = Sprite(self.ball_image)
        self.ball_sprite.position = 192,216
        self.add(self.ball_sprite)

        cout_fg_image = pyglet.resource.image('imgs/court_fg.png')
        court_fg_sprite = Sprite(cout_fg_image)
        court_fg_sprite.position = hsw,hsh
        self.add(court_fg_sprite)
        
        self.arrow = Sprite(pyglet.resource.image('imgs/arrow.png'))
        self.arrow.position = self.ball_sprite.position
        self.arrow.anchor_y = -100
        self.arrow.rotation = 45
        self.add(self.arrow)

        self.schedule(self.step)

    def ageneShot(self):
        theta, force = engine.findBestShot(20)
        self.ball_sprite.stop()
        self.ball_sprite.do(cc.actions.FadeTo(255, 0.2))
        self.ball_body = self.world.throwBall(theta, force)

    def step(self, dt):

        if self.state == S_AGENE_PREP:
            self.ageneShot()
            self.state = S_AGENE_SHOT
            
        elif self.state == S_AGENE_SHOT:
            if self.world.pointMade != None:
                if self.world.pointMade == True:
                    self.iaScore += 1
                self.world.unlinkBall(60 * 3) # 3s
                self.ball_sprite.do(
                    cc.actions.Delay(1.2) +
                    cc.actions.FadeTo(0, 0.6)
                )
                self.state = S_PLAYER_WAITING_COURT

        elif self.state == S_PLAYER_WAITING_COURT:
            if self.world.ready() == True:
                self.state = S_AGENE_PREP


        self.world.step()
        self.arrow.rotation += 1

        if self.ball_body != None:
            self.ball_sprite.position = self.ball_body.position
            self.ball_sprite.rotation = math.degrees(2 * 3.1415 - self.ball_body.angle)
            
            px, py = self.ball_sprite.position
            dx = (py - 132) / 10
            self.ball_shadow_sprite.position = (px - dx, 112)

            sc = py/500
            self.ball_shadow_sprite.scale    = 0.3 + sc
            
            op = (self.ball_sprite.opacity/2) - 100
            if op < 0: op = 0
            self.ball_shadow_sprite.opacity  = op 