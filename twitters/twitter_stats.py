from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ml_demo.settings")
django.setup()
from twitters.views import sent_analyse
#from django.conf import settings
from twitters.models import Tweets
#word_file_path = os.path.join(os.path.join(settings.BASE_DIR, 'twitters'), 'data')

#consumer key, consumer secret, access token, access secret.
ckey = "ViWoARBRjVgWVQJVIYWU1SLmD"
csecret = "1jkZfJBwYCoZBfL6RjOIminHPXaOjQCQqKXiBpyJIcznWVmUYb"
atoken = "1471492488-4Qk5Nz46YzTy7MohvSN5IL7yaNF7UhnolUEXFqd"
asecret = "ZbVKpMjpnzD5VHnnJnKOAPvPx2TnHooLsNg7zPmD6fJFZ"


class listener(StreamListener):
    def on_data(self, data):
        all_data = json.loads(data)
        tweet = all_data["text"]
        sentiment_value, confidence = sent_analyse(str(tweet))
        #print(tweet, sentiment_value, confidence)
        Tweets.objects.create(confidence=confidence, sentiment=sentiment_value, tweets=tweet)
        return True

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["happy"])
