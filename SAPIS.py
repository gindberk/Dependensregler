"""Tagging a sentence from user input"""

import requests
import json
import sys
import os
import readline


def check_and_add_stopsign(sentence):
	"""Checks if the last token in a sentence is a stopsign. If not, add "."."""
	stopsigns = ["!", "?", "."]
	inp = sentence
	if inp[-1] in stopsigns:
		pass
	else:
		inp += "."
	return(inp)


def tag_sentence(sentence):
	"""Tags a sentence with Stagger"""
	# Usage: python3 SAPIS.py
	url = 'https://www.ida.liu.se/projects/scream/services/sapis/service/'
	# Accept and send JSON-Object
	headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
	# Change 'options'
	data = {'options': 'Tagger(-sTagger, -parser)', 'document': sentence}
	r = requests.post(url, headers=headers, data=json.dumps(data))
	# Return one single variable in the response JSON-object:
	taggedText = r.json()['_tags']
	return taggedText


def create_tree_file(taggedText):
	"""Creates a empty file and adds the new conll tree in the file"""
	os.remove("ConLL/newtree.conllx")
	tree = ""
	with open("ConLL/newtree.conllx", "w") as tree_file:
		#adds each row in the tree to the file
		for line in taggedText:
			word_row = line + "\n"
			tree_file.write(word_row)
			tree += word_row
		print(tree)

if __name__ == '__main__':
	sentence = input("Mening att utvardera: ")
	sent = check_and_add_stopsign(sentence)
	tagged = tag_sentence(sent)
	create_tree_file(tagged)
