from __future__ import unicode_literals

from django.db import models

# Create your models here.


class TwitterClassiferAlgo(models.Model):
    classifer_name = models.CharField(max_length=50, primary_key=True)
    classifier_pickled_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.yahoo_sht)

    def save(self, *args, **kwargs):
        self.classifer_name = self.classifer_name.lower()
        super(TwitterClassiferAlgo, self).save(*args, **kwargs)


class Tweets(models.Model):
    tweets = models.TextField()
    sentiment = models.CharField(max_length=50)
    confidence = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.tweets)