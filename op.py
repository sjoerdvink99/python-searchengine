# importeer libraries
import re
import glob
import math

# vind txt bestanden in de directory
bestanden = glob.glob("bestanden/*.txt")

# zet veel gebruikte woorden in lijst
veelGebruikteWoorden = list(open("dutch.txt", "r"))
veelGebruikteWoorden = map(lambda s: s.strip(), veelGebruikteWoorden)

# maak dictionary met teller
wordcounts = {}

# loop door elk bestand en voeg woorden toe aan de wordcounts dictionary
for bestand in bestanden:
    with open(bestand, 'r') as f:
        text = f.read()
        woorden = text.split()
        leestekens = ".`(),-':;_"
        woordfreq = {}
        for term in woorden:
            woord = term.strip(leestekens)
            woord = woord.lower()
            if woord in veelGebruikteWoorden:
                pass
            elif woord in woordfreq:
                woordfreq[woord] += 1
            else:
                woordfreq[woord] = 1
        wordcounts[bestand] = woordfreq

# lege set voor de woorden
unieke_woorden = set()

# unieke woorden toevoegen aan set
for documenten, dictionary in wordcounts.items():
    for key, waarde in dictionary.items():
        unieke_woorden.add(key)

# woordfrequentie matrix maken en document-titels toevoegen
frequentieMatrix = [[''] + list(wordcounts.keys())]

# waardes van unieke woorden toevoegen per document
for term in set(doc for freq in wordcounts.values() for doc in freq.keys()):
    frequentieMatrix.append([term] + [wordcounts[k].get(term, 0) for k in frequentieMatrix[0][1:]])
    
# sorteer matrix
frequentieMatrix = sorted(frequentieMatrix, key=lambda t: t[0])

# maak een lijst voor de df
df_lijst = []
teller = 0

# tel het aantal bestanden
for bestand in bestanden:
    teller += 1

# tel de df per term
for term in frequentieMatrix:
    df = 0
    for i in term[1:]:
        if i == 0:
            continue
        else:
            df += 1
    df_lijst.append(df)

# verwijder eerste rij
df_lijst.remove(df_lijst[0])

# bereken idf per term
df_lijst = [teller / term for term in df_lijst]
idf_lijst = [math.log2(term) for term in df_lijst]

# verwijder strings voor de verdere berekening
documentenRij = frequentieMatrix[0]
termen = []

for rij in frequentieMatrix:
    termen.append(rij[0])
    rij.remove(rij[0])

frequentieMatrix.remove(frequentieMatrix[0])

# term weight matrix maken
twMatrix = [[i * f for i in g] for g, f in zip(frequentieMatrix, idf_lijst)]
twMatrix.insert(0, documentenRij)
twMatrix = [[termen[i]] + twMatrix[i] for i in range(len(termen))]

# bereken kwadraat en de sum-weigths
rijen = [rij[1:] for rij in twMatrix[1:]]
cijfersPerDoc = zip(*rijen)
kwadraat = [sum(cijfer ** 2 for cijfer in docs) for docs in cijfersPerDoc]

# vector-lijst en vector-matrix maken
vectorLijst = []
vectorMatrix = []

# doc-titels toevoegen
vectorMatrix.append(twMatrix[0])

# bereken vierkantswortel en voeg het resultaat toe aan de vector lijst
for getal in kwadraat:
    vector = math.sqrt(getal)
    vectorLijst.append(vector)

# voeg de lijst met vectoren toe aan de matrix
vectorLijst.insert(0, 0.0)
vectorMatrix.append(vectorLijst)

# functie cosinus similariteit berekenen 
def zoeken(queries):
    count = 0

    # tel de queries
    for query in queries:
        count += 1

    # maak matrix en voeg titels van docs toe
    accumulateMatrix = []
    accumulateMatrix.append(twMatrix[0])
    
    termWaarde = []

    rows = [row[0:] for row in twMatrix[0]]
    columns = zip(*rows)
    
    # kijken of de query bestaat
    for row in twMatrix:
        for term in row:
            for query in queries:
                if query in row[0]:
                    if term != 0.0:
                        termWaarde.append(term)
                    else:
                        termWaarde.append(0.0)

    # voeg data toe aan matrix
    accumulateMatrix.append(termWaarde)
    
    # bereken de cosinus similariteit
    rowAcc = [row[1:] for row in accumulateMatrix[1:]]
    rowAcc = rowAcc[0]
    rowVec = [row[1:] for row in vectorMatrix[1:]]
    rowVec = rowVec[0]

    vectorLengte = [(vector * math.sqrt(count)) for vector in rowVec]
    cosinus = [innerProduct / vecLengte for innerProduct, vecLengte in zip(rowAcc, vectorLengte)]
    
    cosinus.insert(0, 0.0)
    
    # maak een matrix waarbij documenten niet gerangschikt zijn
    ongerangschikteMatrix = []
    
    # for loop om titels en data toe te voegen aan ongerangschikte matrix
    for i in range(len(twMatrix[0])):
        lijst = []
        lijst.append(twMatrix[0][i])
        lijst.append(cosinus[i])
        if lijst[1] != 0.0: # verwijder artikelen zonder cosinus similariteit
            ongerangschikteMatrix.append(lijst)
                
    # rangschik de documenten
    gerangschikteMatrix = sorted(ongerangschikteMatrix, key=lambda score: score[1], reverse=True)
    return gerangschikteMatrix


def artikelInformatie(queries):
    gerangschikteMatrix = zoeken(queries)
    artikelInfo = []  # lege lijst voor artikel informatie
    for artikel in gerangschikteMatrix:  # voeg per artikel de informatie toe aan de lijst
        with open(str(artikel[0]), 'r') as f:
            text = f.read()
            titel = artikel[0].strip('bestanden/').strip('.txt')
            woorden = re.findall(r"\w+|\W+", text)
            if queries[0] in woorden:
                index = woorden.index(queries[0])
                preview = '...' + text[(index-10):(index+200)] + '...'
            else:
                preview = text[0:200] + '...'
            link = re.search('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', text).group()
            artikelInfo.append({'titel': titel, 'preview': preview, 'link': link, 'cosinus': artikel[1]})
    return artikelInfo