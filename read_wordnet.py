from bs4 import BeautifulSoup
import re
import json

with open("wordnet.xml") as wordnet:
	soup = BeautifulSoup(wordnet, "html.parser")

idToWordsDict = {}      # Dictionary: Key -> sysnet id,  Value -> List of words in that sysnet + hypernyms
# Tanımlar eklenecek
wordToSensesDict = {}   # Dictionary: Key -> word, Value -> List of sense ids for that word


synsets = soup.find_all("synset")
for synset in synsets:
	#print("Synset is " +   str(synset))
	synsetId = synset.id.string
	hypernymMatch = re.search('<ilr>.*?<type>hypernym</type></ilr>', str(synset))
	hypernymId = ""
	if hypernymMatch: # Else it is empty string
		hypernymId = hypernymMatch.group()[5:-27]
		#print("Hypernym id is: " + hypernymId)      
	
	definition = ""
	definitionMatch = re.search('<def>.*?</def>', str(synset))
	if definitionMatch:
		definition = definitionMatch.group()[5:-6]
	literals = synset.find_all("literal")
	words = []
	definitionWords = definition.lower().replace(',' , ' ').split()
	
	for literal in literals:
		word = ""
		wordMatch = re.search(".*?<sense>", str(literal))
		if wordMatch:
			word = wordMatch.group()[9:-7]
			words.append(word)
		#word = str(literal)[9:-26]   
		
		if word not in wordToSensesDict:
			wordToSensesDict[word] = [synsetId]
		else:
			wordToSensesDict[word].append(synsetId)
	#print(str(words))
	idToWordsDict[synsetId] = [hypernymId, words, definitionWords]


with open('idToWordsDict.json', 'w') as outfile1:
    json.dump(idToWordsDict, outfile1)

with open('wordToSensesDict.json', 'w') as outfile2:
    json.dump(wordToSensesDict, outfile2)








	