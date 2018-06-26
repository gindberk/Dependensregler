# coding: utf-8
import sys
import io

def make_lower(word):
    return word.lower()

def make_upper(word):
    first = word[0].upper()
    word = first + word[1:]
    return word

def clean():
    f = sys.stdin
    l = []
    text = ""
    for line_no, line in enumerate(f):
        line = line.strip('\n').split('\t')
        l.append(line)
    for line in l:
        if len(line) > 1:
            if line[1] in ',.?!:;)': # hantera "-
                text = text[:-1] + line[1] + " "
            elif line[1] == '(':
                text = text + line[1]
            else:
                if line == l[0] or len(l[l.index(line)-1]) == 1:
                    if line[1].islower():
                        text += make_upper(line[1]) + " "
                    else:
                        text += line[1] + " "
                else:
                    if line[3] == "PM":
                        text += line[1] + " "
                    elif l[l.index(line) - 1][1] == '-':
                        text += line[1] + " "
                    else:
                        if line[1].islower():
                            text += line[1] + " "
                        else:
                            text += make_lower(line[1]) + " "
        if len(l[l.index(line) + 1]) < 4:
            text += '\n'
    return text

print(clean())