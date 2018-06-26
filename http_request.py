# coding=utf-8

import requests
import json
import sys



""" Om man vill välja fil att läsa in originaltext från i koden
görs det med de två översta raderna. Om man vill läsa in direkt
i kommandotolken används de två nedersta raderna. Då läggs
filnamnet till efter kodfilen man kallar på, t.ex.
'python http_request.py textfile.txt'. Går också att ha en sträng
direkt i koden. """
#doc = open(sys.argv[-1], 'r')
#docu = doc.read()

if len(sys.argv) > 1:
    doc = open(sys.argv[-1], 'r')
    docu = doc.read()
else:
    #string = "Huset är blått. Huset målades av Kalle. Kalle målade huset. Huset byggdes av Lisa. Lisa byggde huset."
    docu = '" Vad fint huset har blivit ", sa Lisa. " Det blir kanske regn imorgon om vi har otur ", viskade han tyst.'
    #docu = "Det verkar bli fint väder imorgon. Imorgon verkar det bli fint väder."

"""För Stagger: byt ut "nlp" i "nlpTagger" mot "s"
Finns olika options, men jag behöver egentligen bara tagger och parser"""
def preprocess(string):
    """ Öppnar fil att skriva preprocessad text till """
    f = open('workfile', 'w')
    
    url = 'http://www.ida.liu.se/projects/scream/services/sapis/service/'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {'options' : 'Tagger(-sTagger, -parser)', 'document' : string}
    # 'options' : 'LexicalMetrics()\tSurfaceMetrics()\tStructuralMetrics()\tTagger(-nlpTagger, -parser)'

    """Textförenklingsregler"""
    #opt_str = "-straightOrder\n-pass2act\n-quoteInvert\n-decker\n-split"

    """Fler options, behöver inte dessa"""
    #data = {'options' : "StilLett(pre{\n-stagger\n-suc2negra\n-phraseStructParser\n}\neasy{\n" +
    #	opt_str + "}\npost{\n-cleanNoHTML\n})",'document' : docu}

    """Skickar en request till Sapis. Går att printa
    antingen bara taggad och parsad data eller med
    alla mått. Den senare är snyggare."""
    r = requests.post(url, headers=headers, data=json.dumps(data))
    #print(r.json()['_tags'])
    #print(json.dumps(r.json(), sort_keys=True, indent=4))

    """Skriver över output från Sapis i en textfil.
    Filen har conll-format."""
    for i in r.json()['_tags']:
        if i[0:2] == '1\t':
            f.write("\n")
        f.write(i.encode('utf-8') + "\n")
        
    f.close()
    if len(sys.argv) > 1:
        doc.close()
    return None

preprocess(docu)