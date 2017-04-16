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

        # multithreadingEnabled = true -> processa folds em threads
        self.multithreadingEnabled = True
        processPool = []

        # dryRun = true -> roda somente uma vez, para testes
        self.dryRun = False

        for foldNum in range(0,k):

            if self.multithreadingEnabled == True and self.dryRun != True:
                p = multiprocessing.Process(target=self.runMLP, args=(foldNum,))
                processPool.append(p)
            else:
                self.runMLP(foldNum)
                if self.dryRun: return

        if self.multithreadingEnabled:
            for p in processPool: p.start()
            for p in processPool: p.join()

    def runMLP(self, foldNum):

        sample = self.makeSample(foldNum)
        #print "\n: kFold num.: " + str(foldNum)
        #print "................................................."
        #print ": Testando instâncias de " + str(sample["T"][0]) + " até " + str(sample["T"][-1])

        # TODO: montar layouts segundo o enunciado
        attributesCount = len(self.csv.headers)-1
        layouts = self.mlpLayouts(attributesCount)

        for layout in layouts:

            mlp                 = MLP(layout)
            lastEAv             = None
            threshold           = 0.001
            numberOfTeachings   = 0
            rateOfError         = 1

            # 1 passo: treinamento do MLP
            while(rateOfError > threshold or lastEAv > 0.15):

                numberOfTeachings += 1
                for sampleIndex in sample["S"]:

                    currentInstance = self.csv.getLine(sampleIndex)
                    instanceClass = currentInstance.pop(self.csv.classIndex)
                    mlp.forward(currentInstance, self.mlpExpectedVector(instanceClass))

                    if self.dryRun: break # dryrun roda uma vez só

                eAV = mlp.averageSquaredErrorEnergy()
                if lastEAv != None: rateOfError = lastEAv - eAV
                lastEAv = eAV

            print "MLP Ready: mean-error at "+str(round(lastEAv,3))+", delta = "+str(round(rateOfError,5))+" after "+str(numberOfTeachings)+" loops"

            # Classificação
            instanceTested  = 0.0
            succesCount     = 0.0

            for sampleIndex in sample["T"]:
                currentInstance = self.csv.getLine(sampleIndex)
                instanceClass = currentInstance.pop(self.csv.classIndex)
                success = mlp.forward(currentInstance, self.mlpExpectedVector(instanceClass), False)
                instanceTested += 1
                if success == True: succesCount += 1

            print "Success rate: " + str(int(100*succesCount/instanceTested))+"%"

    # instancia tem classe 3 -> [0,0,1]
    def mlpExpectedVector(self, expectedClass):
        responseVector = []
        for aClass in self.csv.responseClasses():
            if aClass == expectedClass: responseVector.append(1)
            else: responseVector.append(0)
        #print "Expected " + str(responseVector) + " : " + str(expectedClass)
        return responseVector

    def mlpLayouts(self, attributesCount):
        # TODO: pedir ajuda do hideki
        # [ attributesCount, willian passou(x hidden de x neuronios), count(classes) ]
        # a) [3,  6,6, 2 ]
        # b) [3,  6,6,6, 2]
        # c) .. vetor de vetores
        return [[attributesCount,attributesCount,attributesCount,attributesCount,3]]

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        return {"T":testRange, "S":sampleRange}
