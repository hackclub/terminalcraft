from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy
with open('json/skinlist2.json', 'r', encoding='utf-8') as f:
    # The ####### is added to the start of the list as a false value
    # If the cosine search can not find any matches it will just return
    # the first item as the match, meaning that when we get this we can
    # just ignore the response
        skinlist = ["#######"] + json.loads(f.read())

def generate_matrix():
    vectoriser = TfidfVectorizer()

    tfidf_matrix = vectoriser.fit_transform(raw_documents=skinlist)
    return tfidf_matrix, vectoriser

def search_matrix(tfidf_matrix, vectoriser, search_item):
    print(search_item)
    # search_item = vectoriser.transform(['crossfade'])
    # similarities = cosine_similarity(tfidf_matrix, search_item)

    results = []

    search_item = vectoriser.transform([str(search_item)])
    similarities = cosine_similarity(tfidf_matrix, search_item) 

    
    for _ in range(4):
        most_similar_index = numpy.argmax(similarities)
        # print(most_similar_index)
        search_result = skinlist[most_similar_index]
        print(search_result)
        if search_result == "#######":
            break
        results.append(search_result)

        # Delete the item we just saw from the similarities list
        similarities = numpy.delete(similarities, most_similar_index)
    
    print(search_result)
    return results