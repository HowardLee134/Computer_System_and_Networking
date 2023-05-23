# This is a class project that for COMP 170 that Made by MING hao(Howard) LEE

import argparse
import string
import re

parser = argparse.ArgumentParser()
parser.add_argument("input", help="file with input to the translator", type=str)
args = parser.parse_args()
modregisters = {'00000': '$s0', '00001': '$s1', '00010': '$s2', '00011': '$s3', '00100': '$s4', '00101': '$s5',
                '00110': '$s6', '00111': '$s7'}
# registers = {'00000':'$zero', '00010':'$v0', '00011':'$v1', '00100':'$a0', '00101':'$a1', '00110':'$a2',
# '00111':'$a3', '01000':'$t0', '01001':'$t1', '01010':'$t2', '01011':'$t3', '01100':'$t4', '01101':'$t5',
# '01110':'$t6', '01111':'$t7', '10000':'$s0', '10001':'$s1', '10010':'$s2', '10011':'$s3', '10100':'$s4',
# '10101':'$s5', '10110':'$s6', '10111':'$s7', '11000':'$t8', '11001':'$t9', '11100':'$gp', '11101':'$sp',
# '11110':'$fp', '11111':'$ra'}
rOps = {'000000': {'add', 'sub'}}
rFuncts = {'100000': 'add', '100010': 'sub'}
iTypes = {'001000': 'addi'}
registerFileValues = {'$s0': 0, '$s1': 0, '$s2': 0, '$s3': 0, '$s4': 0, '$s5': 0, '$s6': 0, '$s7': 0}
outcodes = {'add': '1001000100', 'sub': '1001000100', 'addi': '0101000000'}


# quit program
def quitNicely():
    outcodeWrite("Too many lines. Number of instructions cannot exceed 100. Quitting program...")
    quit()


# open file and put contents into a variable
def openFile():
    with open(args.input, 'r') as f:
        cont = f.read()
        # dont forget to close the file
        f.close()
    return cont


# write and output file
def outcodeWrite(thingToWrite):
    with open('out_control.txt', 'a') as w:
        w.write(thingToWrite)
        w.write('\n')
        w.close()


# write and output file (reg)
def outregWrite(thingToWrite):
    with open('out_registers.txt', 'a') as w:
        w.write(thingToWrite)
        w.write('\n')
        w.close()


# clear file when u restart
def clearFile(filename):
    with open(filename, 'w') as o:
        o.write('')
        o.close()


# given a line, gets the opcode out and checks it against the hashmaps to find the type and call corresponding functions
def findType(line):
    opcode = line[0:6]
    if opcode in iTypes:
        parseIType(line, opcode)
    elif opcode == '':
        pass
    else:
        parseRType(line, opcode)


# for r type, given a line and opcode figure
# out what type it is and call the write function correctly, then call the function to do the correct action
def parseRType(line, opcode):
    funct = line[26:]
    txtOp = rOps[opcode]
    txtFunct = rFuncts[funct]
    if txtFunct not in txtOp:
        print("unsupported instruction format. skipping instruction")
        return
    outcodeWrite(outcodes[txtFunct])
    chooseOperation(txtFunct, line)


# for i type, given a line and opcode call the write function correctly, then call the function to do the correct action
def parseIType(line, opcode):
    txtOp = iTypes[opcode]
    outcodeWrite(outcodes[txtOp])
    chooseOperation(txtOp, line)


# takes the name of the operation and calls the right function
def chooseOperation(operationName, line):
    match operationName:
        case 'add':
            add(line)
        case 'sub':
            sub(line)
        case 'addi':
            addi(line)
        case _:
            print("unsupported instruction format. skipping instruction")
            return


def add(line):
    rs = line[6:11]
    rt = line[11:16]
    rd = line[16:21]
    # rd = rs + rt
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrd = registerFileValues[modregisters[rd]]
    valrd = valrs + valrt
    registerFileValues[modregisters[rd]] = valrd


def sub(line):
    rs = line[6:11]
    rt = line[11:16]
    rd = line[16:21]
    # rd = rs + rt
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrd = registerFileValues[modregisters[rd]]
    valrd = valrs - valrt
    registerFileValues[modregisters[rd]] = valrd


def addi(line):
    rs = line[6:11]
    rt = line[11:16]
    imm = line[16:]
    immDec = binaryToDecimal(imm)
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrt = valrs + immDec
    registerFileValues[modregisters[rt]] = valrt


def binaryToDecimal(binary):
    result = 0
    binary = str(binary)
    binary = binary[::-1]
    for i in range(0, len(binary), 1):
        if binary[i] == '1':
            result += pow(2, i)
    return result


# formats the registers hashmap to the required format then passes to the registerfile write function
def updateRegFile(programCounter):
    thingToWrite = str(programCounter) + "|" + str(registerFileValues['$s0']) + "|" + str(
        registerFileValues['$s1']) + "|" + str(registerFileValues['$s2']) + "|" + str(
        registerFileValues['$s3']) + "|" + str(registerFileValues['$s4']) + "|" + str(
        registerFileValues['$s5']) + "|" + str(registerFileValues['$s6']) + "|" + str(registerFileValues['$s7'])
    outregWrite(thingToWrite)


# line counter, program should exit if this > 100
def checkLineCounter(linecounter):
    if linecounter > 100:
        quitNicely()


def main():
    clearFile('out_control.txt')
    clearFile('out_registers.txt')
    fileContents = openFile()
    fileContents = re.split('\n', fileContents)
    programCounter = 65536
    linecounter = 0
    for line in fileContents:
        linecounter += 1
        checkLineCounter(linecounter)
        updateRegFile(programCounter)
        findType(line)
        programCounter += 4


if __name__ == "__main__":
    main()
