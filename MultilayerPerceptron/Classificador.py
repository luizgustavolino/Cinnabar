#!/usr/bin/python
# -*- coding: utf8 -*-
import math
import operator
import Helpers

#Arrumar empate
#Coisas da Matriz Binaria!
#Calcular acurárcia

class kFold(object):

    def __init__(self, csv, k):

        self.foldSize = int(math.ceil(csv.countLines()/float(k)))
        self.csv = csv

        kCases = []

        classesValues = list(set(self.csv.raw[self.csv.className]))
        classesCount = len(classesValues)

        print "\n#------------------------------------------------#"
        print "| Classificação                                  |"
        print "#------------------------------------------------#\n"
        print " Considerando como class a coluna: " + self.csv.className + " (M="+str(classesCount)+")"
        print "--------------------------------------------------"

        #classesCount = len(self.csv.headers) - 1
        M = classesCount
        if M%2 == 0: M += 1
        Q = self.csv.countLines()

        #1 caso: 1NN
        kCases.append(1)

        #2 caso: (M+2)NN
        kCases.append(M + 2)

        #3 caso: (M*10 + 1)NN
        kCases.append(M*10 + 1)

        #4 caso: Q/2 para impar, Q /2 + 1 par
        halfQ = int(round(Q/2))

        if halfQ%2 == 0:
            kCases.append(halfQ + 1)
        else:
            kCases.append(halfQ)

        multiLevelMatrix = []
        for index in range(0, len(kCases)):
            matrix = [[0 for x in range(classesCount)] for y in range(classesCount)]
            multiLevelMatrix.append(matrix)

        nns = []
        for i in range(0,k):
            sample = self.makeSample(i)
            print "\n: kFold num.: " + str(i)
            print "................................................."
            print ": Testando instâncias de " + str(sample["T"][0]) + " até " + str(sample["T"][-1])
            nn = self.kNN(sample["T"], sample["S"], self.csv.classIndex, multiLevelMatrix, kCases, classesValues)
            nns.append(nn)

        print "\n\n--------------------- Validação Cruzada ---------------------"
        print self.crossValidation(nns)
        print "-------------------------------------------------------------"

        accuracies = self.accuracy(multiLevelMatrix, kCases)
        index = 0
        for matrix in multiLevelMatrix:
            line = ["Total"]
            for value in classesValues:
                line.append(str(value))
            output = []
            output.append(line)

            for i in range(0, classesCount):
                line = []
                line.append(str(classesValues[i]))
                for j in range(0, classesCount):
                    line.append(str(matrix[i][j]))

                output.append(line)

            print ("\n")

            if classesCount == 2:
                print "Matriz de confusão para " + str(kCases[index]) + "NN:\n"
            else:
                print "Matriz multi nivel para " + str(kCases[index]) + "NN:\n"

            Helpers.printTable(output, "  ")
            print "\n  Acurácia: ", str((round(accuracies["k" +str(kCases[index])], 3) * 100)) + "%"
            index += 1

        if classesCount == 2:
            self.printBinaryProperties(self.binaryProperties(multiLevelMatrix, kCases), kCases)

    def makeSample(self, iter):
        lower = iter*self.foldSize
        upper = min(lower + self.foldSize, self.csv.countLines())
        testRange = range(lower, upper)
        sampleRange = list(set(range(self.csv.countLines()))-set(testRange))
        return {"T":testRange, "S":sampleRange}

    def kNN(self, t, s, classIndex, multiLevelMatrix, kCases, classesValues):

        deltaCounters = dict()
        tieCount      = 0

        for k in kCases:
            deltaCounters[k] = {"d1":0}

        for testCase in t:

            p = self.csv.getLine(testCase)
            distances = []

            for sample in s:
                q = self.csv.getLine(sample)
                distances.append({
                    "i": sample,
                    "d": self.euclideanDistance(p, q, classIndex)
                })

            realClass   = p[classIndex]
            nearest, nDistances = self.kFirstItens(distances, kCases[-1])
            index = 0

            for kCase in kCases:

                votes = dict()
                kNearests = nearest[:kCase]

                for aNearest in kNearests:
                    aNearestClass = self.csv.getLine(aNearest)[classIndex]
                    if aNearestClass not in votes:
                        votes[aNearestClass] = 1
                    else:
                        votes[aNearestClass] = votes[aNearestClass] + 1

                sortedVotes = sorted(votes.items(), key=operator.itemgetter(1))
                kNNClass    = sortedVotes[-1][0]

                if len(sortedVotes) > 1:
                    v1count = sortedVotes[-1][1]
                    v2count = sortedVotes[-2][1]
                    if v1count == v2count:
                        tieCount += 1
                        #kNNClass = self.untie(kNearests, nDistances, classIndex, sortedVotes)

                multiLevelMatrix[index][classesValues.index(realClass)][classesValues.index(kNNClass)] += 1

                if kNNClass == realClass:
                    deltaCounters[kCase]["d1"] = deltaCounters[kCase]["d1"] + 1

                index += 1

        response = {"ks": deltaCounters, "foldSize": len(t)}
        print ": Tamanho do teste: "+str(len(t))
        print ": Empates encontrados: "+str(tieCount)
        self.samplingError(deltaCounters, len(t), response)
        print ":................................................"
        return response

    def untie(self, kNearests, dNearests, classIndex, votes):

        # quando sabemos que kNearests contém um empate
        # é feita uma ordenação por distancia entre os empatados
        whitelist = []
        whitelistChecker = votes[-1][1]
        distances = dict()

        # item[0]: valor da classe
        # item[1]: contagem de votos para classe
        for item in reversed(votes):
            if item[1] == whitelistChecker: whitelist.append(item[0])
            else: break

        for aNearest in kNearests:

            aNearestClass = self.csv.getLine(aNearest)[classIndex]
            if aNearestClass not in whitelist: continue

            if aNearestClass not in distances:
                distances[aNearestClass] = dNearests[aNearest]
            else:
                distances[aNearestClass] = distances[aNearestClass] + dNearests[aNearest]

        sortedDistances = sorted(distances.items(), key=operator.itemgetter(1))
        untied = sortedDistances[0][0]
        #print "[!] Solving tie between "+str(votes)+" with: ", untied
        return untied

    def kFirstItens(self, dlist, k):
        v = []
        d = dict()
        for x in sorted(dlist)[:k]:
            v.append(x["i"])
            d[x["i"]] = x["d"]
        return v, d

    def euclideanDistance(self,instance1, instance2, targetClassIx):
        distance    = 0
        length      = min(len(instance1), len(instance2))
        for x in range(length):
            if x != targetClassIx:
                distance += pow((instance1[x] - instance2[x]), 2)
        return math.sqrt(distance)

    def crossValidation(self, values):
        numberOfNN = len(values[0]["ks"])
        keys = values[0]["ks"].keys()

        cross = [0,] * numberOfNN

        for value in values:
            foldSize = float(value["foldSize"])

            for index in range(0, numberOfNN):
                cross[index] = cross[index] + (value["ks"].values()[index]["d1"] / foldSize)

        results = {}
        for index in range(0, numberOfNN):
            results.update({"k"  + str(keys[index]) : str((round((1 - (cross[index] / len(values))), 3) * 100)) + "%"})

        return results

    def accuracy(self, values, kCases):
        results = dict()
        result = 0.0
        total = 0.0
        i = -1
        j = 0
        for matrix in values:
            for line in matrix:
                for element in line:
                    total += element
                i+=1
                result += line[i]
                if i == len(line) - 1:
                    results.update({"k" + str(kCases[j]): float(result) / total})
                    i = -1
                    total = 0.0
                    result = 0.0
            j += 1
        return results

    def binaryProperties(self, multiLevelMatrix, kCases):
        #calculo apenas para matrizes
        cases = dict()
        print "\n\n"

        index = 0

        output = [["kNN", "TP", "TN", "FP", "FN"]]

        for matrix in multiLevelMatrix:
            values = dict()

            TP = matrix[0][0]
            TN = matrix[1][1]
            FP = matrix[0][1]
            FN = matrix[1][0]

            values.update({"sensibility":TP / float((TP + FN + 0.001))})
            values.update({"specificity":TN / float((TN + FP + 0.001))})
            values.update({"precision":TP / float((TP + FP + 0.001))})
            values.update({"recall":TP / float((TP + FN + 0.001))})

            cases.update({"k" + str(kCases[index]): values})

            output.append([
                "k" + str(kCases[index]),
                str(TP),
                str(TN),
                str(FP),
                str(FN)
                ])
            index += 1

        Helpers.printTable(output)
        return cases

    def samplingError(self, deltaCounters, t, response):

        keys = deltaCounters.keys()
        headers = [""]
        values = ["Erro amostral"]
        matches = ["Acertos"]

        for key in keys: headers.append("k" + str(key))
        for key in keys: values.append(str((round(1 - (deltaCounters[key]["d1"] / float(t)), 3) * 100)) + "%")
        for key in keys: matches.append(str(int(response["ks"][key]["d1"])))

        Helpers.printTable([headers, values, matches], ": ")

    def printBinaryProperties(self, values, kCases):
        print "\n\n"
        informations = ["kNN", "recall", "sensibility", "precision", "specificity"]

        output = []
        output.append(informations)

        for index in range(0, len(kCases)):
            kNNCase = values.keys()[index]
            output.append([
                kNNCase,
                str(round(values[kNNCase][informations[1]], 3)),
                str(round(values[kNNCase][informations[2]], 3)),
                str(round(values[kNNCase][informations[3]], 3)),
                str(round(values[kNNCase][informations[4]], 3))
            ])

        Helpers.printTable(output)
