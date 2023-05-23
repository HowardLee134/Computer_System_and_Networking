###This is a Comp 170 Class Project modified by MING HAO LEE
#Please using command line: cache_Lee.py --type=d --cache_size=128 --block_size=32 --memfile= (mem1.txt)[This is the input file should be .txt file]
# and will be output as file named: memOut.txt.


import argparse

parser = argparse.ArgumentParser()
import argparse
import string
import re
import math

parser = argparse.ArgumentParser()
parser.add_argument("--type", help="cache type, direct (d) or n way set associative (s)", type=str)
parser.add_argument("--cache_size", help="The total cache size in bytes. This value must be a power of 2.", type=int)
parser.add_argument("--block_size", help="The size of a block in bytes. This value must be a power of 2.", type=int)
parser.add_argument("--memfile",
                    help="The input text file that contains the sequence of memory accesses. Each line of the input file is a memory address in hexadecimal format.",
                    type=str)
parser.add_argument("--nway", help="Number of ways for set associatve cache", type=int, required=False)
args = parser.parse_args()

cache = [{}]
byteoffset = 2
wordoffset = 0
index = 0
tag = 0
memacc = 0
hits = 0


# quit program
def quitNicely():
    # add message to output file here if necessary
    quit()


# open the read file and put contents into a variable
def openFile():
    with open(args.memfile, 'r') as f:
        cont = f.read()
        cont = re.split('\n', cont)
        # dont forget to close the file
        f.close()
    return cont


# write to the code instructions output file
def outputWrite(thingToWrite):
    with open('memOut.txt', 'a') as o:
        o.write(thingToWrite)
        o.write('\n')
        o.close()


# clear the output file (when you first start the program)
def clearFile(filename):
    with open(filename, 'w') as w:
        w.write('')
        w.close()


def binaryToDecimal(binary):
    result = 0
    binary = str(binary)
    binary = binary[::-1]
    for i in range(0, len(binary), 1):
        if binary[i] == '1':
            result += pow(2, i)
    return result


# convert binary number as a string with specified char
def padBits(num, bit, length):
    if (num == ''):
        return ''
    newNum = ''
    padNum = length - len(num)
    if (padNum < 0):
        quitNicely()
    for i in range(0, padNum, 1):
        newNum += bit
    newNum += num
    return newNum


# convert hax to binary (as string)
def hexToBinary(hex):
    if hex == '':
        return ''
    n = int(hex, 16)
    bStr = ''
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    res = bStr
    return res


# check if a number is power of 2
def isPowerOfTwo(n):
    return math.ceil(logBase2(n)) == math.floor(logBase2(n));


# return the log base 2 of a number
def logBase2(num):
    return (math.log10(num) / math.log10(2));


# given the cache size and block size, initialize the 4 global sizes accordingly
def initBitSizes(cache_size, block_size):
    global wordoffset
    global byteoffset
    global index
    global tag
    numwords = block_size / 4  # divide the size of a block by the size of each word
    wordoffset = logBase2(numwords)
    numblocks = cache_size / block_size
    index = logBase2(numblocks)
    tag = 32 - index - wordoffset - byteoffset
    tag = int(tag)
    index = int(index)
    wordoffset = int(wordoffset)


# check if the program can be run with the given input
def checkInput(type, cache_size, block_size):
    if (type != 'd' and type != 's'):
        print('invalid input ')
        return False
    if (logBase2(cache_size) != True):
        print('invalid input, cache size should be a power of 2')
        return False
    if (logBase2(block_size) != True):
        print('invalid input, block size should be a power of 2')
        return False
    return True


# returns the hit rate given the number of hits and memory accesses
def hitRate(hits, memacc):
    return (hits / memacc) * 100


# given the type and the nway value, initialize the cache data structures
def initDirectMappedCaches(type, nway):
    if (type == 's'):
        for i in range(1, nway, 1):
            cache.append({})


# given memory access in hex make it into a properly formatted binary number
def formatHex(hex):
    bin = hexToBinary(hex)
    padded = padBits(bin, '0', 32)
    return padded


# given binary, split it up and assign the necessary variables, then call memory access function
def processBinary(hex, binary):
    tagbits = binary[0:tag]
    indexbits = binary[tag:(index + tag)]
    wordoffsetbits = binary[(index + tag):(index + tag + wordoffset)]
    byteoffsetbits = binary[(index + tag + wordoffset):]
    memoryAccess(hex, binary, tagbits, indexbits, wordoffsetbits, byteoffsetbits)


# given the memory address broken down, loop through the cache for the tag+index combination
# call the write to output function reporting hit/miss etc
# remember to check index first and then see if tags match
def memoryAccess(hex, binary, tagbits, indexbits, wordoffsetbits, byteoffsetbits):
    global hits
    if (byteoffsetbits != '00'):
        formatAndOutput(hex, tagbits, indexbits, "U")
    if (binaryToDecimal(binary) % 4 != 0):
        formatAndOutput(hex, tagbits, indexbits, "U")
    found = False
    for dm in cache:
        if indexbits in dm:
            if tagbits == dm[indexbits]:
                formatAndOutput(hex, tagbits, indexbits, "HIT")
                hits += 1
                found = True
                return
    if (found == False):
        formatAndOutput(hex, tagbits, indexbits, "MISS")
        # loop through whole cache, if a particular dm doesnt have the index then lets add it
        for i in range(0, len(cache), 1):
            if indexbits not in cache[i]:
                cache[i][indexbits] = tagbits
                return
        # if we dont find one at all, as in they all have that index already, overwrite the first one
        cache[0][indexbits] = tagbits


# formats the hex and binary to output and calls function to write to output file
def formatAndOutput(hex, tagbits, indexbits, status):
    thingToWrite = hex + "|" + tagbits + "|" + indexbits + "|" + status
    outputWrite(thingToWrite)


def main():
    clearFile('memOut.txt')
    global memacc
    global hits
    initDirectMappedCaches(args.type, args.nway)
    initBitSizes(args.cache_size, args.block_size)
    lines = openFile()
    for i in range(0, len(lines) - 1, 1):
        memacc += 1
        binary = formatHex(lines[i])
        processBinary(lines[i], binary)
    outputWrite("hit rate: " + str(hitRate(hits, memacc)))


if __name__ == "__main__":
    main()
