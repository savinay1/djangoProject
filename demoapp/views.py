from django.shortcuts import render
from .forms import Form
from urllib import request as rq
from django.conf import settings

# Libraries  to plot
from matplotlib import pyplot as plt
import matplotlib

matplotlib.use('Agg')
import pandas as pd
import simplejson
import re

# Libraries to do text cleaning
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
from nltk.stem import WordNetLemmatizer

# POS tagger dictionary
pos_dict = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}


# Removes Stop words and tags POS
def token_stop_pos(text):
    tags = pos_tag(word_tokenize(text))
    newlist = []
    for word, tag in tags:
        if word.lower() not in set(stopwords.words('english')):
            newlist.append(tuple([word, pos_dict.get(tag[0])]))
    return newlist


# Lemmatizes the text
def lemmatize(pos_data):
    wordnet_lemmatizer = WordNetLemmatizer()
    lemma_rew = " "
    for word, pos in pos_data:
        if not pos:
            lemma = word
            lemma_rew = lemma_rew + " " + lemma
        else:
            lemma = wordnet_lemmatizer.lemmatize(word, pos=pos)
            lemma_rew = lemma_rew + " " + lemma
    return lemma_rew


# Cleans the text
def clean(text):
    # Removes all special characters and numericals leaving the alphabets
    text = re.sub('[^A-Za-z]+', ' ', text)
    return text


# Calculate individual vader sentiment scores
def vadersentimentanalysis(review):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(review)
    return vs


# Vader sentiment
def vader_sentiment_generator(vs):
    if vs['neg'] > 0.15:
        return 'Negative'
    elif vs['pos'] > 0.0:
        return 'Positive'
    else:
        return 'Neutral'

# Calculate Vader Sentiment scores
def vadersentiment(search_results, filter_field):
    # Construct Dataframe
    df = pd.DataFrame(search_results, columns=[filter_field])

    # Cleaning the text in the review column
    df['Cleaned Reviews'] = df[filter_field].apply(clean)
    df['POS tagged'] = df['Cleaned Reviews'].apply(token_stop_pos)
    df['Lemma'] = df['POS tagged'].apply(lemmatize)
    fin_data = pd.DataFrame(df[[filter_field, 'Lemma']])

    # Calculate Polarity Scores
    fin_data['Vader Sentiment'] = fin_data['Lemma'].apply(vadersentimentanalysis)
    # Calculate Sentiment
    fin_data['Vader Analysis'] = fin_data['Vader Sentiment'].apply(vader_sentiment_generator)

    # Return Sentiment Scores
    return fin_data['Vader Analysis'].value_counts()


# Process User request from landing page
def processrequest(request):
    global movie
    global filter_display
    global vader_counts

    if request.method == 'POST':
        form = Form(request.POST)

        # Process From Contents
        if form.is_valid():

            # Process Form Inputs
            filterkey = {"Post_Text": "Post Text", "Comments": "Comments", "Replies": "Replies"}
            movie = form.cleaned_data['Enter_movie_title']
            filter_display = filterkey[form.cleaned_data['Filter']]
            filter_solr = form.cleaned_data['Filter']
            rows = form.cleaned_data['Results']
            text = movie.replace(" ", "%20")

            # Connection to Apache Solr
            connection = rq.urlopen(
                'http://localhost:8983/solr/movies/query?q=' + filter_solr + ":" + text + "&rows=" + str(rows))
            response = simplejson.load(connection)

            docs = response['response']['docs']

            if len(docs) == 0:
                vader_counts = {}

            # Access Apache Solr documents based on input filter
            search_results = []
            check = "Comments"
            if filter_solr == "Post_Text":
                check = 'Comments'
            elif filter_solr == "Comments":
                check = 'Post_Text'
            elif filter_solr == "Replies":
                check = "Comments"
            for response in docs:
                try:
                    search_results.append(response[check])
                except:
                    search_results.append(response['Comments'])

            # Get Sentiment Scores
            vader_counts = vadersentiment(search_results, check)

    form = Form()
    return render(request, 'demoapp/landing.html', {'form': form})

# Generates context for Results Page
def results(request):

    processrequest(request)

    context = {}
    labels = []
    sizes = []
    context["Movie"] = movie
    context["Filter"] = filter_display

    # If Movie Not Found Edge Case
    if len(vader_counts) == 0:
        context["Results"] = "No Results found . Please try another Movie"
    # Color codes for Pie Chart
    colors = {"Positive": "#7AC154", "Negative": "#FF2D14", "Neutral": "#FBB940"}
    print(vader_counts)
    for x, y in vader_counts.items():
        labels.append(x)
        sizes.append(y)

    # Plot Pie Chart based on Sentiment Scores
    plt.figure()
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, colors=[colors[key] for key in labels])
    plt.axis('equal')
    plt.savefig(settings.STATIC_ROOT + settings.STATIC_URL + 'sentiments.png')

    # Return context to results page
    return render(request, 'demoapp/results.html', context)
