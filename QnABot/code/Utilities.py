import math, re
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag,ne_chunk
from nltk.tokenize import word_tokenize
from nltk.tree import Tree

class Utilities:
    def __init__(self):
        self.stopwords = stopwords.words('english')
        
    def ComputeVector(self, wf, idf):    
        VectorDistance = 0
        for word in wf.keys():
            if word in idf.keys():
                VectorDistance += math.pow(wf[word]*idf[word],2)
        VectorDistance = math.pow(VectorDistance,0.5)
        return VectorDistance
    
    def GetClosestContextFile(self, question):
        closestvector = 0
        obj = 1
        return closestvector, obj
    
    def processText(self, tokenizedWords, remove_stopwords, stemmer, wf):
        processed_sentence = []
        for word in tokenizedWords:
            if remove_stopwords and word in self.stopwords:
                continue
            word = stemmer(word)
            if wf.get(word, 0) == 0:
                wf[word] = 1
            else:
                wf[word] += 1
            processed_sentence.append(word)
        return wf, processed_sentence

    def getSameChunksTogether(self,taggedQuestion):
        chunks = []

        prevTag = taggedQuestion[0][1]
        entity = {"Tag":prevTag,"ListOfChunks":[]}
        
        for token,currTag in taggedQuestion:
            if currTag == prevTag:
                entity["ListOfChunks"].append(token)
            elif prevTag in ["DT","JJ"]:
                entity["Tag"] = prevTag = currTag
                entity["ListOfChunks"].append(token)
            else:
                if len(entity["ListOfChunks"]) != 0:
                    chunks.append((entity["Tag"]," ".join(entity["ListOfChunks"])))
                    entity = {"Tag":currTag,"ListOfChunks":[token]}
                    prevTag = currTag
        if len(entity["ListOfChunks"]) != 0:
            chunks.append((entity["Tag"]," ".join(entity["ListOfChunks"])))
        return chunks
    
    def getNamedEntityChunks(self, sentences):
        chunks = []
        for answer in sentences:
            answerToken = ne_chunk(pos_tag(word_tokenize(answer)))
            entity = {"label":None,"chunk":[]}
            for c_node in answerToken:
                if(type(c_node) == Tree):
                    # print(c_node)
                    if(entity["label"] == None):
                        entity["label"] = c_node.label()
                    entity["chunk"].extend([ token for (token,pos) in c_node.leaves()])
                else:
                    (token,pos) = c_node
                    if pos == "NNP":
                        entity["chunk"].append(token)
                    else:
                        if not len(entity["chunk"]) == 0:
                            chunks.append((entity["label"]," ".join(entity["chunk"])))
                            entity = {"label":None,"chunk":[]}
            if not len(entity["chunk"]) == 0:
                chunks.append((entity["label"]," ".join(entity["chunk"])))
        return chunks
        
    def getSynonyms(self, word):
        synonyms = [word]
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.extend(lemma.name().lower().split("_"))
        return list(set(synonyms))
    
    def getDates(self, text):
        numbers = "(^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)"
        day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        week_day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        month = "(january|february|march|april|may|june|july|august|september|october|november|december)"
        dmy = "(year|day|week|month)"
        rel_day = "(today|yesterday|tomorrow|tonight|tonite)"
        exp1 = "(before|after|earlier|later|ago)"
        exp2 = "(this|next|last)"
        iso = "\d+[./-]\d+[./-]\d+ \d+:\d+:\d+\.\d+"
        any_date = "\d+[./-]\d+[./-]\d+"
        iso_only_date = "((3[01]|[12][0-9]|0?[1-9])[.-/](1[0-2]|0?[1-9])[.-/](?:[0-9]{2})?[0-9]{2})"
        year = "((?<=\s)\d{2,4}|^\d{2,4})"
        year2 = "((?<=\s)\d{4}|^\d{4})"
        regex1 = "((\d+|(" + numbers + "[-\s]?)+) " + dmy + "s? " + exp1 + ")"
        regex2 = f"({exp2} ({dmy}|{week_day}|{month}))"

        regex3= f"(([012]?[0-9]|3[01])(th|st|rd)?[,]? {month} {year})"
        regex4 = f"({month} ([012]?[0-9]|3[01])(th|st|rd)?[,]? {year})"
        regex5= f"((?<=([a-zA-Z]. )){month} {year2})"
        
        # test matchs all the string dd.mm.yyyy or dd/mm/yyyy or dd-mm-yyyy or d.m.yy or you get the gist
        test = "((?:(?:(?:0?[13578]|1[02])(\/|-|\.)31)\1|(?:(?:0?[1,3-9]|1[0-2])(\/|-|\.)(?:29|30)\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:0?2(\/|-|\.)29\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:(?:0?[1-9])|(?:1[0-2]))(\/|-|\.)(?:0?[1-9]|1\d|2[0-8])\4(?:(?:1[6-9]|[2-9]\d)?\d{2}))"
        # test 2 matchs all the string like 30th December 2020 etc.
        test2 = "(((31(?!\ (Feb(ruary)?|Apr(il)?|June?|(Sep(?=\b|t)t?|Nov)(ember)?)))|((30|29)(?!\ Feb(ruary)?))|(29(?=\ Feb(ruary)?\ (((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))))|(0?[1-9])|1\d|2[0-8])\ (Jan(uary)?|Feb(ruary)?|Ma(r(ch)?|y)|Apr(il)?|Ju((ly?)|(ne?))|Aug(ust)?|Oct(ober)?|(Sep(?=\b|t)t?|Nov|Dec)(ember)?)\ ((1[6-9]|[2-9]\d)\d{2}))"
        
        reg_with_space = [(regex3, True), (regex4, True), (regex5, True), (regex2, True), (regex1, True), (iso, True), (any_date, False), (year2, True), (rel_day, True)]
        
        dates = []
        
        for regex, space_flag in reg_with_space:
            compiled_reg = re.compile(regex, re.I)
            found_dates = compiled_reg.findall(text)
            for d in found_dates:
                # print(d, regex)
                if type(d) == tuple:
                    for dd in d:
                        if space_flag:
                            if len(dd.split(" ")) > 1:
                                dates.append(dd)
                        else:
                            if len(dd) > 1:
                                dates.append(dd)
                else:
                    if len(d) > 1:
                        dates.append(d)
        return dates

    