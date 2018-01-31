from django.shortcuts import render
from nltk.classify import ClassifierI
from statistics import mode
from twitters.utils import ascii_unpickle
from twitters.models import TwitterClassiferAlgo
import traceback
import nltk
from ml_demo.config import nltk_data_path
nltk.data.path.append(nltk_data_path)
from nltk.tokenize import word_tokenize

import os
from django.conf import settings

word_file_path = os.path.join(os.path.join(settings.BASE_DIR, 'twitters'), 'data')

class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf

def genearte_vote_classifier():
    classifiers = TwitterClassiferAlgo.objects.values_list('classifier_pickled_data', flat=True)
    voted_classifier = VoteClassifier(*[ascii_unpickle(c) for c in classifiers])
    #print type(voted_classifier)
    return voted_classifier

def find_features(document):
    short_pos = open(os.path.join(word_file_path, "positive.txt"), "r").read()
    short_pos = short_pos.replace(" ", "")
    short_neg = open(os.path.join(word_file_path, "negative.txt"), "r").read()
    short_neg = short_neg.replace(" ", "")
    word_features = short_neg + short_pos
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        #print w, w in words
        features[w] = (w in words)
    return features

def sent_analyse(text):
    #print text
    feats = find_features(text)
    voted_classifier = genearte_vote_classifier()
    #print feats
    return voted_classifier.classify(feats), voted_classifier.confidence(feats)

def sentiment(request):
    try:
        print sent_analyse("This movie was utter junk. There were absolutely 0 pythons. I don't see what the point was at all. Horrible movie, 0/10")
    except Exception:
        print traceback.format_exc()
    return render(request, 'sentiments.html', {})

