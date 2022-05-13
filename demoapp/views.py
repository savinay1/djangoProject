import os

from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .forms import Form
from urllib import request as rq
import pandas as pd
import simplejson
from django.conf import settings
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
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
pos_dict = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}


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
    return vs


def vader_analysis(vs):
    if vs['neg'] > 0.15:
        return 'Negative'
    elif vs['pos'] > 0.0:
        return 'Positive'
    else:
        return 'Neutral'


def results(request):
    hi(request)
    context = {}
    # context["Results"] = vader_counts.to_dict()
    # return render(request,'demoapp/results.html',context)
    labels = []
    sizes = []
    context["Movie"] = movie
    context["Filter"] = filterd
    if len(vader_counts) == 0:
        context["Results"] = "No Results found .Please try another Movie"
    colors = {"Positive":"#7AC154", "Negative":"#FF2D14", "Neutral":"#FBB940"}
    for x, y in vader_counts.items():
        labels.append(x)
        sizes.append(y)
    fig = plt.figure()
    # fig.patch.set_facecolor((139/255,48/255,40/255,0.97/255))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, colors=[colors[key] for key in labels])

    plt.axis('equal')
    plt.savefig(settings.STATIC_ROOT + settings.STATIC_URL + 'sentiments.png')
    return render(request, 'demoapp/results.html', context)


def hi(request):
    # return HttpResponse('<h1>Homepage</h1>')
    if request.method == 'POST':
        form = Form(request.POST)
        filterkey={"Post_Text":"Post Text","Comments":"Comments","Replies":"Replies"}
        if form.is_valid():
            global movie
            movie = form.cleaned_data['Enter_movie_title']
            global filterd
            filterd = filterkey[form.cleaned_data['Filter']]
            filter = form.cleaned_data['Filter']
            rows = form.cleaned_data['Results']
            text = movie.replace(" ", "%20")

            connection = rq.urlopen(
                'http://localhost:8983/solr/movies/query?q=' + filter + ":" + text + "&rows=" + str(rows))
            response = simplejson.load(connection)
            docs = response['response']['docs']
            global vader_counts
            if len(docs) == 0:
                vader_counts = {}
            comments = []
            check = "Comments"
            if filter == "Post_Text":
                check = 'Comments'
            elif filter == "Comments":
                check = 'Post_Text'
            elif filter == "Replies":
                check = "Comments"
            for response in docs:
                try:
                    comments.append(response[check])
                except:
                    comments.append(response['Comments'])

            df = pd.DataFrame(comments, columns=['Comments'])
            # Cleaning the text in the review column
            df['Cleaned Reviews'] = df['Comments'].apply(clean)
            df['POS tagged'] = df['Cleaned Reviews'].apply(token_stop_pos)
            df['Lemma'] = df['POS tagged'].apply(lemmatize)
            fin_data = pd.DataFrame(df[['Comments', 'Lemma']])

            fin_data['Vader Sentiment'] = fin_data['Lemma'].apply(vadersentimentanalysis)
            fin_data['Vader Analysis'] = fin_data['Vader Sentiment'].apply(vader_analysis)
            vader_counts = fin_data['Vader Analysis'].value_counts()

    form = Form()
    return render(request, 'demoapp/hi.html', {'form': form})
