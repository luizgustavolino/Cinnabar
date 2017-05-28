#!/usr/bin/python
# -*- coding: utf8 -*-

import pygame, os

class Asset(pygame.sprite.Sprite):

    def __init__(self, imageName, position):

        pygame.sprite.Sprite.__init__(self)
        self.imagePath = imageName
        self.imagePath = os.path.join( "imgs", self.imagePath )
        self.image = pygame.image.load( self.imagePath )
        self.rect = self.image.get_rect()

    def doEvent(self, ev):
        pass

    def doUpdate(self, dt):
        pass

    def doDraw(self, surface):
        surface.blit( self.image, self.rect)
