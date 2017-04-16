#!/usr/bin/python
# -*- coding: utf8 -*-

import Helpers

# logica aplicada aos dados lidos
class CSV(object):

    def __init__(self, filename, separator, classIndex, cleanup = True):

        self.classIndex = int(classIndex)

        #abre o arquivo, o nome vem pelo parametro 'file'
        rawFile = open(filename, 'r').read()
        lines = rawFile.split('\n')

        #linhas vazias sao descartadas
        lines = [line for line in lines if line.strip() != ""]

        # TODO: embaralhar as linhas

        headerLine = lines.pop(0)
        headerFields = headerLine.split(separator)
        classesLabel = dict()
        response = dict()

        for field in headerFields:
            response[field] = []

        for line in lines:
            lineFields = line.split(separator)

            for i,field in enumerate(lineFields):

                fieldData = field.strip()
                header = headerFields[i]

                try:
                    fieldData = float(fieldData)
                    response[header].append(fieldData)

                except ValueError:
                    if fieldData == "?":
                        response[headerFields[i]].append(None)
                    else:
                        if header in classesLabel:

                            fieldIndex = None
                            for fi, alreadyThere in enumerate(classesLabel[header]):
                                if alreadyThere == fieldData:
                                    fieldIndex = fi
                                    break

                            if fieldIndex == None:
                                classesLabel[header].append(fieldData)
                                fieldIndex = len(classesLabel[header]) - 1
                        else:
                            classesLabel[header] = [fieldData]
                            fieldIndex = 0

                        response[headerFields[i]].append(fieldIndex + 1)

        self.headers = headerFields
        self.raw = response
        self.classes = classesLabel
        self.className = self.headers[self.classIndex]

        if cleanup:
            self.cleanup()

    def countLines(self):
        return len(self.raw[self.raw.keys()[0]])

    def responseClasses(self):
        classesValues = list(set(self.raw[self.className]))
        return classesValues

    def getLine(self, num):

        if num >= self.countLines():
            return None

        response = []
        for field in self.headers:
            response.append(self.raw[field][num])
        return response

    def cleanup(self):

        shouldRepeat = True
        while shouldRepeat:
            shouldRepeat = False
            for ix in range(0,len(self.raw[self.raw.keys()[0]])):
                for field in self.headers:
                    if self.raw[field][ix] == None:
                        self.removeLine(ix)
                        shouldRepeat = True
                        break
                if shouldRepeat: break


    def removeLine(self, n):
        for field in self.headers:
            del self.raw[field][n]

    # Calculo de min, max e avg
    def fieldStats(self, field):

        if field in self.raw:

            fieldData = self.raw[field]

            minvalue = fieldData[0]
            maxvalue = fieldData[0]
            sumvalue = 0

            for data in fieldData:
                if data == None: continue
                sumvalue += data
                if minvalue > data:
                    minvalue = data
                if maxvalue < data:
                    maxvalue = data

            avg = round(sumvalue/len(fieldData), 3)
            return {
                'min': minvalue,
                'max': maxvalue,
                'average': avg,
                'deviation': self.standardDeviation(fieldData, avg)
            }

        else:
            print 'Campo nao encontrado!', field

    # Calculo do desvio padrao
    def standardDeviation(self, values, average):
        sum = 0.0
        for value in values:
            if value == None: continue
            sum += ((value - average) ** 2)
        variance = sum / (len(values) - 1)
        return round((variance ** 0.5), 3)

    # Calculo do valor normalizado
    def normalized(self, values, max, min):
        vector = []
        range = max-min
        for value in values:
            if value == None: continue
            normalized = (value - min) / range
            vector.append(normalized)
        return vector

    # Grava o normalizado
    def writeNormalized(self, filename, separator):

        output = ""
        headersCount = len(self.headers)
        for field in self.headers:
            output += field + separator
        output += "\n"

        normRaw = dict()
        for field in self.headers:
            # desmarque para nao normalizar classes
            # if field in self.classes: continue
            stats = self.fieldStats(field)
            normRaw[field] = self.normalized(self.raw[field], stats['max'], stats['min'])

        for ix in range(0,len(self.raw[self.raw.keys()[0]])):
            for fx, field in enumerate(self.headers):

                if field in self.classes or field == "Class":
                    finalValue = self.raw[field][ix]
                    output += str(finalValue)
                else:
                    finalValue = normRaw[field][ix]
                    output += str(finalValue)

                if fx < headersCount - 1:
                    output += separator

            output += "\n"

        handler = open(filename, 'w')
        handler.write(output)
        handler.close()

    # Faz print do status
    def printStats(self):

        print "\n#------------------------------------------------#"
        print "| Normalização                                   |"
        print "#------------------------------------------------#\n"

        if len(self.classes.keys()) != 0:
            for aclass in self.classes:
                output = [["Atributo: " + aclass, "Valor indexado"]]
                for ix,item in enumerate(self.classes[aclass]):
                    output.append([item,str(ix+1)])
                Helpers.printTable(output)
                print("\n")

        response = [["Campo","Min.","Max.","Média ", "Desvio padrão"]]
        for field in self.headers:

            if field in self.classes:
                continue

            stats = self.fieldStats(field)
            response.append([
                field,
                str(stats['min']),
                str(stats['max']),
                str(stats['average']),
                str(stats['deviation'])
            ])

        Helpers.printTable(response)
