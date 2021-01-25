import math, nltk
import numpy as np
from Utilities import Utilities
from nltk.corpus import stopwords
from nltk import pos_tag,ne_chunk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer
from nltk.tree import Tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProcessContext:
    def __init__(self, contextParas, remove_stopwords, lemm_or_stemm, use_stemmer_lemm, which_stemmer, sim_func, sent_t):
        self.utl = Utilities()
        self.sent_tokenizer = sent_tokenize
        self.sim_func = sim_func
        if sent_t == "Punkt":
            self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle').tokenize
        self.remove_stopwords = remove_stopwords
        self.stopwords = stopwords.words('english')
        self.stemmer = lambda x: x.lower()
        if lemm_or_stemm == "Stemming" and which_stemmer == "PorterStemmer" and use_stemmer_lemm:
            self.stemmer = PorterStemmer().stem
        elif lemm_or_stemm == "Stemming" and which_stemmer == "SnowBallStemmer" and use_stemmer_lemm:
            self.stemmer = SnowballStemmer().stem
        elif lemm_or_stemm == "Lemmanization" and use_stemmer_lemm:
            self.stemmer = WordNetLemmatizer().lemmatize
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
            docs[index]['paraSentences'] = self.sent_tokenizer(paras[index])
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
        if self.sim_func in ["SkLearn", "Gensim"]:
            sentencesWithSimScores = set()
            sentencesWithSimScores.update(self.getMostSimilarSentences(PQ.question, allSentences))
            while len(sentencesWithSimScores) < 5:
                sentencesWithSimScores.update(self.getMostSimilarSentences(sentencesWithSimScores[0], allSentences, True))
            relevantSentencesWithScores = list(sentencesWithSimScores)
                
        sentences = [sentencewithscore[0] for sentencewithscore in relevantSentencesWithScores]
        # print(relevantSentences)
        
        answerType = PQ.questionDoc['Atype']
        # print(answerType)
        answer = " ".join(sentences[:2])
        
        if answerType in ["GPE", "PERSON", "ORGANIZATION"]:
            entities = self.utl.getNamedEntityChunks(sentences)
            for entity in entities:
                if entity[0] == answerType:
                    answer = entity[1]
                    # print(entities)
                    ansTokens = [self.stemmer(word) for word in word_tokenize(answer)]
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
    
    def getMostSimilarSentences(self, question, sentences, second_time = False):
        documents = [question]
        documents.extend(sentences)
        df = self.getsimilarityDF(documents)
        res = cosine_similarity(df, df)
        z = res[0,:]
        y = []
        for idx,i in enumerate(z):
            if i > 0:
                y.append((documents[idx], i))
        arr = sorted(y, key =lambda x: (x[1], x[0]), reverse=True)
        return arr[2:] if second_time else arr[1:]
    
    def getsimilarityDF(self, documents):
        count_vectorizer = CountVectorizer(stop_words='english')
        count_vectorizer = CountVectorizer()
        sparse_matrix = count_vectorizer.fit_transform(documents)
        doc_term_matrix = sparse_matrix.todense()
        return doc_term_matrix

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