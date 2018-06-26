# -*- coding: utf-8 -*-
import re
import codecs

with codecs.open('oregelbundna.txt', 'r', encoding='utf8') as f1:
    oregel = f1.read()
    oregel = oregel.split('\n')
    for word in oregel:
        oregel[oregel.index(word)] = word.split('\t')

with codecs.open('opp_vb.txt', 'r', encoding='utf8') as f2:
    opp = f2.read()
    opp = opp.split('\n')
    for line in opp:
        opp[opp.index(line)] = line.split('\t')
                
# Group 1
def group1(w, c, info):
    x = {'pres': 'r', 'pret': 'de', 'sup': 't'}
    y = {'pres': 's', 'pret': 'des', 'sup': 'ts'}
    if info[0] == 's':
        w = w[:-1]
        return w + y[c]
    w = w + x[c]
    return w

# Group 2
def group2(w, c, info):
    x = {'pres': 'er', 'pret': 'de', 'sup': 't'}
    y = {'pres': 's', 'pret': 'des', 'sup': 'ts'}
    p = re.compile('[eyuioaåäö][rl][ae]$')
    p2 = re.compile('[^eyuioaåäö][dt]$')
    p3 = re.compile('[eyuioaåäö]d$')
    p4 = re.compile('(mm|nn)$')
    p5 = re.compile('ss$')
    
    # 2s
    if info[0] == 's':
        w = w[:-2]
        if w[-1] in "skptf":
            y['pret'] = 'tes'
        if w[-2:] == 'ss':
            y['pres'] = ''
        if c in ['pret', 'sup'] and p4.findall(w):
            w = w[:-1]
        w = w + y[c]
        return w
        
    # 2a + 2m
    else:
        if p.findall(w) and info[1] == 'hyra':
            x['pres'] = ''
        w = w[:-1]
        if c == 'pret':
            if w[-1] in "skptf":
                x['pret'] = 'te'
        if p2.findall(w):
            x['pret'] = 'e'
            if c == 'sup':
                if w[-1] in 'dt':
                    w = w[:-1]
        if p3.findall(w):
            x['pret'] = 'dde'
            x['sup'] = 'tt'
            if c in ['pret', 'sup']:
                w = w[:-1]
        if c in ['pret', 'sup'] and p4.findall(w):
            w = w[:-1]
            
    w = w + x[c]
    return w

# Group 3
def group3(w, c, info):
    x = {'pres': 'r', 'pret': 'dde', 'sup': 'tt'}
    if info == 's':
        x = {'pres': 's', 'pret': 'ddes', 'sup': 'tts'}
        w = w[:-1]
    w = w + x[c]
    return w

# Group 4
def group4(w, c, info):
    p = re.compile('[eyuioaåäö][rl]$')
    p2 = re.compile('i\w$')
    p3 = re.compile('i\w{2}$')
    p4 = re.compile('ju\w$')
    p5 = re.compile('u\w{2}$')
    p6 = re.compile('y\w$')
    p7 = re.compile('ar$')
    p8 = re.compile('åt$')
    p9 = re.compile('mm$')
    p10 = re.compile('[aå]ll$')
    p11 = re.compile('ät$')
    p12 = re.compile('är$')
    
    w = w[:-1]
    
    if info[0] == 's':
        w = w[:-1]
        if c == 'pres':
            return w + 's'
    
    if c == 'pres':
        if not p.findall(w):
            w = w + 'er'
    else:
        if c == 'pret':
            if p7.findall(w):
                w = w[:-2] + 'o' + w[-1]
            elif p8.findall(w):
                w = w[:-2] + 'ä' + w[-1]
            elif p9.findall(w):
                w = w[:-1]
            elif p10.findall(w):
                w = w[:-4] + 'ö' + w[-2:]
            elif p11.findall(w):
                w = w[:-4] + 'å' + w[-1]
        if p2.findall(w) and c == 'pret':
            w = w[:-2] + 'e' + w[-1]
        elif p3.findall(w):
            if c == 'pret':
                w = w[:-3] + 'a' + w[-2:]
            else:
                w = w[:-3] + 'u' + w[-2:]
        elif p4.findall(w) or p6.findall(w):
            if c == 'pret':
                w = w[:-2] + 'ö' + w[-1]
            else:
                w = w[:-2] + 'u' + w[-1]
        elif p5.findall(w):
            if c == 'pret':
                w = w[:-3] + 'ö' + w[-2:]
            else:
                w = w[:-3] + 'u' + w[-2:]
        elif p12.findall(w):
            if c == 'pret':
                w = w[:-2] + 'a' + w[-1]
            else:
                w = w[:-2] + 'u' + w[-1]
    if c == 'sup':
        w += 'it'
    if info[0] == 's':
        w += 's'
    return w


        
def oregelbundna(w, word, c):
    x = {'pres': 1, 'pret': 2, 'sup': 3}
    y = x[c]
    p = re.match(r'(\w*)' + re.escape(word[0]) + r'$', w)
    word = word[y]
    if w != word:
        if p:
            begin = p.group(1)
            word = begin + word
    return word

def conjugate(w, c, what):
    if c == "inf":
        return w
    no_match = True
    for line in opp:
        s = False
        if what in line and 's' in line[1]:
            m3 = re.match(r'.+_(\d)(\w+)_.+', line[1])
            if m3 and 's' in m3.group(1):
                s = True
                return what
        elif w in line and s == False:
            o = False
            paradigm = line[1]
            m = re.match(r"(.+)_(\d)(\w+)_(.+)", paradigm)
            m2 = re.match(r".+_(\w+)_(.+)", paradigm)
            if m:
                n = int(m.group(2))
                info = m.group(3, 4)
                lemma = m.group(1)
                for word in oregel:
                    m4 = re.match(r'\w*' + word[0] + r'$', w)
                    if m4:
                        o = True
                        no_match = False
                        w_ = oregelbundna(w, word, c)
                        return w_
                if o == False:
                    if n == 1:
                        return group1(w, c, info)
                    elif n == 2:
                        return group2(w, c, info)
                    elif n == 3:
                        return group3(w, c, info)
                    elif n == 4:
                        return group4(w, c, info)
            elif m2:
                info = m2.group(1, 2)
    if no_match == True:
        return w
