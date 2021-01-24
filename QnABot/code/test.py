import streamlit as st
import os

possible_db_name = os.listdir('../dataset')
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
similarity_func = st.sidebar.selectbox("Which Sentence level similarity function to use", ["SKlearn", "Gensim", "User Made"])
show_file = st.sidebar.checkbox("Show Selected File")
st.write(show_file)
st.title("Consolidated DashBoard since the OutBreak")
st.markdown("This application is a Streamlit dashboard that can be used "
                "to analyze the spread of COVID-19 💥🚗")

st.selectbox("Choose the Data from which you want to ask questions from", possible_db_name)


value = "default value"
# if st.button('reset textarea'):
#     value = "new value"

text = st.text_area("here's my text", value)
st.write(text)