#!/usr/bin/python
# -*- coding: utf8 -*-

import random

from court_world import CourtWorld
from operator import itemgetter

randomNumber = 0
group = []
matingPool = []

#gera cromossomos com carga genetica aleatoria
def initCromosomes(n):

	#indice 0 = x
	#indice 1 = y
	#indice 2 = angulo
	#indice 3 = forca
	#indice 4 = fitness

	for x in xrange(0, n):
 		cromosome = []
 		for y in xrange(0, 5):
 			if y == 2:
				cromosome.append(random.randint(40,80))
			elif y == 4:
				cromosome.append(None)
			else: 
				cromosome.append(random.random())
		group.append(cromosome)

#define os melhores cromossomos
def fitness():

	for x in group:
		court = CourtWorld(960, 540)
		court.throwBall(x[2], x[3])
		
		while court.classification == None:	
	   		court.step()
	   		
	   	if court.classification == "acertou":
	   		x[4] = 0
	   	elif court.classification == "muito perto":
	   		x[4] = 1
	   	elif court.classification == "perto":
	   		x[4] = 2
	   	elif court.classification == "longe":
	   		x[4] = 3
	   	
	   	# print "angulo:", x[2],"forca:", x[3] ,court.classification

#escolhe os pais de uma nova geracao,
def naturalSelection():

	matingPool[:] = []
	aux = sorted(group, key=itemgetter(4))

	for x in xrange(0, len(group) / 2):
		matingPool.append(aux[x])
	group[:] = []

#cruza os dados geneticos de diterations cromossomos para gerar nova geracao 
def crossover(prob):

	# randomNumber gera o valor que dira em que indice do cromossomo ocorrera a troca
	for x in xrange(0, len(matingPool) * 2):
		randomNumber = random.randint(1, len(matingPool[0]) - 1)
		a = random.randint(0, len(matingPool) -1)
		b = random.randint(0, len(matingPool) -1)

		if random.random() >= 0.5:
			matingPool[a][2] = matingPool[b][2]
		else: 
			matingPool[a][3] = matingPool[b][3]

		if random.random() <= prob:
			cromosome = []
	 		for y in xrange(0, 5):
	 			if y == 2:
					cromosome.append(random.randint(0,90))
				elif y == 4:
					cromosome.append(None)
				else: 
					cromosome.append(random.random())
				group.append(cromosome)
		else:
			if random.random > 0.5:
				group.append(matingPool[a])
			else:
				group.append(matingPool[b])

def genetic(popSize, mutationChance, loopLimit = -1):

	initCromosomes(popSize)
	iteration = 0
	
	while True:

		fitness()
		naturalSelection()
		iteration += 1

		if matingPool[0][4] == 0 or iteration == loopLimit:
			break
		crossover(mutationChance)

	return (matingPool[0][2] , matingPool[0][3])
