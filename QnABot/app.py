## Entry Point for the application 

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
count_vectorizer = CountVectorizer(stop_words='english')

while True:
    print("Person1 -> ", end=" ")
    inp = input()
    documents = ["exit bye ta-ta", inp]
    sparse_matrix = count_vectorizer.fit_transform(documents)
    # print("Similarity between input ans exit is:", cosine_similarity(sparse_matrix))
    if cosine_similarity(sparse_matrix)[0][1] > 0.4:
        break
    ans = "This is the answer"
    print("Person2 -> ", ans)