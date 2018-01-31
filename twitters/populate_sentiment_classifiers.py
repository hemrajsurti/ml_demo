import os, django
import psycopg2
from nltk.classify.scikitlearn import SklearnClassifier

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
# from django.core.management import settings
# settings.configure()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ml_demo.settings")
django.setup()
from ml_demo.settings import db_engine
from twitters.models import TwitterClassiferAlgo
from twitters.utils import ascii_pickle
import nltk
from ml_demo.config import nltk_data_path
nltk.data.path.append(nltk_data_path)
import random

featuresets = []
short_pos = open("data/positive.txt", "r").read()
short_pos = short_pos.replace(" ", "")
short_neg = open("data/negative.txt", "r").read()
short_neg = short_neg.replace(" ", "")
featuresets.extend([({p: True}, 'pos') for p in short_pos.split(',')])
featuresets.extend([({p: True}, 'neg') for p in short_neg.split(',')])
print len(featuresets)
random.shuffle(featuresets)


testing_set = featuresets[900:]
training_set = featuresets[:900]
print training_set[:5]
#exit()
def train_classifier(classifier_type, classifier_obj, training_set):
    print "Processing {} Algo".format(classifier_type)
    print training_set[:5]
    classifier = getattr(classifier_obj, 'train')(training_set)
    perc_accuracy = nltk.classify.accuracy(classifier, testing_set)*100
    print "{} Algo accuracy percent: {}".format(classifier_type, perc_accuracy)
    return classifier


###############
def save_classfier(name, classfier_obj):
    print "Training {}".format(name)
    classifer = ascii_pickle(classfier_obj)
    c, created = TwitterClassiferAlgo.objects.update_or_create(classifer_name=name,
                                          classifier_pickled_data=
                                                classifer
                                          )
    if created:
        print "{} Classifer trained".format(name)

cname = 'NaiveBayesClassifier'
classfier_obj = train_classifier(cname, nltk.NaiveBayesClassifier, training_set)
save_classfier(cname, classfier_obj)

cname = 'MNB_classifier'
MNB_classifier = SklearnClassifier(MultinomialNB())
classfier_obj = train_classifier(cname, MNB_classifier, training_set)
save_classfier(cname, classfier_obj)


cname = 'BernoulliNB_classifier'
BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
classfier_obj = train_classifier(cname, BernoulliNB_classifier, training_set)
save_classfier(cname, classfier_obj)


cname = 'LogisticRegression_classifier'
LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
classfier_obj = train_classifier(cname, LogisticRegression_classifier, training_set)
save_classfier(cname, classfier_obj)

cname = 'LinearSVC_classifier'
LinearSVC_classifier = SklearnClassifier(LinearSVC())
classfier_obj = train_classifier(cname, LinearSVC_classifier, training_set)
save_classfier(cname, classfier_obj)

cname = 'SGDC_classifier'
SGDC_classifier = SklearnClassifier(SGDClassifier())
classfier_obj = train_classifier(cname, SGDC_classifier, training_set)
save_classfier(cname, classfier_obj)


