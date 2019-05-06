from bs4 import BeautifulSoup
import re
import json

idToWordsDict = {}
wordToSensesDict = {}
with open('idToWordsDict.json') as f:
    idToWordsDict = json.load(f)

with open('wordToSensesDict.json') as f2:
    wordToSensesDict = json.load(f2)

def getSenses(word):
	return wordToSensesDict[word]

def getWords(senseId):
	return idToWordsDict[senseId][1]

def getDefinitionWords(senseId):
	return idToWordsDict[senseId][2]

def getHypernym(senseId):
	return idToWordsDict[senseId][0]

def setHypernym(senseId, hypernymId):
	idToWordsDict[senseId][0] = hypernymId

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
	# BU MAK EKLEME İŞİNİ ZEMBEREK KODU HALLETMELİ, ZEMBEREK EKLENİNCE ALT SATIR DEĞİŞTİRİLECEK
	candidates = candidates + wordToSensesDict[target + "mak"] 
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

		# DEFINITION WORDS'E ZEMBEREK GEREKLİ
		definitionWords =idToWordsDict[senseId][2]
		bag = bag + definitionWords      
		sensesOfTargetToBag[senseId] = bag

	# Handling nearby words
	# To add weights, enumerate this for loop and pass the divider into the bigbag
	# Specify a window size here and consider only those tokens
	targetId = -1
	for i, token in enumerate(tokens):
		if token == target:
			targetId = i
			break

	windowSize = 20
	startIndex = targetId - windowSize
	if startIndex < 0:
		startIndex = 0
	endIndex = targetId + windowSize
	print(endIndex)

	tokens = tokens[startIndex : endIndex]
	print(str(tokens))
	# Handling nearby words
	for token in tokens:
		if token != target:
			if token in wordToSensesDict:
				senses = wordToSensesDict[token]
				for senseId in senses:
					words = idToWordsDict[senseId][1]      # Words in the synset
					for word in words:
						if word not in bigBag:
							bigBag.append(word)


	#print(bigBag)
	#print(sensesOfTargetToBag)
	#scoresDict = calculate_scores(sensesOfTargetToBag, bigBag, scoresDict, 1)
	# BUNU COMMENT OUT ETTİM TEKRAR BAKMALIYIM
	
	level = 0 # number of iterations
	while level < 3:
		level = level + 1
		#sensesOfTargetToBag'e her sense'in hypernym'inin kelimelerini ekliyorum
		for senseId in sensesOfTargetToBag:
			hypernymId = getHypernym(senseId)
			if hypernymId != "":
				additionalWords = getWords(hypernymId) 
				sensesOfTargetToBag[senseId] = sensesOfTargetToBag[senseId] + additionalWords
				setHypernym(senseId, getHypernym(hypernymId))
		#bigBag'e içindeki her kelimenin her sense'inin hypernym'inin kelimesini ekliyorum
		for word in bigBag:  # Burda optimizasyon yapılabilir
			# BURDAKİ WORD'LERİN DE ZEMBEREK'E SOKULMASI LAZIM (YANİ SADECE INPUT CÜMLE YETMEZ)
			# ÇÜNKÜ BURAYA TANIMLARDAN KELİMELER GELİYOR
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
	return max(scoresDict, key=lambda key: scoresDict[key])
	

	winnerId = ""
	winnerScore = -1
	for senseId in scoresDict:
		if scoresDict[senseId] > winnerScore:
			winnerScore = scoresDict[senseId]
			winnerId = senseId

	print("Definition of the winner :" + str(getDefinitionWords(winnerId)))
	print("Synset of the winner: " + str(getWords(winnerId)))
	#print("Hypernym of the winner is : " + idToWordsDict[winnerId][0])
	#print("The winner is: " + str(getWords(idToWordsDict[winnerId][0])))
	# Wordnette tanım yoksa ne bastıracağız ekrana? Belki hypernym?
	# Hypernym'i yukarda bozuyorum level çıkarken

# SENTENCE VE TARGET ZEMBEREĞE SOKULMALI
sentence = "fkdjhfj yaz zaaaaxd bahar".lower()
# "Optik fare" denedim patladı çünkü wordnette optik kelimesi yok
tokens = sentence.split()

# WORDNETE BUNU HEM YAZ HEM YAZMAK OLARAK SOKMAMIZ LAZIM
target = "yaz"  
if target not in wordToSensesDict:
	print("Bu kelime Wordnet'te bulunmamaktadır. Lütfen başka bir kelime deneyiniz.")
else:
	disambiguate(tokens, target)


########### EVALUATION ##################
correctSensesDict = {}     # BUNU AMELE GİBİ DOLDURCAZ VİKİPEDİDEN
tokensEvaluated = len(tokens)
correctGuesses = 0

for token in tokens:
	if token not in wordToSensesDict:   # it means there is no such word in wordnet
		tokensEvaluated = tokensEvaluated - 1
		continue
	else:
		number_of_senses = len(getSenses(token))
		if number_of_senses == 1:       # no need to evaluate
			tokensEvaluated = tokensEvaluated - 1
			continue
		else:
			target = token
			proposed_sense = disambiguate(target,tokens)
			if proposed_sense == correctSensesDict[token]:
				correctGuesses = correctGuesses + 1

print(str(correctGuesses) + " correct senses out of " + tokensEvaluated + " words.")
#############################################

# Oğuzhan's todo list:
# 1. Zemberek gömülecek 
#(Zemberek hem input cümlesini halletmeli hem de level çıkarken tanımları falan ekliyoruz, o tanımları halletmeli)
# 2. Stopwordler kaldırılacak 
# 3. Input cümlesindeki punctuation'lar kaldırılacak
# 4. Vikipediden yardırcaz


# Kendime notlar

# Daha fazla if check gerekebilir kontrol etmeliyim
# Nearby word'lere weight









	