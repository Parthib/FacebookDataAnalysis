 #!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import re
import datetime
import matplotlib.pyplot as plt
import csv
from collections import defaultdict

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

def getYear(message):
    return datetime.datetime.fromtimestamp(message['timestamp_ms']/1000).strftime('%Y')

def getMonth(message):
    return datetime.datetime.fromtimestamp(message['timestamp_ms']/1000).strftime('%B')

def monthToInt(month):

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    monthToInt = defaultdict(int, {month: idx + 1 for idx, month in enumerate(months)})
    return(monthToInt[month])

def monthYearToComparable(text):
    monthYear = text.split(" ")
    month = monthYear[0]
    year = monthYear[1]

    return(int(year)*100 + monthToInt(month))

def generateCSV(wordFreq, n):

    monthYears = sorted(wordFreq.keys(), key=lambda kv: monthYearToComparable(kv))

#    sum = 0

    for i in range(1, len(monthYears)):
        for word in wordFreq[monthYears[i - 1]]:
            wordFreq[monthYears[i]][word] = wordFreq[monthYears[i-1]][word] + wordFreq[monthYears[i]][word]

#    for word in wordFreq["November 2019"]:
#        sum = sum + wordFreq["November 2019"][word]

    words = wordFreq[monthYears[len(monthYears) - 1]].keys()

    with open('facebookWords.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Word"] + monthYears)

        for word in words:
            row = [word]
            for monthYear in monthYears:
                row.append(str(wordFreq[monthYear][word]))
            writer.writerow(row)





def graphGramFreq(wordFreq, name, n, month=False):
    for year in wordFreq:
        wordFreq[year] = sorted(wordFreq[year].items(), key=lambda kv: kv[1], reverse=True)

    years = None

    if (not month):
        years = sorted(wordFreq)
    else:
        years = sorted(wordFreq.keys(), key=lambda kv: monthYearToComparable(kv))

    plt.figure(figsize=(15.0, 10*len(years)))

    for year in years:
        words = [tuple[0] for tuple in wordFreq[year]]
        maxVal = min(20, len(words) - 1)
        words = words[:20]
        values = [tuple[1] for tuple in wordFreq[year]]
        totalWords = float(sum(values))
        values = values[:20]
        values = [100 * x / totalWords for x in values]

        plt.subplot(len(years), 1, years.index(year) + 1)
        grams = []
        for i in range(0,maxVal):
            gram=""
            for element in words[i]:
                gram = gram + element + " "
            grams.append(gram)
            plt.bar(i, values[i], tick_label=gram)

        plt.ylabel("Percent of All Words")
        plt.xticks(range(0,maxVal), grams)
        plt.xticks(rotation=45)
        plt.title(name + "'s Word Frequency in " + str(year) + " out of " + str(int(totalWords)) + " " + str(n) + "-Grams")

    plt.xlabel("Word")
    plt.savefig('words.png', bbox_inches='tight')

def getGramWordFrequency(name, n, includeMonth = False, excluded = []):
#    total = 0
    removed_words = {word.lower() for word in stopwords.words('english')}
    pattern = re.compile("^[a-zA-z]{2,}$")
    autoMessages = ["left the group", "joined the video chat", "joined the call", "started a video chat", "The video chat ended.", "You missed a video chat with",
    "You missed a call from", "missed your call.", "missed your video chat.", "set the emoji to", "set the nickname for", "set their own nickname to", "named the group", "from the group", "in the poll",
    "as a group admin.", "You changed the listing title to", "changed the listing description.", "named the group", "changed the group photo.", "changed the chat colors.", "points playing", "to the group", "on Messenger.", "played back, now it is your turn!", "turned on member approval and will review requests to join the group.", "turned off member approval. Anyone with the link can join the group.", "made their move:"]
    skipped = 0
    wordFreq = defaultdict(lambda: defaultdict(int))

    for dirname, dirnames, filenames in os.walk('.'):
        for filename in filenames:

            filePath = os.path.join(dirname, filename)

            if (".json" in filePath):

                with open(filePath, 'r') as file:
                    parsedJson = json.load(file)
                    for message in parsedJson['messages']:
                        if (name in message['sender_name']):
                            try:
                                if any(phrase in message['content'] for phrase in autoMessages):
                                    skipped = skipped + 1
                    #            elif "like" in message['content'].lower():
                    #                print(message['content'])
                                else:
                                    year = getYear(message)
                                    month = getMonth(message)
                                    text = message['content']
                                    text = text.lower()
                                #    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
                                    words = [token for token in text.split(" ") if token != ""]
                                    ngramList = list(ngrams(words, n))

                                    for gram in ngramList:
                                        if (n == 1):
                                            if not (any((word in removed_words for word in gram)) or (gram[0] in excluded)) and all(pattern.match(word) for word in gram):
                                                if not includeMonth:
                                                    wordFreq[year][gram] = wordFreq[year][gram] + 1
                                                else:
                                                    wordFreq[month + " " + year][" ".join(gram)] = wordFreq[month + " " + year][" ".join(gram)] + 1
                                        else:
                                            if not any((word in removed_words for word in gram) or any((word in excluded for word in gram))) and all(pattern.match(word) for word in gram):
                                                if not includeMonth:
                                                    wordFreq[year][gram] = wordFreq[year][gram] + 1
                                    #                total = total + 1
                                                else:
                                                    wordFreq[month + " " + year][" ".join(gram)] = wordFreq[month + " " + year][" ".join(gram)] + 1
                            except KeyError:
                                continue
    print ("skipped " + str(skipped))
#    print(total)
    return wordFreq

def runGramAnalysis(name, n):
    gramFreq = getGramWordFrequency(name, n)
    graphGramFreq(gramFreq, name, n)

def runGenerateCSV(name, n, excluded = []):
    gramFreq = getGramWordFrequency(name, n, True, excluded)
    generateCSV(gramFreq, n)

runGramAnalysis('Parthib Samadder', 2)
#runGenerateCSV('Parthib Samadder', 1, {"excludedwordshere"})
