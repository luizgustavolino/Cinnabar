#!/usr/bin/python
# -*- coding: utf8 -*-

import random
import math

class MLP (object):

    def __init__(self, layout, momentum, shouldReadFromFile):
        # cria uma rede MLP seguindo a quantidade
        # de neuronios do layout (vetor de ints)

        #print "Criando MLP, layout:" + str(layout)
        shouldReadFromFile = False

        self.layers  = [] # layers[0]  -> input layer, demais são hidden layers
        self.outputs = []

        self.n                  = 0  # Contagem de forwards, com learning
        self.instantErrorLog    = [] # Lista de erros instantâneos para cada forward de learning
        self.outputErrorLog     = [] # Lista dos erros no output (esperado)
        self.learningRate       = 0.1 # ƞ
        self.a                  = 1.0 #
        self.momentum           = momentum
        self.classesCount       = layout[-1]
        self.confMatrix         = [[0 for col in range(self.classesCount)] for row in range(self.classesCount)]


        layersCount  = len(layout)

        #lendo os pesos do txt
        biasWeights = self.readBiasWeights()
       
        # Criando os layers, inputs,neuronios e outputs
        # enumerate([2,2,1]) -> [(0,2),(1,2),(2,1)]
        indexOfNeuron = 0
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

                    biasWeight = 0.0
                    if shouldReadFromFile == True:
                        biasWeight = biasWeights[indexOfNeuron]
                    else:
                        biasWeight = random.uniform(-1,1)

                    hlNeuron = Neuron(tag, self.a, self.learningRate, self.momentum, biasWeight)
                    currentLayer.append(hlNeuron)
                    if i == layersCount -1:
                        hlNeuron.insideOutputLayer = True
                    indexOfNeuron += 1

            self.layers.append(currentLayer)


        #lendo os pesos do txt
        allLayersWeights = self.readWeights()
       

        indexOfNeuron = 0
        # Criando as sinapses entre os neuronios
        for i, layer in enumerate(self.layers):

            if i < layersCount - 1:
                nextLayer = self.layers[i+1]
                for neuron in layer:
                    neuronWeights = allLayersWeights[indexOfNeuron]
                    for j, target in enumerate(nextLayer):

                        synapseWeight = 0.0
                        if shouldReadFromFile == True:
                            synapseWeight = neuronWeights[j]
                        else:
                            synapseWeight = random.uniform(-1,1)

                        synapse = Synapse(neuron,target, synapseWeight)
                        neuron.synapsesOut.append(synapse)
                        target.synapsesIn.append(synapse)
                    indexOfNeuron += 1
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
        # Iniciando passo forward

        for (j, inputNode) in enumerate(self.layers[0]):
            inputNode.receiveSignal(inputs[j])

        if learningMode == True:

            # Iniciando passo backward
            self.instantErrorLog.append(self.instantaneousErrorEnergy())
            self.n += 1

            # Aplicando correção nas sinapses da layer: i
            for i,layer in enumerate(reversed(self.layers[1:])):
                for neuron in layer: neuron.weightFix()
        else:

            self.outputErrorLog.append(self.outputError())
            currentClass        = -1
            currentClassValue   = -1

            # pega o output de maior signal
            for i, output in enumerate(self.outputs):
                if output.lastSignal > currentClassValue:
                    currentClass        = i
                    currentClassValue   = output.lastSignal

            # expectedOutputs: [0,0,1] = terceira classe
            for i, expected in enumerate(expectedOutputs):
                if expected == 1:
                    self.confMatrix[i][currentClass] += 1
                    if i == currentClass: return True
                    else: return False

    ### Calculo dos erros ###

    def instantaneousErrorEnergy(self):
        #  ℰ(n) = (1/2) Σ(ej(n))^2
        total = 0
        for output in self.outputs: total += output.error*output.error
        return total * 0.5

    def averageSquaredErrorEnergy(self):
        # ℰav = (1/N) Σ ℰ(n)
        result = 0
        for instant in self.instantErrorLog: result += instant
        return result / len(self.instantErrorLog)

    def meanAbsoluteError(self):
        result = 0
        for error in self.outputErrorLog: result += abs(error)
        return result / len(self.outputErrorLog)

    def rootMeanSquareDeviation(self):
        result = 0
        for error in self.outputErrorLog: result += error * error
        return math.sqrt(result / len(self.outputErrorLog))

    def outputError(self):
        for output in self.outputs:
            if output.expectedValue == 1:
                return output.error

    def readBiasWeights(self):
        fileBias = open("bias.txt", "r")

        biasWeights = []
        for line in fileBias:
            stringArray = line.split(";")
            biasWeights = [float(item) for item in stringArray]

        return biasWeights

    def readWeights(self):
        file = open("weights.txt", "r")

        allLayersWeights = []
        for line in file:
            stringArray = line.split(";")
            weightsArray = [float(item) for item in stringArray]
            allLayersWeights.append(weightsArray)

        return allLayersWeights


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
        sigmoidValue = 1.0 / (1.0+math.exp(self.accumulatedWeight * -1.0))
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
        self.lastSignal     = 0
        self.error          = 0     #ej(n)

    def signal(self, signalValue):
        # na literatura:  ej(n) = dj(n)-yj(n)
        self.error  = self.expectedValue - signalValue
        self.lastSignal = signalValue

class Neuron (object):

    def __init__(self, tag, a, learningRate, momentum, biasWeight):
        # cria um neuronio, que tera sinapses
        # de entrada e saida
        self.tag                = tag
        self.signalsReceived    = 0
        self.accumulatedWeight  = 0.0           # vj(n)
        self.bias               = Bias(self, biasWeight)    # bj(n)
        self.synapsesIn         = [self.bias]
        self.synapsesOut        = []
        self.a                  = a
        self.learningRate       = learningRate
        self.insideOutputLayer  = False
        self.momentum           = momentum

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
            for synapse in self.synapsesOut: synapse.signal(sigmoidData)
            self.currentOutput     = sigmoidData

    def warmUp(self):
        # Chamado antes de um forward para zerar a saturação
        # gerada pelas sinapses de entrada
        self.accumulatedWeight = 0.0
        self.signalsReceived   = 0

    def sigmoid(self):
        # na literatura, yj(n) = φj(vj(n))
        sigmoidValue = 1.0 / (1.0 + math.exp(self.accumulatedWeight * -1.0))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

    def sigmoidDerivative(self):
        return self.a * self.currentOutput * (1.0 - self.currentOutput)

    def weightFix(self):

        # para cada sinapse de input
        # a = Δwji(n-1) * momentum
        # hidden & output: Δwji(n) = ƞ * localGrad * φi(vi(n)) + a
        for inputSynapse in self.synapsesIn:
            fi_i = inputSynapse.source.sigmoid()
            a = self.momentum * inputSynapse.lastDelta
            deltaw = self.learningRate * self.localGrad() * fi_i
            inputSynapse.weight = inputSynapse.weight + a + deltaw
            inputSynapse.lastDelta = deltaw

    def localGrad(self):

        # ∂ output: ej(n) * φ'j(vj(n))
        if self.insideOutputLayer:
            return self.synapsesOut[0].error * self.sigmoidDerivative()

        # ∂ hidden: φ'j(vj(n)) * Σ(localGradk(n) * wkj(n))
        else:
            sum_grads = 0.0
            for out in self.synapsesOut:
                sum_grads += out.destiny.localGrad() * out.weight
            return self.sigmoidDerivative() * sum_grads

class Synapse (object):

    def __init__(self, source, destiny, weight):
        # cria uma sinapse, que tem um neuronio
        # de entrada e um de saida
        self.source     = source
        self.destiny    = destiny
        self.lastDelta  = 0
        self.weight     = weight 

    def signal(self,input):
        # recebe um estimulo e repassa
        # para outro neuronio
        self.destiny.receiveSignal(self.weight * input, self.source.tag +" -> "+ self.destiny.tag)

class Bias (object):

    def __init__(self, destiny, biasWeight):
        # similar a Sinapse, mas sempre tem
        # 1 como entrada
        self.destiny = destiny
        self.source = self
        self.lastDelta = 0
        self.weight = biasWeight 
        #print self.weight
        self.accumulatedWeight = self.weight

    def sigmoid(self):
        # na literatura, yj(n) = φj(vj(n))
        sigmoidValue = 1 / (1+math.exp(self.accumulatedWeight * -1))
        if sigmoidValue > 1 or sigmoidValue < 0: raise NameError('INVALID SIGMOID VALUE')
        return sigmoidValue

    def signal(self):
        self.accumulatedWeight = self.weight
        self.destiny.receiveSignal(self.weight * 1, "bias")
