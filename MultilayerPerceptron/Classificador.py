#!/usr/bin/python
# -*- coding: utf8 -*-
import math
import operator
import Helpers
import multiprocessing
import MLP

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

        processPool = []
        multithreadingEnabled = True

        for i in range(0,k):
            if multithreadingEnabled == True:
                p = multiprocessing.Process(target=self.runMLP, args=(i,))
                processPool.append(p)
                p.start()
            else:
                self.runMLP(i)


    def runMLP(self, foldNum):

        sample = self.makeSample(foldNum)
        print "\n: kFold num.: " + str(foldNum)
        print "................................................."
        print ": Testando instâncias de " + str(sample["T"][0]) + " até " + str(sample["T"][-1])

        # TODO: montar layouts segundo o enunciado
        layouts = self.mlpLayouts(len(self.csv.headers)-1)

        for layout in layouts:

            mlp = MLP.MLP(layout)

            # 1 passo: treinamento do MLP
            for sampleIndex in sample["S"]:
                currentInstance = self.csv.getLine(sampleIndex)
                expected = currentInstance.pop(self.csv.classIndex)
                mlp.forward(currentInstance)

            # TODO: 2 passo: classificação

    def mlpLayouts(self, attributesCount):
        # TODO: pedir ajuda do hideki
        return [[attributesCount,4,2]]

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        return {"T":testRange, "S":sampleRange}
