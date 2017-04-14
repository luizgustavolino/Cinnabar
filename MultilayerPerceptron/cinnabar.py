#!/usr/bin/python
# -*- coding: utf8 -*-
import Helpers
import Parser
import Classificador

# inicio do fluxo do programa
# parseArguments vai ler os parametros da command line
args = Helpers.parseArguments()

# se houver um problema na leitura dos argumentos
# nao ha o que fazer, entao validamos aqui se eles existem
if args != None:

    filename = args.get('file')
    separator = args.get('separator')
    classindex = args.get('class-index')

    #1) le o csv e normaliza
    csv = Parser.CSV(filename,separator,classindex)

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

    #4) roda o kNN
    knn = Classificador.kFold(csv, 10)
