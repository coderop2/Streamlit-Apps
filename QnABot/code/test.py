import streamlit as st
import os

@st.cache(show_spinner=True)
def get_file_content_as_string(file):
    return open('../dataset/'+file,'r', encoding='utf-8').read()

# docs = loadData()
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

file_selected = st.selectbox("Choose the Data from which you want to ask questions from", possible_db_name)
if show_file:
    st.markdown(get_file_content_as_string(file_selected))

value = "default value"
# if st.button('reset textarea'):
#     value = "new value"

text = st.text_area("here's my text", value)
st.write(text)