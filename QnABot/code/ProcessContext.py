import math, nltk
import numpy as np
from Utilities import Utilities
from nltk.corpus import stopwords
from nltk import pos_tag,ne_chunk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, SnowballStemmer
from nltk.tree import Tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class ProcessContext:
    def __init__(self, contextParas, remove_stopwords = True):
        self.utl = Utilities()
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        self.remove_stopwords = remove_stopwords
        self.stopwords = stopwords.words('english')
        self.stemmer = PorterStemmer()
        self.numOfParas = len(contextParas)
        self.paraInfo, self.vocab, self.processed_vocab = self.processParas(contextParas)
        del contextParas
    
    def processParas(self, paras):
        idf = {}
        docs = {}
        vocab = set()
        processed_vocab = set()
        
        for index in range(self.numOfParas):
            
            docs[index] = {}
            docs[index]['para'] = paras[index]
            docs[index]['paraWords'] = word_tokenize(paras[index])
            vocab.update(docs[index]['paraWords'])
            docs[index]['paraSentences'] = self.sent_tokenizer.tokenize(paras[index])
            wf, processed_sentences, pv = self.processSentences(docs[index]['paraSentences'])
            docs[index]['paraWF'] = wf
            docs[index]['paraProcessedSentences'] = processed_sentences
            docs[index]['paraPV'] = pv
            processed_vocab.update(pv)
            
            for word in pv:
                if idf.get(word,0) == 0:
                    idf[word] = 1
                else:
                    idf[word] += 1
        
        self.contextIDF = {}
        for word in idf:
            # Laplace smoothing
            self.contextIDF[word] = math.log((self.numOfParas+1)/idf[word])
            
        for index in range(self.numOfParas):
            docs[index]['paraVector'] = self.utl.ComputeVector(docs[index]['paraWF'], self.contextIDF)
            
        return docs, vocab, processed_vocab
    
    def processSentences(self, sentences):
        wf = {}
        processed_sentences = []
        processed_vocab = set()
        for sent in sentences:
            processed_sentence = []
            words = word_tokenize(sent)
            wf, processed_sentence = self.utl.processText(words, self.remove_stopwords, self.stemmer, wf)
            # for word in words:
            #     if not self.remove_stopwords:
            #         continue
            #     else:
            #         if word in self.stopwords:
            #             continue
            #     word = self.stemmer.stem(word)
            #     if wf.get(word, 0) == 0:
            #         wf[word] = 1
            #     else:
            #         wf[word] += 1
            #     processed_sentence.append(word)
            processed_vocab.update(processed_sentence)
            processed_sentences.append(" ".join(processed_sentence))
        return wf, processed_sentence, processed_vocab
    
    def getResults(self, PQ):
        PQ.questionDoc['questionVector'] = self.utl.ComputeVector(PQ.questionDoc['questionWF'], self.contextIDF)
        # print(PQ.questionDoc['questionVector'])
        simParas = self.getSimilarParas(PQ.questionDoc)
        allSentences = []
        if simParas != None:
            for i in simParas:
                allSentences.extend(sent_tokenize(i[0]))
                
        if len(allSentences) == 0:
            return "Oops! Unable to find answer"
        
        relevantSentencesWithScores = self.getMostRelevantSentences(allSentences,PQ,1)
        sentences = [sentencewithscore[0] for sentencewithscore in relevantSentencesWithScores]
        # print(relevantSentences)
        
        answerType = PQ.questionDoc['Atype']
        print(answerType)
        answer = " ".join(sentences[:2])
        
        if answerType in ["GPE", "PERSON", "ORGANIZATION"]:
            entities = self.utl.getNamedEntityChunks(sentences)
            for entity in entities:
                if entity[0] == answerType:
                    answer = entity[1]
                    # print(entities)
                    ansTokens = [self.stemmer.stem(word) for word in word_tokenize(answer)]
                    if [(i in PQ.questionDoc['processedQuestion']) for i in ansTokens].count(True) >= 1:
                        continue
                    break
        elif answerType == "DEFINITION":
            answer = " ".join(sentences[:4])
            
        elif answerType == "DATE":
            dates = self.utl.getDates(" ".join(sentences))
            # print(dates)
            if len(dates) > 0:
                answer = dates[0]
            
        elif answerType == "QUANTITY":
            answer = "Work In Progress"
        elif answerType == "YESNO":
            answer = "Work In Progress"
        else:
            if len(sentences) > 5:
                answer = " ".join(sentences[:5])
        
        return answer
        
    def getSimilarParas(self, questionVector):
        if questionVector['questionVector'] == 0:
            return None
        
        qv = questionVector['questionWF']
        
        rankedParas = []
        for index in range(self.numOfParas):
            dotProduct = 0
            paraInfo = self.paraInfo[index]
            for word in qv.keys():
                if word in paraInfo['paraWF']:
                    dotProduct += qv[word]*paraInfo['paraWF'][word]*self.contextIDF[word]*self.contextIDF[word]
        
            sim = dotProduct / (paraInfo['paraVector'] * questionVector['questionVector'])
            rankedParas.append((paraInfo['para'], sim))
        
        return sorted(rankedParas, key = lambda x: (x[1], x[0]), reverse = True)[:4]
    
    # Thanks to the project made by vaibhav for the below Code 
    def getMostRelevantSentences(self, sentences, pQ, nGram=3):
        relevantSentences = []
        for sent in sentences:
            sim = 0
            if(len(word_tokenize(pQ.question))>nGram+1):
                sim = self.sim_ngram_sentence(pQ.question,sent,nGram)
            else:
                sim = self.sim_sentence(pQ.qVector, sent)
            relevantSentences.append((sent,sim))
        
        return sorted(relevantSentences,key=lambda tup:(tup[1],tup[0]),reverse=True)
    
    def sim_ngram_sentence(self, question, sentence,nGram):
        #considering stop words as well
        ps = PorterStemmer()
        getToken = lambda question:[ ps.stem(w.lower()) for w in word_tokenize(question) ]
        getNGram = lambda tokens,n:[ " ".join([tokens[index+i] for i in range(0,n)]) for index in range(0,len(tokens)-n+1)]
        qToken = getToken(question)
        sToken = getToken(sentence)

        if(len(qToken) > nGram):
            q3gram = set(getNGram(qToken,nGram))
            s3gram = set(getNGram(sToken,nGram))
            if(len(s3gram) < nGram):
                return 0
            qLen = len(q3gram)
            sLen = len(s3gram)
            sim = len(q3gram.intersection(s3gram)) / len(q3gram.union(s3gram))
            return sim
        else:
            return 0
     
    def sim_sentence(self, queryVector, sentence):
        sentToken = word_tokenize(sentence)
        ps = PorterStemmer()
        for index in range(0,len(sentToken)):
            sentToken[index] = ps.stem(sentToken[index])
        sim = 0
        for word in queryVector.keys():
            w = ps.stem(word)
            if w in sentToken:
                sim += 1
        return sim/(len(sentToken)*len(queryVector.keys()))