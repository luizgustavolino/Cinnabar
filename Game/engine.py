#!/usr/bin/python
# -*- coding: utf8 -*-
import pyglet, sys, time, os
import wiiuse, wii
import cocos as cc
from scene_court import CourtScene
from mlp import *

sw = 960
sh = 540

mlp = MLP([2,4,4,8], 0.0, True)

def start():
    #acquireWiiRemote()

def runGameScene():
    cc.director.director.init(width=sw, height=sh)
    cc.director.director.run(cc.scene.Scene(CourtScene()))

def acquireWiiRemote():

    print "esperando wiimotes..."
    print "segure o botão 1 & 2 ao mesmo tempo"

    wii.init(1,5)

    if wii.get_count() == 0:
        print 'no wiimotes found!'
        sys.exit(1)

    wm = wii.Wiimote(0)
    wm.enable_ir(1, vres=(512,512))
    wm.enable_accels(1)

    import pygame
    pygame.init()
    pygame.display.set_mode((512,512))
    
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print 'quiting'
                wii.quit()
                run = False
                break

        pygame.display.flip()
        pygame.time.wait(10)


"""
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
"""


"""
    print "esperando wiimotes..."
    print "segure o botão 1 & 2 ao mesmo tempo"

    wii.init(1,5)

    if wii.get_count() == 0:
        print 'no wiimotes found!'
        sys.exit(1)

    wm = wii.Wiimote(0)
    wm.enable_accels(1)
    wm.enable_ir(1, vres=(512,512))

    pygame.init()
    pygame.display.set_mode((512,512))
    
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print 'quiting'
                wii.quit()
                run = False
                break
            elif event.type in [ wii.WIIMOTE_BUTTON_PRESS, wii.NUNCHUK_BUTTON_PRESS ]:
                print event.button, 'pressed on', event.id


        pygame.display.flip()
        pygame.time.wait(10)

    """
    #start()
    #runGameScene()