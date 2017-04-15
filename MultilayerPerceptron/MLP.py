#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import math

class MLP (object):

    def __init__(self, layout, expected = None):
        # cria uma rede MLP seguindo a quantidade
        # de neuronios do layout (vetor de ints)

        print "Criando MLP, layout:" + str(layout)

        self.layers  = [] # layers[0]  -> input layer, demais são hidden layers
        self.outputs = []
        layersCount  = len(layout)

        # Criando os layers, inputs,neuronios e outputs
        # enumerate([2,2,1]) -> [(0,2),(1,2),(2,1)]
        for i, nCount in enumerate(layout):
            currentLayer = []
            for j in range(0, nCount):
                if i == 0:
                    print "Criando neuronio "+str(j)+" da input layer"
                    tag = "iln"+str(j)
                    currentLayer.append(Input(tag))
                elif i < layersCount:
                    print "Criando neuronio "+str(j)+" da layer "+str(i)
                    tag = "hl"+str(i)+"n"+str(j)
                    currentLayer.append(Neuron(tag))

            self.layers.append(currentLayer)

        # Criando as sinapses entre os neuronios
        for i, layer in enumerate(self.layers):

            if i < layersCount - 1:
                nextLayer = self.layers[i+1]
                for neuron in layer:
                    for target in nextLayer:
                        synapse = Synapse(neuron,target)
                        neuron.synapsesOut.append(synapse)
                        target.synapsesIn.append(synapse)
            else:
                for neuron in layer:
                    out = Output("output", neuron)
                    neuron.synapsesOut.append(out)
                    self.outputs.append(out)

    def forward(self, inputs):

        # Avisa as sinapses de entrada e,
        # após os eventos em cascata, colhe a saida
        print "-------------------------"
        print "Iniciando passo forward"
        print "-------------------------"
        for (j, inputNode) in enumerate(self.layers[0]):
            inputNode.receiveSignal(inputs[j])

        # resultado esta no vetor de outputs

class Input (object):

    def __init__(self, tag):
        # Inputs são os receptores na camada de entrada
        # representam o atributo da instancia
        # Não tem sinapseIn, só sinapseOut
        self.tag         = tag
        self.synapsesOut = []

    def receiveSignal(self, signalValue):
        # a input layer não tem somatório de valores
        # ela recebe de uma fonte somente, então para já ativar
        # o próximo passo
        for synapse in self.synapsesOut: synapse.signal(signalValue)

class Output (object):

    def __init__(self, tag, source):
        # Outputs são o resultado do processamento
        # representam uma classe na classificação
        # Não tem sinapseOut, só sinapseIn
        # também não tem peso, recebe sinal integralmente
        self.source     = source
        self.synapsesIn = []
        self.tag        = tag

    def signal(self, signalValue):
        print("Output: " + str(signalValue))

class Neuron (object):

    def __init__(self, tag):
        # cria um neuronio, que tera sinapses
        # de entrada e saida
        self.tag                = tag
        self.signalsReceived    = 0
        self.accumulatedWeight  = 0.0
        self.bias               = Bias(self)
        self.synapsesIn         = [self.bias]
        self.synapsesOut        = []

    def receiveSignal(self, signalValue, fromTag):

        print(" (" + fromTag + ") Recebendo da sinapse sinal: " + str(signalValue))
        self.signalsReceived += 1
        self.accumulatedWeight += signalValue

        if self.signalsReceived == len(self.synapsesIn) -1:
            # quando n-1 neurônios entragaram o sinal
            # significa que só falta o bias
            self.bias.signal()

        elif self.signalsReceived == len(self.synapsesIn):
            # todos sinais foram recebidos e somados!
            # agora é só calcular a sigmoid e passar adiante
            # também é preciso resetar para se preparar
            sigmoidData = self.sigmoid()
            print("# " + self.tag + " saturado com sigmoid " + str(sigmoidData))
            for synapse in self.synapsesOut: synapse.signal(sigmoidData)
            self.accumulatedWeight = 0
            self.signalsReceived   = 0

    def sigmoid(self):
        sigmoidValue = 1 / (1+math.exp(self.accumulatedWeight * -1))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

class Synapse (object):

    def __init__(self, source, destiny):
        # cria uma sinapse, que tem um neuronio
        # de entrada e um de saida
        self.source = source
        self.destiny = destiny
        self.weight = random.uniform(-1,1)
        print "Sinapse criada entre "+source.tag+ " e "+destiny.tag

    def signal(self,input):
        # recebe um estimulo e repassa
        # para outro neuronio
        self.destiny.receiveSignal(self.weight * input, self.source.tag +" -> "+ self.destiny.tag)

class Bias (object):

    def __init__(self, destiny):
        # similar a Sinapse, mas sempre tem
        # 1 como entrada
        self.destiny = destiny
        self.weight = random.uniform(-1,1)

    def signal(self):
        self.destiny.receiveSignal(self.weight * 1, "bias")
