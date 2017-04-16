#!/usr/bin/python
# -*- coding: utf8 -*-
import Helpers
import Parser
import Classificador

# inicio do fluxo do programa
# run options retornara os parametros do arquivo escolhido
args = Helpers.runOptions()

#1) le o csv e normaliza
csv = Parser.CSV(args["file"], args["separator"], args["class-index"])

#2) mostra resultado da normalizacao
csv.printStats()

#3) salva o resultado normalizado em outro arquivo
if ".data" in args['file']:
    finalFileName = args['file'].replace(".data", ".norm.csv")
elif ".csv" not in args['file']:
    finalFileName = args['file'] + ".norm.csv"
else:
    finalFileName = args['file'].replace(".csv", ".norm.csv")

csv.writeNormalized(finalFileName, args['separator'])
Classificador.kFold(csv, 10)
