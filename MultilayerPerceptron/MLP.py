#!/usr/bin/python
# -*- coding: utf8 -*-

import random

class MLP (object):

    def __init__(self, layout):
        # cria uma rede MLP seguindo a quantidade
        # de neuronios do layout (vetor de ints)

        print "Criando MLP, layout:" + str(layout)

        self.layers = []
        layersCount = len(layout)

        # Criando os layers, inputs,neuronios e outputs
        for i, nCount in enumerate(layout):
            currentLayer = []
            for j in range(0, nCount):
                if i == 0:
                    print "Criando Neuronio "+str(j)+" da input layer"
                    tag = "iln"+str(j)
                    currentLayer.append(Input(tag))
                elif i < layersCount-1:
                    print "Criando Neuronio "+str(j)+" da layer "+str(i)
                    tag = "hl"+str(i)+"n"+str(j)
                    currentLayer.append(Neuron(tag))
                else:
                    print "Criando Neuronio "+str(j)+" da output layer"
                    tag = "oln"+str(j)
                    currentLayer.append(Output(tag))
            self.layers.append(currentLayer)

        # Criando as sinapses entre os neuronios
        for i, layer in enumerate(self.layers):
            if i == layersCount - 1: continue
            nextLayer = self.layers[i+1]
            for neuron in layer:
                for target in nextLayer:
                    synapse = Synapse(neuron,target)
                    neuron.synapsesOut.append(synapse)
                    target.synapsesIn.append(synapse)

    def forward(self, inputs):
        # Avisa as sinapses de entrada e espera a saida
        print "Iniciando passo forward"

class Input (object):

    def __init__(self, tag):
        # Inputs são os receptores na camada de entrada
        # representam o atributo da instancia
        # Não tem sinapseIn, só sinapseOut
        self.tag         = tag
        self.synapsesOut = []

class Output (object):

    def __init__(self, tag):
        # Outputs são o resultado do processamento
        # representam uma classe na classificação
        # Não tem sinapseOut, só sinapseIn
        self.tag = tag
        self.synapsesIn = []

class Neuron (object):

    def __init__(self, tag):
        # cria um neuronio, que tera sinapses
        # de entrada e saida
        self.tag                = tag
        self.signalsReceived    = 0
        self.accumulatedWeight  = 0.0
        self.bias               = Bias()
        self.synapsesIn         = []
        self.synapsesOut        = []

    def receiveSignal(self, signalValue):
        print("Recebendo sinal no neuronio " + self.tag)
        self.signalsReceived += 1
        self.accumulatedWeight += signalValue
        if self.signalsReceived == len(self.sinapseIn) -1:
            self.accumulatedWeight +=
            print("Neuronio saturado " + self.tag)

    def sigmoid():
        return 1 / (1+math.exp(self.accumulatedWeight))

class Synapse (object):

    def __init__(self, source, destiny):
        # cria uma sinapse, que tem um neuronio
        # de entrada e um de saida
        self.src = source
        self.dst = destiny
        self.weight = random.uniform(-1,1)
        print "Sinapse criada entre "+source.tag+ " e "+destiny.tag

    def signal(self,input):
        # recebe um estimulo e repassa
        # para outro neuronio
        self.dst.receiveSignal(self.weight * input)

class Bias (object):

    def __init__(self):
        # similar a Sinapse, mas sempre tem
        # 1 como entrada
        pass

MLP([2,1,1])
