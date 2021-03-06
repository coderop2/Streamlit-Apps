from Utilities import Utilities
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer

class ProcessQuestion:
    def __init__(self, question, remove_stopwords, use_synonyms, lemm_or_stemm, use_stemmer_lemm, which_stemmer):
        self.question = question
        self.utl = Utilities()
        self.stemmer = lambda x: x.lower()
        if lemm_or_stemm == "Stemming" and which_stemmer == "PorterStemmer" and use_stemmer_lemm:
            self.stemmer = PorterStemmer().stem
        elif lemm_or_stemm == "Stemming" and which_stemmer == "SnowBallStemmer" and use_stemmer_lemm:
            self.stemmer = SnowballStemmer(language='english').stem
        elif lemm_or_stemm == "Lemmanization" and use_stemmer_lemm:
            self.stemmer = WordNetLemmatizer().lemmatize
        self.remove_stopwords = remove_stopwords
        self.use_synonyms = use_synonyms
        self.stopwords = stopwords.words('english')
        self.questionTags = ['WP','WDT','WP$','WRB']
        self.tokenizedQuestion = pos_tag(word_tokenize(question))
        self.questionDoc = self.generateQuestionInfo(question)
        # print(self.questionDoc)
        
    def generateQuestionInfo(self, question):
        questionDoc = {}
        questionDoc['processedQuestion'] = self.processQuestion(question)
        questionDoc['Atype'] = self.determineAnswerType(question)
        questionDoc['questionWF'] = self.getFullWF(questionDoc['processedQuestion'])
        return questionDoc
    
    def processQuestion(self, question):
        words = []
        for tag in self.tokenizedQuestion:
            if tag[1] in self.questionTags:
                continue
            else:
                word = self.stemmer(tag[0])
                words.append(tag[0])
                if self.use_synonyms:
                    synonyms = set()
                    syn2 = self.utl.getSynonyms(tag[0])
                    syn = self.utl.getSynonyms(word)
                    if len(syn) > 0:
                        synonyms.update(syn)
                    if len(syn2) > 0:
                        synonyms.update(syn2)
                    if len(synonyms) > 0:
                        words.extend(list(synonyms))
        return words
    
    def determineAnswerType(self, question):
        questionTag = None

        for token in self.tokenizedQuestion:
            if token[1] in self.questionTags:
                questionTag = token[0].lower()
                break
        
        if questionTag is None:
            if len(self.tokenizedQuestion) > 1:
                if self.tokenizedQuestion[0][1].lower() in ['is','are','can','should','has']:
                    return "YESNO"
        if questionTag == "who":
            return "PERSON"
        elif questionTag == "where":
            return "GPE"
        elif questionTag == "when":
            return "DATE"
        elif questionTag == "what":
            sameTokens = self.utl.getSameChunksTogether(self.tokenizedQuestion)

            if len(sameTokens) <= 4:
                if sameTokens[1][1] in ['is','are','was','were'] and sameTokens[2][0] in ["NN","NNS","NNP","NNPS","VBN"]:
                    self.question = " ".join([sameTokens[0][1],sameTokens[2][1],sameTokens[1][1]])
                    return "DEFINITION"

            if self.tokenizedQuestion[1][0] in ['is','are','was','were'] and self.tokenizedQuestion[3][0] in ['name']:
                if "place" in self.question.split(" "):
                    return "GPE"
                return "PERSON"

            # print(self.tokenizedQuestion[0][0],self.tokenizedQuestion[3][0])
            for token in self.tokenizedQuestion:
                if token[0].lower() in ["city","place","country"]:
                    return "GPE"
                elif token[0].lower() in ["company","industry","organization"]:
                    return "ORGANIZATION"
            return "FULL"
        elif questionTag == "how":
            if len(self.tokenizedQuestion)>1:
                if self.tokenizedQuestion[1][0].lower() in ["few","great","little","many","much","tall","wide","big","far"]:
                    return "QUANTITY"
            return "FULL"
        else:
            return "FULL"
        
    def getFullWF(self, precessedQuestion):
        wf = {}
        for token in precessedQuestion:
            if self.remove_stopwords:
                if token in self.stopwords:
                    continue
            token = self.stemmer(token)
            if wf.get(token, 0) == 0:
                wf[token] = 1
            else:
                wf[token] += 1
        return wf
        
    