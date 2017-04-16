#!/usr/bin/python
# -*- coding: utf8 -*-
import math
import operator
import Helpers
import multiprocessing
from MLP import MLP

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

        layouts = self.mlpLayouts()
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

            # dryRun = true -> roda somente uma vez, para testes
            self.dryRun = False
            foldLimit   = 2
            print "[ Considerando "+str(foldLimit)+" folds ]"

            for foldNum in range(0, foldLimit):

                if self.multithreadingEnabled == True and self.dryRun != True:
                    p = multiprocessing.Process(
                        target=self.runMLP,
                        args=(foldNum,layout,responseQueue,))
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
                self.numberOfTeachings    = aResponse["Teac"]

            log  = str(layout)
            log += " mean-abs-error: " + str(round(self.sumOfMeanAbs/foldLimit, 3))
            log += " root-mean-square-deviation: " + str(round(self.sumOfRootDeviantion/foldLimit, 3))
            log += " success-rate: " + str(round(self.sumOfSucessRate/foldLimit, 3))
            log += " loops: " + str(self.numberOfTeachings)

            print(log)

    def runMLP(self, foldNum, layout, responseQueue):

        sample = self.makeSample(foldNum)

        mlp                 = MLP(layout)
        lastEAv             = None
        threshold           = 0.001
        numberOfTeachings   = 0
        rateOfError         = 1
        maxTeachings        = 150
        minTeachings        = 20

        # ### Treinamento do MLP ###
        # Parada 1: taxa de erro menor que o gatilho
        # Parada 2: taxa de erro menor que 15%
        # Parada 3: atingiu o max de treinamentos
        while (rateOfError > threshold or lastEAv > 0.15) and numberOfTeachings < maxTeachings:

            numberOfTeachings += 1
            for sampleIndex in sample["S"]:

                currentInstance = self.csv.getLine(sampleIndex)
                instanceClass = currentInstance.pop(self.csv.classIndex)
                mlp.forward(currentInstance, self.mlpExpectedVector(instanceClass))

                if self.dryRun: break # dryrun roda uma vez só

            eAV = mlp.averageSquaredErrorEnergy()
            if lastEAv != None: rateOfError = lastEAv - eAV
            lastEAv = eAV

        log  = "MLP-k" + str(foldNum) + " ready!"
        log += " mean-error: " + str(round(lastEAv,3))
        log += ", delta = "+str(round(rateOfError,5))
        log += " after "+str(numberOfTeachings)+" loops"
        #print(log)

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
            'Teac': numberOfTeachings
        }

        responseQueue.put(respose)
        log  = "MLP-k" + str(foldNum)
        log += " results: success-rate at " + str(int(100*succesCount/instanceTested)) + " %"
        #print(log)

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
                layout.append(inputs)
                if j == 2: layout.append(n)
                layout.append(n)
                layout.append(n)
                layout.append(outputs)
                layoutGroup.append(layout)
                layout = []

        return layoutGroup

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        return {"T":testRange, "S":sampleRange}
