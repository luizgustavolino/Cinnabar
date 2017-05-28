
import pygame
from scenery import *

class SceneCourt(object):


    def __init__(self):

        self.bg = Asset("city.png", (0,0))
        self.court = Asset("court.png", (0,0))
        self.assets = [self.bg, self.court]

    def update(self):
        for asset in self.assets: asset.doUpdate(0)

    def event(self, ev):
        for asset in self.assets: asset.doEvent(ev)

    def draw(self, surface):
        for asset in self.assets: asset.doDraw(surface)
