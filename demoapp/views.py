from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .forms import Form
from urllib import request as rq
import pandas as pd
import simplejson
import matplotlib.pyplot as plt
import re

import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk import pos_tag
nltk.download('stopwords')
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
# POS tagger dictionary
pos_dict = {'J':wordnet.ADJ, 'V':wordnet.VERB, 'N':wordnet.NOUN, 'R':wordnet.ADV}

def token_stop_pos(text):
    tags = pos_tag(word_tokenize(text))
    newlist = []
    for word, tag in tags:
        if word.lower() not in set(stopwords.words('english')):
            newlist.append(tuple([word, pos_dict.get(tag[0])]))
    return newlist


from nltk.stem import WordNetLemmatizer

wordnet_lemmatizer = WordNetLemmatizer()


def lemmatize(pos_data):
    lemma_rew = " "
    for word, pos in pos_data:
        if not pos:
            lemma = word
            lemma_rew = lemma_rew + " " + lemma
        else:
            lemma = wordnet_lemmatizer.lemmatize(word, pos=pos)
            lemma_rew = lemma_rew + " " + lemma
    return lemma_rew




# Define a function to clean the text
def clean(text):
    # Removes all special characters and numericals leaving the alphabets
    text = re.sub('[^A-Za-z]+', ' ', text)
    return text




# function to calculate vader sentiment
def vadersentimentanalysis(review):
    vs = analyzer.polarity_scores(review)
    return vs['compound']

def vader_analysis(compound):
    if compound >= 0.5:
        return 'Positive'
    elif compound <= -0.5 :
        return 'Negative'
    else:
        return 'Neutral'

def results(request):
    hi(request)
    print(vader_counts)
    context = {}
    context["Results"] = vader_counts.to_dict()
    return render(request,'demoapp/results.html',context)

def hi(request):
    #return HttpResponse('<h1>Homepage</h1>')
    if request.method=='POST':
        form = Form(request.POST)

        if form.is_valid():
            movie= form.cleaned_data['Enter_movie_title']
            filter= form.cleaned_data['Filter']
            rows= form.cleaned_data['Results']

            connection = rq.urlopen('http://localhost:8983/solr/movies/query?q='+filter+":"+movie+"&rows="+str(rows))
            response = simplejson.load(connection)
            docs=response['response']['docs']
            comments=[]
            for response in docs:
                comments.append(response['Comments'])
            df=pd.DataFrame(comments,columns =['Comments'])
            # Cleaning the text in the review column
            df['Cleaned Reviews'] = df['Comments'].apply(clean)
            df['POS tagged'] = df['Cleaned Reviews'].apply(token_stop_pos)
            df['Lemma'] = df['POS tagged'].apply(lemmatize)
            fin_data = pd.DataFrame(df[['Comments', 'Lemma']])
            fin_data['Vader Sentiment'] = fin_data['Lemma'].apply(vadersentimentanalysis)
            fin_data['Vader Analysis'] = fin_data['Vader Sentiment'].apply(vader_analysis)
            global vader_counts
            vader_counts=fin_data['Vader Analysis'].value_counts()

    form=Form()
    return render(request,'demoapp/hi.html',{'form':form})