#!/usr/bin/python
# -*- coding: utf8 -*-

import pygame, os, math
import pymunk

class Asset(pygame.sprite.Sprite):

    def __init__(self, imageName, position = (0,0), use_alpha = True):

        pygame.sprite.Sprite.__init__(self)
        self.imagePath = imageName
        self.imagePath = os.path.join( "imgs", self.imagePath )

        if use_alpha == True:
            self.image = pygame.image.load( self.imagePath ).convert_alpha()
        else:
            self.image = pygame.image.load( self.imagePath ).convert()

        self.rect = self.image.get_rect()
        self.original = self.image

    def rotate(self, angle):

        pos_org = ( self.rect.center[0] - self.original.get_rect().width / 2,
                    self.rect.center[1] - self.original.get_rect().height / 2)
        self.image = pygame.transform.rotate(self.original, angle)
        pos_new = ( pos_org[0] - self.image.get_rect().width / 2,
                    pos_org[1] - self.image.get_rect().height / 2)
        self.rect.center = pos_new

    def doEvent(self, ev):
        pass

    def doUpdate(self, dt):
        pass

    def doDraw(self, surface):
        surface.blit( self.image, self.rect)


class Ball(Asset):

    def __init__(self):
        Asset.__init__(self, "ball.png")
        self.body = None

    def attachBody(self, body):
        self.body = body

    def doUpdate(self, dt):
        if self.body != None:
            x, y    = self.body.position
            r       = self.body.angle
            self.rect.centerx = 18*2 + x
            self.rect.centery = 18*2 + 540 - y
            self.rotate(math.degrees(r))
