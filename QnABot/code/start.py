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
        return docs
    except FileNotFoundError:
        exit()
        
def get_file_content_as_string(file):
    return open('../dataset/'+file, 'r', encoding = 'utf-8').read()

# def processContextWithNewParams(docs, param1, param2, param3, param4):
#     for i in docs:
#         docs[name]['contextobj'] = PC(docs[name]['data'])
#     return docs

docs = loadData()
instead_use_lemmanization = False
possible_db_name = os.listdir('../dataset')
stemmer = "No Stemmer"
lemm_stemm_flag = "No"
specific = False
ut = UT()
yesnoDict = {
             "Yes" : True,
             "No"  : False
            }

st.sidebar.title("Configure Your Bot")
lemm_or_stemm = st.sidebar.selectbox("Stemming or Lemmanization of the word", ["None","Stemming", "Lemmanization"])

if lemm_or_stemm == "Lemmanization":
    title_header = "Choose lemmanization option"
    lemm_stemm_flag = st.sidebar.selectbox(title_header, ["Yes", "No"])
else if lemm_or_stemm == "Stemming":
    title_header = "Choose Stemming option"
    lemm_stemm_flag = st.sidebar.selectbox(title_header, ["Yes", "No"])



if lemm_or_stemm == "Stemming" and lemm_stemm_flag == "Yes":
    stemmer = st.sidebar.selectbox("Choose which stemmer", ["PorterStemmer", "SnowBallStemmer"])
    
removestopword_flag = st.sidebar.selectbox("Remove Stopwords", ["Yes", "No"])
use_synonyms_flag = st.sidebar.selectbox("Use Synonyms", ["Yes", "No"])

similarity_func = st.sidebar.selectbox("Which Sentence level similarity function to use", ["SkLearn", "Gensim", "User Made"])
show_file = st.sidebar.checkbox("Show Selected File")

st.title("Hi There !!")
st.header("I am a Q and A bot !!!")
st.markdown("I can answer many types of question belonging to any of the category "
                "shown in the List below ")

file_selected = st.selectbox("Choose the Data from which you want to ask questions from", possible_db_name)
if show_file:
    st.markdown(get_file_content_as_string(file_selected))

placeholder = "Enter your Query here ..."
user_query = st.text_input("User Input", placeholder)

# docs = processContextWithNewParams(docs, removestopword_flag, use_synonyms_flag, lemm_or_stemm, lemm_stemm_flag, stemmer, similarity_func)
specificData = PC(docs[file_selected]['data'], yesnoDict[removestopword_flag], lemm_or_stemm, yesnoDict[lemm_stemm_flag], stemmer, similarity_func)

greetPattern = re.compile("^\ *((hey)|(hi+)|((good\ )?morning|evening|afternoon)|(he((llo)|y+)))\ *$",re.I)
exitPattern = re.compile("^\ *((bye*\ ?)|(see (you|ya) later))\ *$",re.I)

if user_query != placeholder:
    
    response = ""
    if not len(user_query) > 5:
        response = "Please enter valid question."
    elif greetPattern.match(user_query):
        response = "Hello!"
    elif exitPattern.match(user_query):
        response = "See ya next time!"
        print("Bot-> ", response)
        break
    else:
        if specific:
            objPQ = PQ(user_query, yesnoDict[removestopword_flag], yesnoDict[use_synonyms_flag])
            response = specificData.getResults(objPQ)

            # closestvector, obj = ut.GetClosestContextFile(1)
    st.write(response)
    
