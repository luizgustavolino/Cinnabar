#!/usr/bin/python
# -*- coding: utf8 -*-

import sys

# Print table
# codigo auxiliar, escrito por Steven Fernandez
# https://gist.github.com/lonetwin/4721748
def printTable(rows, start = ""):
    widths = [ len(max(columns, key=len)) for columns in zip(*rows) ]
    header, data = rows[0], rows[1:]

    print( start +
        ' | '.join( format(title, "%ds" % width)
        for width, title in zip(widths, header) )
    )

    print( start + '-+-'.join( '-' * width for width in widths ) )

    for row in data:
        print( start +
            " | ".join( format(cdata, "%ds" % width)
            for width, cdata in zip(widths, row)
        ))

## Mostra o Help do programa
def showHelp():
    print '- Cinnabar - PI-V Senac - Lino, Hideki, Guilherme'
    print ' exemplo: python cinnabar.py file:dados.csv separator:c class-index:0'
    print '  a primeira linha do arquivo sera sempre o header.'
    print '--- file: nome do arquivo com os dados (csv)'
    print '--- separator: caracter separador, pode ser \'sc\' para ponto e virgula ou \'c\' para virgula'
    print '--- class-index: index do atributo que será classificado'
    print '-'

## Le os argumentos da command line
def parseArguments():
    response = dict()

    for arg in sys.argv:
        comps = arg.split(":")
        if len(comps) == 2:
            response[comps[0]] = comps[1]

    if 'separator' in response:
        newValue = response['separator']
        if newValue == "sc": response['separator'] = ';'
        elif newValue == "c": response['separator'] = ','
        else:
            showHelp()
            return
    else:
        response['separator'] = ','

    if 'file' in response:
        return response
    else:
        showHelp()


def fileArguments():
    files = [
        {
            "file": "input/agene.csv",
            "separator": ";",
            "class-index": 2
        },{
            "file": "input/agene-4.csv",
            "separator": ";",
            "class-index": 2
        },{
            "file": "input/iris.csv",
            "separator": ",",
            "class-index": 4
        },
        {
            "file": "input/breast.csv",
            "separator": ";",
            "class-index": 9
        },
        {
            "file": "input/wine.csv",
            "separator": ",",
            "class-index": 0
        },
        {
            "file": "input/abalone.csv",
            "separator": ",",
            "class-index": 0
        },
        {
            "file": "input/adult.csv",
            "separator": ",",
            "class-index": 14
        },
        {
            "file": "input/wine-white.csv",
            "separator": ";",
            "class-index": 11
        },
        {
            "file": "input/wine-red.csv",
            "separator": ";",
            "class-index": 11
        }
    ]
    return files

def runOptions():
    print "\n\n-------------- Cinnabar! --------------\n\n"
    files = fileArguments()

    output = []
    output.append(["ID", "Arquivo"])
    for index in range(0, len(files)):
        output.append([" " + str(index + 1), files[index]["file"]])

    while True:
        printTable(output)
        fileId = input("Escolha o ID de um dos arquivos: ")

        if fileId > 0 and fileId <= len(files):
            break
        else:
            print ("ID inexistente.\n\n")


    return files[fileId - 1]
