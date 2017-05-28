#!/usr/bin/python
# -*- coding: utf8 -*-
import pygame
from pygame.locals import *
from pygame.color import *
from scene_court import *

class Engine(object):

    def __init__(self):
        self.scene = SceneCourt()
        self.clock = pygame.time.Clock()
        self.makeSurface()

    def start(self):
        self.gameLoop()

    def makeSurface(self):
        self.sw = 960
        self.sh = 540
        self.surface = pygame.display.set_mode((self.sw, self.sh),
                        pygame.DOUBLEBUF | pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

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
            self.surface.fill(THECOLORS["white"])

            # roda o game loop
            if self.scene != None:
                for event in events:
                    self.scene.event(event)
                self.scene.update()
                self.scene.draw(self.surface)

            # swap de framebuuffer
            pygame.display.flip()

            # mantem 60FPS
            self.clock.tick(60)
