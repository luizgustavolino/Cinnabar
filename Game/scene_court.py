#!/usr/bin/python
# -*- coding: utf8 -*-
import pyglet
import cocos as cc

class CourtScene(cc.layer.Layer):

    def __init__(self):

        super(CourtScene, self).__init__()

        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        label = cc.text.Label('Hello, World!',
                                font_name='Times New Roman',
                                font_size=32,
                                anchor_x='center',
                                anchor_y='center')
        label.position = 320, 240
        self.add(label)


"""
import pygame
from scenery import *
from court_world import *

class SceneCourt(object):

    def __init__(self):

        self.world      = CourtWorld(960, 540)
        self.bg         = Asset("city.png", (0,0), False)
        self.court      = Asset("court.png", (0,0))
        self.court_bg   = Asset("court_bg.png", (0,0))
        self.court_fg   = Asset("court_fg.png", (0,0))
        self.ball       = Ball()
        self.assets     = [self.bg, self.court_bg, self.court, self.ball, self.court_fg]

    def update(self, frame):
        for asset in self.assets: asset.doUpdate(frame)
        self.world.step()

        if frame%220 == 0:
            newBall = self.world.throwRandomBall()
            self.ball.attachBody(newBall)

    def event(self, ev):
        for asset in self.assets: asset.doEvent(ev)

    def draw(self, surface):
        for asset in self.assets: asset.doDraw(surface)
        #self.world.linkDebugDraw(surface)
        #self.world.debugDraw()
"""