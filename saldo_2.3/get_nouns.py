"""Hämtar alla substantiv ur saldom.xml samt alla böjningar av det substantivet"""
import re

def create_nounfile():
    START_PATTERN = '^<LexicalEntry>$'
    END_PATTERN = '^</LexicalEntry>$'
    POSTAG_PATTERN = '^   <feat att="partOfSpeech" val="nn"/>$'
    LEM_PATTERN = "lemgram"

    with open('saldom.xml') as file:
        se_match = False
        pos_match = False
        current_lemma = ""
        word = ""
        wordlist = []
        new_file = None

        for line in file:

            if re.match(START_PATTERN, line):
                se_match = True
                continue
            elif re.match(END_PATTERN, line):
                with open("nouns.xml", "a") as nyfil:
                    for string in wordlist:
                        nyfil.write(string)
                    wordlist = []
                pos_match = False
                se_match = False
                continue
            elif se_match:
                if LEM_PATTERN in line:
                    current_lemma = line
                if re.match(POSTAG_PATTERN, line):
                    pos_match = True
                    i = 0
                    continue
                elif pos_match:
                    if i ==0:
                        wordlist.append(current_lemma)
                        key = line
                        i +=1
                    else:
                        wordlist.append(line)
                        i +=1

def structure_nounfile(filename):
    WORD_PATTERN = '\b  <feat att="writtenForm" val="'
    #'\b .*\batt="writtenForm"\bval=""'

    with open(filename) as f:

        for line in f:
            if re.match(WORD_PATTERN, line):
                print("Hej")
                print(line)












words = create_nounfile()
#structure_nounfile("nouns.txt")
