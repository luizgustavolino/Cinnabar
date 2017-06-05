#!/usr/bin/python
# -*- coding: utf8 -*-
import pyglet, sys, time, os
import wiiuse, wii
import cocos as cc
from scene_court import CourtScene
from ia_mlp import *
import ia_agene as agene

##### Game loop e cenas

sw = 960
sh = 540

pitch   = 0
strengh = 0.5
rumble  = 0
throwButtonPressed = None


def start():
    acquireWiiRemote()
    runGameScene()

def quit():
    print "desconectando wiimote..."
    wii.quit()
    print "done!"

def runGameScene():
    cc.director.director.init(width=sw, height=sh)
    engine_scene = CourtScene()
    cc.director.director.run(cc.scene.Scene(engine_scene))

#### Rede Multilayer Perceptron

LONGE       = 0 
PERTO       = 2
MUITO_PERTO = 4
ACERTOU     = 1

mlp = MLP([2,8,8,4], 0.0, True)

def predictionForShot(theta, force):
    return mlp.run([theta,force])

##### Algoritmo Genético
def findBestShot(loopLimit = 5):
    return agene.genetic(200, 0.01, loopLimit)

##### Acesso ao Wiimote
wiimote = None

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
    global wiimote
    wiimote = wm

piches  = []

def getPitch():
    # Tiramos a média dos valores para suavizar o sinal
    return reduce(lambda x, y: x + y, piches) / len(piches)

def appendPitch(newP):
    # mantendo histórico de 30 sinais
    piches.append(newP)
    if len(piches) > 30:
        piches.pop(0)

def getStrengh():
    if strengh > 1.0: return 1.0
    if strengh < 0.0: return 0.0
    return strengh
