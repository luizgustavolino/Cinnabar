#!/usr/bin/python
# -*- coding: utf8 -*-

# ora pois!

from court import CourtWorld

court = CourtWorld(960, 540)
court.throwBall(45, 0.6) # 45 graus, 60% de força

while court.classification == None:
    court.step()

print "no que deu: " + court.classification
