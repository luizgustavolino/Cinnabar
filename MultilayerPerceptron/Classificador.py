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
        self.multithreadingEnabled = False
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
        print "\n: kFold num.: " + str(foldNum)
        print "................................................."
        print ": Testando instâncias de " + str(sample["T"][0]) + " até " + str(sample["T"][-1])

        # TODO: montar layouts segundo o enunciado
        attributesCount = len(self.csv.headers)-1
        layouts = self.mlpLayouts(attributesCount)

        for layout in layouts:

            mlp = MLP(layout)

            # 1 passo: treinamento do MLP
            for sampleIndex in sample["S"]:

                currentInstance = self.csv.getLine(sampleIndex)
                currentInstance.pop(self.csv.classIndex)
                mlp.forward(currentInstance, self.mlpExpectedVector())

                if self.dryRun: break # dryrun roda uma vez só

            # TODO: 2 passo: classificação

            print "Av Error: " + str(mlp.averageSquaredErrorEnergy())

    def mlpExpectedVector(self):
        responseVector = []
        for aClass in self.csv.headers:
            if aClass == self.csv.className: responseVector.append(1)
            else: responseVector.append(0)
        return responseVector

    def mlpLayouts(self, attributesCount):
        # TODO: pedir ajuda do hideki
        return [[attributesCount,4,4,3]]

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        return {"T":testRange, "S":sampleRange}
