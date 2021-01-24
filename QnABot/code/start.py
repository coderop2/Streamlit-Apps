import re, sys, os
import streamlit as st 
from ProcessContext import ProcessContext as PC
from ProcessQuestion import ProcessQuestion as PQ
from Utilities import Utilities as UT

@st.cache(suppress_st_warning=True, persist=True, allow_output_mutation=True)
def loadData():
    docs = {}
    try:
        for name in possible_db_name:
            docs[name] = {}
            docs[name]['data'] = []

            with open('../dataset/'+name,"r", encoding='utf-8') as f:
                for line in f.readlines():
                    if(len(line.strip()) > 0):
                        docs[name]['data'].append(line.strip())

            docs[name]['contextobj'] = PC(docs[name]['data'])
        return docs
    except FileNotFoundError:
        print("Bot> Oops! Currently i dont have \"" + databasename + "\""+" in my database set")
        exit()

docs = loadData()
instead_use_lemmanization = False
possible_db_name = os.listdir('../dataset')
stemmer = "No Stemmer"
yesnoDict = {
             "Yes" : True,
             "No"  : False
            }

st.sidebar.title("Configure Your Bot")
lemm_or_stemm = st.sidebar.selectbox("Stemming or Lemmanization of the word", ["Stemming", "Lemmanization"])

if lemm_or_stemm == "Lemmanization":
    title_header = "Choose lemmanization option"
else:
    title_header = "Choose Stemming option"

lemm_stemm_flag = st.sidebar.selectbox(title_header, ["Yes", "No"])

if lemm_or_stemm == "Stemming" and lemm_stemm_flag == "Yes":
    stemmer = st.sidebar.selectbox("Choose which stemmer", ["PorterStemmer", "SnowBallStemmer"])
    
removestopword_flag = st.sidebar.selectbox("Remove Stopwords", ["Yes", "No"])
use_synonyms_flag = st.sidebar.selectbox("Use Synonyms", ["Yes", "No"])

similarity_func = st.sidebar.selectbox("Which Sentence level similarity function to use", ["SkLearn", "Gensim", "User Made"])
show_file = st.sidebar.checkbox("Show Selected File")


st.title("Hi There !! I am a Q and A bot !!!")
st.markdown("I can answer many types of question belonging to any of the category "
                "shown in the List below ")

st.selectbox("Choose the Data from which you want to ask questions from", possible_db_name)


specific = False
ut = UT()



while True:
    response = ""
    userInp = input("You-> ")
    if not len(userInp) > 5:
        response = "Please enter valid question."
    elif greetPattern.match(userInp):
        response = "Hello!"
    elif exitPattern.match(userInp):
        response = "See ya next time!"
        print("Bot-> ", response)
        break
    else:
        if specific:
            objPQ = PQ(userInp)
            # print(len(specificData.paraInfo))
            response = specificData.getResults(objPQ)
        else:
            closestvector, obj = ut.GetClosestContextFile(1)
            if closestvector == 0:
                response = "Please provide a better question with more context"
            else:
                response = "Going wide"
    print("Bot-> ", response)
    
