#!/usr/bin/python
# -*- coding: utf8 -*-
import math
import operator
import Helpers
import multiprocessing
from MLP import MLP
import time

class kFold(object):

    def __init__(self, csv, k):

        self.foldSize = int(math.ceil(csv.countLines()/float(k)))
        self.csv = csv

        classesValues = list(set(self.csv.raw[self.csv.className]))
        classesCount = len(classesValues)

        print "\n#------------------------------------------------#"
        print "| Classificação                                  |"
        print "#------------------------------------------------#\n"
        print " Considerando como class a coluna: " + self.csv.className + " (M="+str(classesCount)+")"
        print "--------------------------------------------------"

        foldLimit = 1
        print "[ Considerando "+str(foldLimit)+" folds ]"

        bestLayout          = None
        bestSuccessRate     = 0
        bestLoopsCounts     = 0
        bestElapsedTime     = 0

        layouts = self.mlpLayouts()
        layoutsConfMatrix = {}

        for layout in layouts:

            # multithreadingEnabled = true -> processa folds em threads
            self.multithreadingEnabled = True
            processPool     = []
            responseQueue   = multiprocessing.Queue()

            # Sums
            self.sumOfRootDeviantion    = 0
            self.sumOfMeanAbs           = 0
            self.sumOfSucessRate        = 0
            self.numberOfTeachings      = 0
            self.sumOfConfMatrix        = None
            self.bestLayoutMomentum     = 0.0

            # dryRun = true -> roda somente uma vez, para testes
            self.dryRun = False
            start_time = time.time()

            for foldNum in range(0, foldLimit):

                if self.multithreadingEnabled == True and self.dryRun != True:
                    p = multiprocessing.Process(
                        target=self.runMLP,
                        args=(foldNum, layout, self.bestLayoutMomentum, responseQueue,))
                    processPool.append(p)
                else:
                    self.runMLP(foldNum, responseQueue)
                    if self.dryRun: return

            if self.multithreadingEnabled:
                for p in processPool: p.start()
                for p in processPool: p.join()

            while responseQueue.empty() == False :
                aResponse = responseQueue.get()
                self.sumOfRootDeviantion += aResponse["SDev"]
                self.sumOfMeanAbs        += aResponse["MAbs"]
                self.sumOfSucessRate     += aResponse["SucR"]
                self.numberOfTeachings   += aResponse["Teac"]
                self.sumConfMatrix(aResponse["Conf"])

            successRate = self.sumOfSucessRate/foldLimit
            loops       = int(self.numberOfTeachings/foldLimit)
            elapsed     = time.time() - start_time
            layoutsConfMatrix[str(layout)] = self.sumOfConfMatrix

            log  = str(layout)
            log += " mean-abs: " + str(round(self.sumOfMeanAbs/foldLimit, 3))
            log += " square-deviation: " + str(round(self.sumOfRootDeviantion/foldLimit, 3))
            log += " success: " + str(round(successRate, 3))
            log += " loops: " + str(loops)
            log += " elapsed time: " + str(round(elapsed,1)) + "s "

            useThisAsBestLayout = False
            if successRate > bestSuccessRate:
                useThisAsBestLayout = True
            elif successRate == bestSuccessRate:
                if loops < bestLoopsCounts:
                     useThisAsBestLayout = True
                elif loops == bestLoopsCounts:
                    if elapsed < bestElapsedTime:
                        useThisAsBestLayout = True

            if useThisAsBestLayout == True:
                bestSuccessRate = successRate
                bestLayout      = layout
                bestLoopsCounts = loops
                bestElapsedTime = elapsed

            print(log)

        print "Best layout: " + str(bestLayout)

        #escolher a melhor matriz conf
        bestConfiMatrix = layoutsConfMatrix[str(bestLayout)]
        classesValues   = self.csv.classes[self.csv.className]
        header = [str(layout)]
        output = [header]

        for i, iClass in enumerate(classesValues):
            header.append(str(iClass))
            line = [str(iClass)]
            for j, jClass in enumerate(classesValues):
                line.append(str(bestConfiMatrix[i][j]))

            output.append(line)

        print "\n"
        Helpers.printTable(output)
        print "\n"

        ## Validação de melhor a
        # for aMomentum in [0.0]:

        #     # Sums
        #     self.sumOfRootDeviantion    = 0
        #     self.sumOfMeanAbs           = 0
        #     self.sumOfSucessRate        = 0
        #     self.sumOfConfMatrix        = None
        #     self.numberOfTeachings      = 0
        #     self.bestLayoutMomentum     = 0.0

        #     processPool     = []
        #     responseQueue   = multiprocessing.Queue()

        #     for foldNum in range(0, foldLimit):
        #         p = multiprocessing.Process(
        #                 target=self.runMLP,
        #                 args=(foldNum, bestLayout, aMomentum, responseQueue,))
        #         processPool.append(p)

        #     for p in processPool: p.start()
        #     for p in processPool: p.join()

        #     while responseQueue.empty() == False :
        #         aResponse = responseQueue.get()
        #         self.sumOfSucessRate     += aResponse["SucR"]
        #         self.numberOfTeachings   += aResponse["Teac"]

        #     loops = int(self.numberOfTeachings/foldLimit)
        #     successRate = str(round(self.sumOfSucessRate/foldLimit, 3)) + "%"
        #     print "Para momentum = "+ str(round(aMomentum,2)) +", loops: " + str(loops) + ", success: " + successRate

    def runMLP(self, foldNum, layout, momentum, responseQueue):

        sample = self.makeSample(foldNum)

        #Controla se vai ler pesos do txt
        #Caso sim, nao treina a rede, apenas testa
        #Caso nao, rede treinada normalmente e novos pesos salvos em um arquivo
        shouldReadFromFile  = True


        mlp                 = MLP(layout, momentum, shouldReadFromFile)
        lastEAv             = None
        threshold           = 0.001
        numberOfTeachings   = 0
        rateOfError         = 1
        maxTeachings        = 200
        minTeachings        = 20

        # ### Treinamento do MLP ###
        # Parada 1: taxa de erro menor que o gatilho
        # Parada 2: taxa de erro menor que 15%
        # Parada 3: atingiu o max de treinamentos
        while (rateOfError > threshold or lastEAv > 0.15) and numberOfTeachings < maxTeachings and shouldReadFromFile == False:

            numberOfTeachings += 1
            for sampleIndex in sample["S"]:

                currentInstance = self.csv.getLine(sampleIndex)
                instanceClass = currentInstance.pop(self.csv.classIndex)
                mlp.forward(currentInstance, self.mlpExpectedVector(instanceClass))

                if self.dryRun: break # dryrun roda uma vez só

            eAV = mlp.averageSquaredErrorEnergy()
            if lastEAv != None: rateOfError = lastEAv - eAV
            lastEAv = eAV

            
            print numberOfTeachings


        # Classificação
        instanceTested  = 0.0
        succesCount     = 0.0

        for sampleIndex in sample["T"]:
            currentInstance = self.csv.getLine(sampleIndex)
            instanceClass = currentInstance.pop(self.csv.classIndex)
            success = mlp.forward(currentInstance, self.mlpExpectedVector(instanceClass), False)
            if success == True: succesCount += 1
            instanceTested += 1

        self.sumOfSucessRate        += succesCount/instanceTested
        self.sumOfRootDeviantion    += mlp.rootMeanSquareDeviation()
        self.sumOfMeanAbs           += mlp.meanAbsoluteError()

        respose = {
            'SucR': succesCount/instanceTested,
            'SDev': mlp.rootMeanSquareDeviation(),
            'MAbs': mlp.meanAbsoluteError(),
            'Teac': numberOfTeachings,
            'Conf': mlp.confMatrix
        }


        #Rotina para salvar pesos no txt
        if shouldReadFromFile == False:
            layers = mlp.layers
            allLayersWeights = self.getWeights(layers)
            biasWeights = self.getBiasWeights(layers)
            self.createTxt(allLayersWeights)
            self.createBiasTxt(biasWeights)

        responseQueue.put(respose)

    def getBiasWeights(self, layers):
        #Percorre os neuronios da MLP, pegando o pesos nos bias, apos o treinamento da rede
        biasWeights = []

        for i, neurons in enumerate(layers):
            if i > 0:
                for neuron in neurons:
                    synapse = neuron.synapsesIn[0]
                    biasWeights.append(synapse.weight)
                    print neuron.tag, synapse.weight

        return biasWeights

    def getWeights(self, layers):
        #Percorre os neuronios da MLP, pegando o pesos nos de input, apos o treinamento da rede
        allLayersWeights = []

        for i, neurons in enumerate(layers):
            if i < len(layers) - 1:
                for neuron in neurons:
                    currentNeuronWeights = []
                    for synapse in neuron.synapsesOut:
                        currentNeuronWeights.append(synapse.weight)
                        print neuron.tag, synapse.weight, synapse.destiny.tag
                    allLayersWeights.append(currentNeuronWeights)

        return allLayersWeights

    def createTxt(self, allLayersWeights):
        #Cria um arquivo .txt, com os pesos de saida de cada neuronio
        file = open("weights.txt", "w")

        for neuron in allLayersWeights:
            stringWeights = ""
            print neuron, "\n"
            for weight in neuron:
               stringWeights += '{0:.16f}'.format(weight) + ";"
  
            stringWeights = stringWeights[:-1]
            stringWeights += "\n"
            file.write(stringWeights)

        file.close()
        print "\n\n"

    def createBiasTxt(self, biasWeights):
        #Cria um arquivo .txt, com os pesos do bias de cada neuronio
        file = open("bias.txt", "w")
        stringWeights = ""

        for weight in biasWeights:
            stringWeights += '{0:.16f}'.format(weight) + ";"

        stringWeights = stringWeights[:-1]
        stringWeights += "\n"
        file.write(stringWeights)
        file.close()


    # instancia tem classe 3 -> [0,0,1]
    def mlpExpectedVector(self, expectedClass):
        responseVector = []
        for aClass in self.csv.responseClasses():
            if aClass == expectedClass: responseVector.append(1)
            else: responseVector.append(0)
        return responseVector

    def mlpLayouts(self):

        inputs      = len(self.csv.headers)-1
        outputs     = len(self.csv.responseClasses())
        layout      = []
        layoutGroup = []
        qMax = max(inputs, outputs)

        for i in xrange(1,4):

            if i == 1: n = int(qMax * 0.5)
            if i == 2: n = int(qMax)
            if i == 3: n = int(qMax * 2)

            for j in xrange(1,3):
                if i == 3 and j == 2: continue
                layout.append(inputs)
                if j == 2: layout.append(n)
                layout.append(n)
                layout.append(n)
                layout.append(outputs)
                layoutGroup.append(layout)
                layout = []

        return [[2,8,8,4]]
        #return layoutGroup

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        #sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        sampleRange = range(0, self.csv.countLines())
        return {"T":testRange, "S":sampleRange}

    def sumConfMatrix(self, newMatrix):

        if self.sumOfConfMatrix == None:
            self.sumOfConfMatrix = newMatrix
        else:
            for i, sm in enumerate(newMatrix):
                for j, v in enumerate(sm):
                    self.sumOfConfMatrix[i][j] += v
