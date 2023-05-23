# Python MIPS assembly to Machine Language Converter
# ECPE 170 project made by MING HAO LEE

import argparse
import string
import re

parser = argparse.ArgumentParser()
parser.add_argument("input", help="file with input to the translator", type=str)
args = parser.parse_args()

rTypes = ['add', 'sub', 'sll', 'srl', 'slt']
rTypeOpCodes = {'add': '000000', 'sub': '000000', 'sll': '000000', 'srl': '000000', 'slt': '000000'}
rTypeFunctCodes = {'add': '100000', 'sub': '100010', 'sll': '000000', 'srl': '000010', 'slt': '101010'}
iTypes = ['addi', 'beq', 'bne', 'lw', 'sw']
iTypeOpCodes = {'addi': '001000', 'beq': '000100', 'bne': '000101', 'lw': '100011', 'sw': '101011'}
registers = {'$zero': 0, '$v0': 2, 'v1': 3, '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7, '$t0': 8, '$t1': 9, '$t2': 10,
             '$t3': 11, '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15, '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
             '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23, '$t8': 24, '$t9': 25, '$gp': 28, '$sp': 29, '$fp': 30,
             '$ra': 31}


# clear the output file when you first start the program
def clearFile():
    with open('out_code.txt', 'w') as w:
        w.write('')
        w.close()


# open the read file
def openFile():
    with open(args.input, 'r') as f:
        cont = f.read()
        # dont forget to close the file
        f.close()
    return cont


# create and open the write file name as out_code.txt
def writeFile(line):
    with open('out_code.txt', 'a') as o:
        o.write(line)
        o.write('\n')
        o.close()


# quit program gracefully if necessary
def quitNicely():
    writeFile('!!! invalid input !!!')
    quit()


# decide which binary funct a number should use! pos or neg
def decimalToBinary(n):
    n = int(n)
    if (n >= 0):
        return posToBinary(n)
    else:
        return negToBinary(n)


# convert a decimal number to a binary number
def posToBinary(n):
    return bin(n).replace("0b", "")


# convert a negative decimal number to 2s complement
def negToBinary(n):
    n = posToBinary(n)
    n = n[1:]
    n = flipBits(n)
    n = addOne(n)
    return n


def addOne(n):
    # loop through string backwards, change first 0 to 1 and 1 to 0 in the meantime
    n = list(n)
    for i in range(len(n) - 1, 0 - 1, -1):
        if (n[i] == '0'):
            n[i] = '1'
            return "".join(n)
        elif (n[i] == '1'):
            n[i] = '0'


def flipBits(n):
    m = ""
    for bit in n:
        if (bit == '0'):
            m += '1'
        else:
            m += '0'
    return m


# helper function, remove commas from a line
def removeChar(line, remove):
    for i in range(0, len(line), 1):
        line[i] = line[i].replace(remove, '')
    return (line)


# helper function, split misformatted list correctly
def reformat(line, charToChange, popNormal):
    addList = line[1].split(charToChange)
    if (popNormal):
        line.pop()
    else:
        line.pop(1)
    for x in addList:
        line.append(x)
    return line


# helper function, pads a binary number as a string with specified char
def padBits(num, bit, length):
    newNum = ''
    padNum = length - len(num)
    if (padNum < 0):
        quitNicely()
    for i in range(0, padNum, 1):
        newNum += bit
    newNum += num
    return newNum


# helper function, takes a register and returns the binary. returns -1 if invalid register
def makeBinReg(reg):
    if (registers.get(reg)):
        reg = registers[reg]
        reg = decimalToBinary(reg)
        reg = str(reg)
        reg = padBits(reg, '0', 5)
        return reg
    elif (reg == 0):
        return '00000'
    else:
        # remove $ and check if its 0-31 value
        reg = reg.replace('$', '')
        reg = int(reg)
        if (reg < 32 and reg >= 0):
            reg = decimalToBinary(reg)
            reg = str(reg)
            reg = padBits(reg, '0', 5)
            return reg
        else:
            quitNicely()


# function that receives a line and passes to other functions to parse
def decideType(line):
    # skip empty lines
    if (len(line) == 0):
        return
    # skip comments
    if (line[0] == '#'):
        return
    # make it into a list to handle more finely
    line = line.split()
    if (rTypes.count(line[0])):
        parseRType(line)
    elif (iTypes.count(line[0])):
        parseIType(line)
    # not valid r or i
    else:
        quitNicely()


# takes an r type instruction and puts the values into variables, so it can be put into binary
def parseRType(line):
    if (line[0] == 'sll' or line[0] == 'srl' or line[0] == 'slt'):
        parseSpecialRType(line)
        return
    reformat(line, ',', True)
    op = line[0]
    rs = line[2]
    rt = line[3]
    rd = line[1]
    shamt = 0
    changeRToBinary(op, rs, rt, rd, shamt)
    return


# some of the r types have shift amounts, thought it should go in a special function
def parseSpecialRType(line):
    removeChar(line, ',')
    op = line[0]
    rs = 0
    rt = line[2]
    rd = line[1]
    shamt = line[3]
    changeRToBinary(op, rs, rt, rd, shamt)


# takes an i type instruction and puts the values into variables, so it can be put into binary
def parseIType(line):
    if (len(line[0]) == 2):
        parseSpecialIType(line)
        return
    reformat(line, ',', True)
    op = line[0]
    rs = line[1]
    rt = line[2]
    offset = line[3]
    changeIToBinary(op, rs, rt, offset)


# some of the i types had parenthesis, thought it should go in a special function
def parseSpecialIType(line):
    reformat(line, '(', True)
    removeChar(line, ')')
    reformat(line, ',', False)
    op = line[0]
    rs = line[1]
    rt = line[2]
    imm = line[3]
    changeIToBinary(op, rs, rt, imm)


def changeRToBinary(op, rs, rt, rd, shamt):
    binOp = rTypeOpCodes[op]
    # need to check if we have a valid register!
    binRs = makeBinReg(rs)
    binRt = makeBinReg(rt)
    binRd = makeBinReg(rd)
    shamt = int(shamt)
    shamt = decimalToBinary(shamt)
    shamt = str(shamt)
    shamt = padBits(shamt, '0', 5)
    binFunct = rTypeFunctCodes[op]
    binInstruct = binOp + binRs + binRt + binRd + shamt + binFunct
    writeFile(binInstruct)


def changeIToBinary(op, rs, rt, imm):
    binOp = iTypeOpCodes[op]
    binRs = makeBinReg(rs)
    binRt = makeBinReg(rt)
    imm = int(imm)
    if (op == 'beq' or op == 'bne'):
        imm /= 4
    if (imm < 0):
        # negative needs to be padded w 1s
        imm = decimalToBinary(imm)
        imm = str(imm)
        imm = padBits(imm, '1', 16)
    else:
        # be normal
        imm = decimalToBinary(imm)
        imm = str(imm)
        imm = padBits(imm, '0', 16)
    if (op == 'addi'):
        binInstruct = binOp + binRt + binRs + imm
    else:
        binInstruct = binOp + binRs + binRt + imm
    writeFile(binInstruct)


def main():
    clearFile()
    result = openFile()
    result = re.split('\n', result)
    for line in result:
        decideType(line)


if __name__ == "__main__":
    main()
