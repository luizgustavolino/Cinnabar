#!/usr/bin/python
# -*- coding: utf8 -*-
import pygame
from pygame.locals import *
from pygame.color import *
from scene_court import *

class Engine(object):

    def __init__(self):
        self.frame  = 0
        self.clock = pygame.time.Clock()
        self.makeSurface()
        self.scene = SceneCourt()

    def start(self):
        self.gameLoop()

    def makeSurface(self):
        self.sw = 960
        self.sh = 540
        flags = pygame.DOUBLEBUF | pygame.FULLSCREEN
        self.surface = pygame.display.set_mode((self.sw, self.sh), flags)
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed([KEYDOWN])

    def gameLoop(self):
        while True:

            # verifica se é preciso sair do jogo
            # ou sair do fullscreen
            events = []
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f: pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_q: return
                    else: events.append(event)

            # prepara a tela
            self.surface.fill(THECOLORS["black"])

            # roda o game loop
            if self.scene != None:
                for event in events:
                    self.scene.event(event)
                self.scene.update(self.frame)
                self.scene.draw(self.surface)

            # swap de framebuuffer
            pygame.display.flip()

            # mantem 60FPS
            self.frame += 1
            self.clock.tick(60)

            text = "FPS: {0:.2f}".format(self.clock.get_fps())
            print(text)
