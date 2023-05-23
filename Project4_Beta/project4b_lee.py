# This is a sample Python script.

import argparse
import string
import re
from bitstring import BitArray

parser = argparse.ArgumentParser()
parser.add_argument("input", help="file with input to the translator", type=str)
parser.add_argument("memory", help="file with disk memory.txt values for the simulator", type=str)
args = parser.parse_args()
modregisters = {'00000': '$s0', '00001': '$s1', '00010': '$s2', '00011': '$s3', '00100': '$s4', '00101': '$s5',
                '00110': '$s6', '00111': '$s7'}
rOps = {'000000': {'add', 'sub'}}
rFuncts = {'100000': 'add', '100010': 'sub'}
iTypes = {'001000': 'addi', '100011': 'lw', '101011': 'sw', '000100': 'beq', '000101': 'bne'}
registerFileValues = {'$s0': 0, '$s1': 0, '$s2': 0, '$s3': 0, '$s4': 0, '$s5': 0, '$s6': 0, '$s7': 0}
outcodes = {'add': '100100010', 'sub': '100100010', 'addi': '010100000', 'lw': '011110000', 'sw': '010001000',
            'beq': '000000101', 'bne': '000000111'}
instrMap = {}
memoryMap = {}
index = 0
programCounter = 65536


# open the read file and put contents into a variable
def openAndLoadInstrFile():
    with open(args.input, 'r') as f:
        cont = f.read()
        cont = re.split('\n', cont)
        f.close()
    for i in range(0, len(cont), 1):
        pcInd = 65536 + (i * 4)
        instrMap[pcInd] = cont[i]


# open memory.txt and load it into my hashmap {linenum:value}
def openAndLoadMemFile():
    with open(args.memory, 'r') as f:
        cont = f.read()
        cont = re.split('\n', cont)
        f.close()
        for i in range(0, len(cont), 1):
            memoryMap[i] = cont[i]


# write to the code instructions output file
def outcodeWrite(thingToWrite):
    with open('out_control.txt', 'a') as o:
        o.write(thingToWrite)
        o.write('\n')
        o.close()


# write to the register report output file
def outregWrite(thingToWrite):
    with open('out_registers.txt', 'a') as o:
        o.write(thingToWrite)
        o.write('\n')
        o.close()


# write to the memory.txt report output file
def outMemoryWrite():
    with open('out_memory.txt', 'a') as o:
        for item in memoryMap:
            o.write(memoryMap[item])
            o.write('\n')
        o.close()


# clear a file when u re run it
def clearFile(filename):
    with open(filename, 'w') as w:
        w.write('')
        w.close()


# given a line, gets the opcode out and checks it against the hashmaps to find the type and call corresponding functions
def findType(line):
    opcode = line[0:6]
    if (opcode in iTypes):
        parseIType(line, opcode)
    elif (opcode == ''):
        pass
    else:
        parseRType(line, opcode)


# for r type, given a line and opcode figure out what type it is and call the write function correctly, then call the
# function to do the correct action
def parseRType(line, opcode):
    funct = line[26:]
    txtOp = rOps[opcode]
    txtFunct = rFuncts[funct]
    if txtFunct not in txtOp:
        print("unsupported instruction format. skipping instruction")
        return
    chooseOperation(txtFunct, line)


# for i type, given a line and opcode call the write function correctly, then call the function to do the correct action
def parseIType(line, opcode):
    txtOp = iTypes[opcode]
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
        case 'lw':
            lw(line)
        case 'sw':
            sw(line)
        case 'bne':
            bne(line)
        case 'beq':
            beq(line)
        case _:
            print("unsupported instruction format. skipping instruction")
            return


def add(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    rd = line[16:21]
    print('add ', modregisters[rd], " ", modregisters[rs], " ", modregisters[rt])
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrd = registerFileValues[modregisters[rd]]
    valrd = valrs + valrt
    registerFileValues[modregisters[rd]] = valrd
    programCounter += 4
    if (valrd == 0):
        flag = "1"
    else:
        flag = "0"
    outcodeWrite(outcodes['add'] + flag)


def sub(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    rd = line[16:21]
    print('sub ', modregisters[rd], " ", modregisters[rs], " ", modregisters[rt])
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrd = registerFileValues[modregisters[rd]]
    valrd = valrs - valrt
    registerFileValues[modregisters[rd]] = valrd
    programCounter += 4
    if valrd == 0:
        flag = "1"
    else:
        flag = "0"
    outcodeWrite(outcodes['sub'] + flag)


def addi(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    imm = line[16:]
    immDec = binaryToDecimal(imm)
    print('addi ', modregisters[rs], " ", modregisters[rt], " ", immDec)
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    valrt = valrs + immDec
    registerFileValues[modregisters[rt]] = valrt
    programCounter += 4
    if valrt == 0:
        flag = "1"
    else:
        flag = "0"
    outcodeWrite(outcodes['addi'] + flag)


def lw(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    offset = line[16:]
    valrs = registerFileValues[modregisters[rs]]
    offset = binaryToDecimal(offset)
    offset = offset * 4
    print('lw ', modregisters[rs], " ", modregisters[rt], " ", offset)
    if (offset in memoryMap):
        valrt = memoryMap[offset]
    else:
        segFault()
    registerFileValues[modregisters[rt]] = int(valrt)
    programCounter += 4
    outcodeWrite(outcodes['lw'] + "0")


def sw(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    offset = line[16:]
    valrs = registerFileValues[modregisters[rs]]
    offset = binaryToDecimal(offset)
    offset = offset * 4
    print('sw ', modregisters[rs], " ", modregisters[rt], " ", offset)
    if (offset in memoryMap):
        memoryMap[offset] = valrt
    else:
        segFault()
    programCounter += 4
    outcodeWrite(outcodes['sw'] + "0")


def bne(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    offset = line[16:]
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    offset = binaryToDecimal(offset)
    offset = offset * 4
    print('bne ', modregisters[rs], " ", modregisters[rt], " ", offset)
    if (valrs == valrt):
        programCounter += 4
        outcodeWrite(outcodes['bne'] + "1")
        return
    programCounter = programCounter + offset + 4
    outcodeWrite(outcodes['bne'] + "0")


def beq(line):
    global programCounter
    rs = line[6:11]
    rt = line[11:16]
    offset = line[16:]
    valrs = registerFileValues[modregisters[rs]]
    valrt = registerFileValues[modregisters[rt]]
    offset = binaryToDecimal(offset)
    offset = offset * 4
    print('beq ', modregisters[rs], " ", modregisters[rt], " ", offset)
    if (valrs != valrt):
        programCounter += 4
        outcodeWrite(outcodes['beq'] + "0")
        return
    programCounter = programCounter + offset + 4
    outcodeWrite(outcodes['beq'] + "1")


def binaryToDecimal(binary):
    b = BitArray(bin=binary)
    immediate = b.int
    return immediate


# formats the registers hashmap to the required format then passes to the registerfile write function
def updateRegFile(programCounter):
    thingToWrite = str(programCounter) + "|" + str(registerFileValues['$s0']) + "|" + str(
        registerFileValues['$s1']) + "|" + str(registerFileValues['$s2']) + "|" + str(
        registerFileValues['$s3']) + "|" + str(registerFileValues['$s4']) + "|" + str(
        registerFileValues['$s5']) + "|" + str(registerFileValues['$s6']) + "|" + str(registerFileValues['$s7'])
    outregWrite(thingToWrite)


# this should be triggered if we look for something in memory.txt that isnt there, memory.txt address not found/too large
# or if branch instruction goes out of bounds
def segFault():
    outcodeWrite("!!!Segmentation Fault!!!")
    updateRegFile(programCounter)
    outMemoryWrite()
    quit()


def main():
    clearFile('out_control.txt')
    clearFile('out_registers.txt')
    clearFile('out_memory.txt')
    openAndLoadMemFile()
    openAndLoadInstrFile()
    global programCounter
    fileContentsCounterMax = (len(instrMap) * 4) + 65536
    while programCounter < fileContentsCounterMax - 4:
        if programCounter < 65536 or programCounter > fileContentsCounterMax:
            segFault()
        updateRegFile(programCounter)
        findType(instrMap[programCounter])
    updateRegFile(programCounter)
    outMemoryWrite()


if __name__ == "__main__":
    main()
