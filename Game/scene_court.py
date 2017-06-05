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

        self.frame       = 0
        self.playerScore = 0
        self.iaScore     = 0
        self.state       = S_AGENE_PREP

        self.player_ready = False

        super(CourtScene, self).__init__()
        self.world = CourtWorld(sw, sh, False)
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
        self.arrow.anchor_x = -100
        self.arrow.rotation = -45
        self.arrow.position = 192+100,216
        self.arrow.opacity  = 0
        self.add(self.arrow)

        self.coach = Sprite(pyglet.resource.image('imgs/seu_mlp.png'))
        self.coach.scale = 0.3
        self.coach.position = (56, 48)
        self.add(self.coach)

        self.hints = {}

        self.hints["acertou"] = Sprite(pyglet.resource.image('imgs/hint-acertou.png'))
        self.hints["longe"] = Sprite(pyglet.resource.image('imgs/hint-longe.png'))
        self.hints["perto"] = Sprite(pyglet.resource.image('imgs/hint-perto.png'))
        self.hints["agene"] = Sprite(pyglet.resource.image('imgs/hint-agene.png'))

        for item in self.hints:
            self.hints[item].scale      = 0.25
            self.hints[item].position   = (135, 32)
            self.hints[item].opacity    = 0
            self.add(self.hints[item])

        self.changeMLPTo("agene")
        self.schedule(self.step)

    def changeMLPTo(self, name):
        for item in self.hints:
            if item == name:
                self.hints[item].stop()
                self.hints[item].do(
                    cc.actions.FadeTo(255, 0.1) + 
                    cc.actions.JumpTo((135, 32), 10, 0, duration=0.2)
                )
            else:
                self.hints[item].stop()
                self.hints[item].do(cc.actions.FadeTo(0, 0.1))

    def checkWithMLP(self):
        theta = self.arrow.rotation * -1
        force = 0.5 + engine.getStrengh()/2
        k = engine.predictionForShot((theta-10)/80, force)
        if k == engine.LONGE: self.changeMLPTo("longe")
        elif k == engine.PERTO: self.changeMLPTo("perto")
        elif k == engine.MUITO_PERTO: self.changeMLPTo("perto")
        elif k == engine.ACERTOU: self.changeMLPTo("acertou")

    def ageneShot(self):
        theta, force = engine.findBestShot(20)
        self.ball_sprite.stop()
        self.ball_sprite.do(cc.actions.FadeTo(255, 0.2))
        self.ball_body = self.world.throwBall(theta, force)

    def playerPrep(self):
        if self.player_ready == False:
            self.ball_sprite.stop()
            self.ball_sprite.do(cc.actions.FadeTo(255, 0.2))
            self.ball_body = None
            self.ball_sprite.position = 192,216
            self.arrow.stop()
            self.arrow.do(cc.actions.FadeTo(200, 0.2))
            self.player_ready = True

    def throwButtonPressed(self):
        if self.state == S_PLAYER_PREP:
            theta = self.arrow.rotation * -1
            force = 0.5 + engine.getStrengh()/2
            self.ball_body = self.world.throwBall(theta,force)
            self.state = S_PLAYER_SHOT
            engine.throwButtonPressed = False
            self.arrow.stop()
            self.arrow.do(cc.actions.FadeTo(0, 0.1))

    def step(self, dt):

        self.frame += 1

        if self.state == S_AGENE_PREP:
            self.ageneShot()
            self.state = S_AGENE_SHOT
            
        elif self.state == S_AGENE_SHOT:
            if self.world.pointMade != None:
                if self.world.pointMade == True:
                    self.iaScore += 1
                self.world.unlinkBall(60 * 2) # 3s
                self.ball_sprite.do(
                    cc.actions.Delay(1.0) +
                    cc.actions.FadeTo(0, 0.4)
                )
                self.state = S_PLAYER_WAITING_COURT

        elif self.state == S_PLAYER_WAITING_COURT:
            if self.world.ready() == True:
                self.player_ready = False
                engine.throwButtonPressed = False
                self.state = S_PLAYER_PREP

        elif self.state == S_PLAYER_PREP:

            self.playerPrep()
            if engine.throwButtonPressed == True:
                self.throwButtonPressed()
            elif self.frame % 10 == 0:
                self.checkWithMLP()

        elif self.state == S_PLAYER_SHOT:
            if self.world.pointMade != None:
                if self.world.pointMade == True:
                    self.playerScore += 1
                self.world.unlinkBall(60 * 2) # 3s
                self.ball_sprite.do(
                    cc.actions.Delay(1.0) +
                    cc.actions.FadeTo(0, 0.4)
                )
                self.state = S_AGENE_WAITING_COURT

        elif self.state == S_AGENE_WAITING_COURT:
            if self.world.ready() == True:
                self.changeMLPTo("agene")
                self.state = S_AGENE_PREP


        self.world.step()

        rawRotation = engine.getPitch() * 1.1
        if rawRotation > -10: rawRotation = -10
        if rawRotation < -70: rawRotation = -70
        self.arrow.rotation = rawRotation
        self.arrow.scale = 0.5 + engine.getStrengh()/2.0

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

        if engine.rumble > 1:
            engine.wiimote.enable_rumble(1)
            engine.rumble -= 1
        elif engine.rumble == 1:
            engine.wiimote.enable_rumble(0)
            engine.rumble -= 1

