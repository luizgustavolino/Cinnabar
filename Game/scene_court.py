
import pygame
from scenery import *
from court_world import *

class SceneCourt(object):

    def __init__(self):

        self.world      = CourtWorld(960, 540)
        self.bg         = Asset("city.png", (0,0), False)
        self.court      = Asset("court.png", (0,0))
        self.court_fg   = Asset("court_fg.png", (0,0))
        self.ball       = Ball()
        self.assets     = [self.bg, self.court, self.ball, self.court_fg]

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
