from bs4 import BeautifulSoup
import re

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
	definitionMatch = re.search('<def>.*?</def', str(synset))
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

#print(str(idToWordsDict))
#print(str(wordToSensesDict))

#sentence = "yaz gelmek bahar kış"
sentence = "blok bölge"      # "Optik fare" denedim patladı çünkü wordnette optik kelimesi yok
tokens = sentence.split()
target = "blok"  

def getSenses(word):
	return wordToSensesDict[word]

def getWords(senseId):
	return idToWordsDict[senseId][1]

def getHypernym(senseId):
	return idToWordsDict[senseId][0]

def setHypernym(senseId, hypernymId):
	idToWordsDict[senseId][0] = hypernymId

# Wordnete bunu hem yaz hem yazmak olarak sokmamız lazım çünkü wordnette yaz'ın fiil hali yok
# Burda zemberek falan kullanılacak
# Wordnette olmayan kelimeler için bi if kontrolü lazım yoksa program patlar

def calculate_scores(senseToBag, bigBag, scoresDict, divider):
	list2 = bigBag
	#scoresDict = {}
	for key in senseToBag:
		list1 = senseToBag[key]
		score = len(list(set(list1).intersection(list2))) # Attention: Only uniques
		if key not in scoresDict:
			scoresDict[key] = score
		else:
			scoresDict[key] = scoresDict[key] + (score / divider)


	return scoresDict
	

def disambiguate(tokens, target):
	candidates = wordToSensesDict[target]
	#candidates = candidates + wordToSensesDict[target + "mak"]      # MAK SİLİNECEK
	#print(candidates)
	scoresDict = {}
	#targetBags = []  # Target word'ümüzün tüm senselerinin bagleri
	sensesOfTargetToBag = {}
	bigBag = []      # Diğer her şeyin istiflendiği bag
	for senseId in candidates:
		bag = []
		synset = idToWordsDict[senseId][1]
		for word in synset:
			bag.append(word)
		bag = bag + idToWordsDict[senseId][2]
		sensesOfTargetToBag[senseId] = bag

	# Handling nearby words
	# To add weights, enumerate this for loop and pass the divider into the bigbag
	# Specify a window size here and consider only those tokens
	for token in tokens:
		if token != target:
			senses = wordToSensesDict[token]
			for senseId in senses:
				words = idToWordsDict[senseId][1]
				for word in words:
					if word not in bigBag:
						bigBag.append(word)


	print(bigBag)
	print(sensesOfTargetToBag)
	scoresDict = calculate_scores(sensesOfTargetToBag, bigBag, scoresDict, 1)
	# While there are hypernyms left
	level = 0 # number of iterations
	while level < 3:
		level = level + 1
		#sensesOfTargetToBag'e her sense'in hypernym'inin kelimelerini ekle.
		for senseId in sensesOfTargetToBag:
			hypernymId = getHypernym(senseId)
			if hypernymId != "":
				additionalWords = getWords(hypernymId)
				sensesOfTargetToBag[senseId] = sensesOfTargetToBag[senseId] + additionalWords
				setHypernym(senseId, getHypernym(hypernymId))
		#bigBag'e içindeki her kelimenin her sense'inin hypernym'inin kelimesini ekle.
		for word in bigBag:  # Burda optimizasyon yapılabilir
			senses = getSenses(word)
			for senseId in senses:
				hypernymId = getHypernym(senseId)
				if hypernymId != "":
					additionalWords = getWords(hypernymId)
					bigBag = bigBag + additionalWords
					setHypernym(senseId, getHypernym(hypernymId))

		scoresDict = calculate_scores(sensesOfTargetToBag, bigBag, scoresDict, level)
		#print("RESULTS FROM LEVEL " + str(count))
		#print(sensesOfTargetToBag)
		#print(bigBag)
		#print(scoresDict)
	print(scoresDict)

	# Lazım olabilecek fonksiyonlar
	# getSenses(word)
	# getWords(senseId)


disambiguate(tokens, target)









	