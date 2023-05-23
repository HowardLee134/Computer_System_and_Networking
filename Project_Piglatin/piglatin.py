# This projector is a convertor reads a .txt file of english input and converts it into piglatin, retaining all
# punctuation while doing so. Please run by navigating to the file in your terminal and typing python3 piglatin.py
# data.txt(data.txt can be replaced by any other .txt file) to execute the program##
### written by MING HAO LEE on 2/02/2023 for ECPE 170 project import argparse ###
import re
import argparse

parser = argparse.ArgumentParser(description="piglatin translator")
parser.add_argument("input", type=str, help="file with data pt the translator")
# parser.add_argument("output", type=str, help="file with data pt the translator")
args = parser.parse_args()


# readfile function
def readFile():
    with open(args.input, 'r') as f:
        word = f.read()
        f.close()
    return word


# write file function
def writeFile(file):
    with open("output.txt", 'w') as f:
        word = f.write(file)
        f.close()


# list of consonant
#consonant = ['B', 'b', 'C', 'c', 'D', 'd', 'F', 'f', 'G', 'g', 'H', 'h', 'J', 'j', 'K', 'k',
#            'L', 'l', 'M', 'm', 'N', 'n', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't',
#             'U', 'u', 'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z']

# list of vowel
vowel = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']

# list of punctuation
punctuations = ['!', '"', '#', '$', '%', '&', '(', ')', '.', '-', '.', '\'', '\'', ';', ',']


def piglatin(sentence):
    # check the word length
    if len(sentence) == 0:
        return ""
    elif len(sentence) < 2:
        if sentence in vowel:
            return sentence + "way"
        # if sentence in punctuations:
        elif sentence in punctuations:
            return sentence
        else:
            return sentence + "ay"
    # piglatin translator
    elif sentence[0] not in vowel and sentence[1] in vowel:
        return sentence[1:] + sentence[:1] + "ay"
    elif sentence[0] not in vowel and sentence[1] not in vowel:
        return sentence[2:] + sentence[:2] + "ay"
    elif sentence[0] in vowel:
        return sentence + "way"


def main():
    finalList = " "
    apple = readFile()
    # separate word and function into a list
    newSentenceList = re.findall(r'\w+|[^\s\w]+', apple)

    for sentence in newSentenceList:
        sentence = piglatin(sentence)
        finalList += sentence + " "

    writeFile(finalList)


if __name__ == "__main__":
    main()
