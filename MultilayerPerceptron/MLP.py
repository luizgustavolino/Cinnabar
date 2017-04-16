#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import math

class MLP (object):

    def __init__(self, layout):
        # cria uma rede MLP seguindo a quantidade
        # de neuronios do layout (vetor de ints)

        print "Criando MLP, layout:" + str(layout)

        self.layers  = [] # layers[0]  -> input layer, demais são hidden layers
        self.outputs = []

        self.n                  = 0  # Contagem de forwards, com learning
        self.instantErrorLog    = [] # Lista de erros instantâneos para cada forward de learning
        self.learningRate       = 0.1 # ƞ
        self.a                  = 1.0 #

        layersCount  = len(layout)

        # Criando os layers, inputs,neuronios e outputs
        # enumerate([2,2,1]) -> [(0,2),(1,2),(2,1)]
        for i, nCount in enumerate(layout):
            currentLayer = []
            for j in range(0, nCount):
                if i == 0:
                    #print "Criando neuronio "+str(j)+" da input layer"
                    tag = "iln"+str(j)
                    currentLayer.append(Input(tag))

                elif i < layersCount:
                    #print "Criando neuronio "+str(j)+" da layer "+str(i)
                    tag = "hl"+str(i)+"n"+str(j)
                    hlNeuron = Neuron(tag, self.a, self.learningRate)
                    currentLayer.append(hlNeuron)
                    if i == layersCount -1:
                        hlNeuron.insideOutputLayer = True

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

    def forward(self, inputs, expectedOutputs, learningMode = True):

        # Configura as saidas para o valor esperado
        for i, output in enumerate(self.outputs):
            output.expectedValue = expectedOutputs[i]

        # Prepara os neuronios para um novo forward
        for layer in self.layers:
            for neuron in layer: neuron.warmUp()

        # Avisa as sinapses de entrada e,
        # após os eventos em cascata, colhe a saida
        #print "-------------------------"
        #print "Iniciando passo forward"
        #print "-------------------------"

        for (j, inputNode) in enumerate(self.layers[0]):
            inputNode.receiveSignal(inputs[j])

        if learningMode == True:

            self.instantErrorLog.append(self.instantaneousErrorEnergy())
            self.n += 1

            #print "-------------------------"
            #print "Iniciando passo backward"
            #print "-------------------------"

            for i,layer in enumerate(reversed(self.layers[1:])):
                #print("Aplicando correção nas sinapses da layer " + str(i))
                for neuron in layer: neuron.weightFix()

    def instantaneousErrorEnergy(self):
        #  ℰ(n) = (1/2) Σ(ej(n))^2
        total = 0
        for output in self.outputs: total += output.error*output.error
        return total * 0.5

    def averageSquaredErrorEnergy(self):
        # ℰav = (1/N) Σ ℰ(n)
        result = 0
        for instant in self.instantErrorLog: result += instant
        return result * (1.0/len(self.instantErrorLog))


class Input (object):

    def __init__(self, tag):
        # Inputs são os receptores na camada de entrada
        # representam o atributo da instancia
        # Não tem sinapseIn, só sinapseOut
        self.tag                = tag
        self.synapsesOut        = []
        self.accumulatedWeight  = 0

    def warmUp(self):
        pass

    def sigmoid(self):
        # na literatura, yj(n) = φj(vj(n))
        sigmoidValue = 1 / (1+math.exp(self.accumulatedWeight * -1))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

    def receiveSignal(self, signalValue):
        # a input layer não tem somatório de valores
        # ela recebe de uma fonte somente, então para já ativar
        # o próximo passo
        self.accumulatedWeight = signalValue
        for synapse in self.synapsesOut: synapse.signal(signalValue)

class Output (object):

    def __init__(self, tag, source):

        # Outputs são o resultado do processamento
        # representam uma classe na classificação
        # Não tem sinapseOut, só sinapseIn
        # também não tem peso, recebe sinal integralmente
        self.source     = source
        self.tag        = tag

        # Cada passo forward ajusta o expectedValue
        # para evitar confusão, será inicializado com None
        self.expectedValue  = None  #dj(n)
        self.error          = 0     #ej(n)

    def signal(self, signalValue):
        # na literatura:  ej(n) = dj(n)-yj(n)
        self.error = self.expectedValue - signalValue
        #print("Output: " + str(signalValue)
        #      + " (expected:"+str(self.expectedValue)
        #      + ", error: "+str(self.error)+")")

class Neuron (object):

    def __init__(self, tag, a, learningRate):
        # cria um neuronio, que tera sinapses
        # de entrada e saida
        self.tag                = tag
        self.signalsReceived    = 0
        self.accumulatedWeight  = 0.0           # vj(n)
        self.bias               = Bias(self)    # bj(n)
        self.synapsesIn         = [self.bias]
        self.synapsesOut        = []
        self.a                  = a
        self.learningRate       = learningRate
        self.insideOutputLayer  = False

    def receiveSignal(self, signalValue, fromTag):

        #print(" (" + fromTag + ") Recebendo da sinapse sinal: " + str(signalValue))
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

            # na literatura, yj(n):
            sigmoidData = self.sigmoid()

            #print("# " + self.tag + " saturado com sigmoid " + str(sigmoidData))
            for synapse in self.synapsesOut: synapse.signal(sigmoidData)
            self.currentOutput     = sigmoidData

    def warmUp(self):
        # Chamado antes de um forward para zerar a saturação
        # gerada pelas sinapses de entrada
        self.accumulatedWeight = 0
        self.signalsReceived   = 0
        self.currentOutput     = 0

    def sigmoid(self):
        # na literatura, yj(n) = φj(vj(n))
        sigmoidValue = 1 / (1+math.exp(self.accumulatedWeight * -1))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

    def sigmoidDerivative(self):
        return self.a * self.currentOutput * (1.0 - self.currentOutput)

    def weightFix(self):
        # para cada sinapse de input
        # hidden & output: Δwji(n) = ƞ * localGrad * φi(vi(n))
        for inputSynapse in self.synapsesIn:
            fi_i = inputSynapse.source.sigmoid()
            inputSynapse.weight += self.learningRate * self.localGrad() * fi_i

    def localGrad(self):

        # ∂ output: ej(n) * φ'j(vj(n))
        if self.insideOutputLayer:
            return self.synapsesOut[0].error * self.sigmoidDerivative()

        # ∂ hidden: φ'j(vj(n)) * Σ(localGradk(n) * wkj(n))
        else:
            sum_grads = 0
            for out in self.synapsesOut:
                sum_grads += out.destiny.localGrad() * out.weight
            return self.sigmoidDerivative() * sum_grads

class Synapse (object):

    def __init__(self, source, destiny):
        # cria uma sinapse, que tem um neuronio
        # de entrada e um de saida
        self.source = source
        self.destiny = destiny
        self.weight = random.uniform(-1,1)
        #print "Sinapse criada entre "+source.tag+ " e "+destiny.tag

    def signal(self,input):
        # recebe um estimulo e repassa
        # para outro neuronio
        self.destiny.receiveSignal(self.weight * input, self.source.tag +" -> "+ self.destiny.tag)

class Bias (object):

    def __init__(self, destiny):
        # similar a Sinapse, mas sempre tem
        # 1 como entrada
        self.destiny = destiny
        self.source = self
        self.weight = random.uniform(-1,1)
        self.accumulatedWeight = self.weight

    def sigmoid(self):
        # na literatura, yj(n) = φj(vj(n))
        sigmoidValue = 1 / (1+math.exp(self.accumulatedWeight * -1))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

    def signal(self):
        self.accumulatedWeight = self.weight
        self.destiny.receiveSignal(self.weight * 1, "bias")
