import re
import pickle

stats = []

text_pattern = re.compile("\s*<feat att=\"writtenForm\" val=\"(.*?)\".*>")
feat_pattern = re.compile("\s*<feat att=\"msd\" val=\"(.*?)\".*>")


def read_file():
	with open("nouns.xml") as infile:
		c = 0

		for line in infile:

			m = text_pattern.match(line)
			if m != None:
				stats.append([m.group(1)])
			n = feat_pattern.match(line)
			if n != None:
				stats[-1].append(n.group(1))
				continue

read_file()

file = open("slut.txt", "w")
line = ""
stats.sort()
for word in stats:
	line += word[0] + " " + word[1] + "\n"
file.write(line)
#f = open("saldo.pickle", "wb")
#pickle.dump(stats, f, protocol=pickle.HIGHEST_PROTOCOL)
file.close()
print("Wrote stats to file")


# Read

#stats = pickle.load(open("sou_stats.pickle", "rb"))
