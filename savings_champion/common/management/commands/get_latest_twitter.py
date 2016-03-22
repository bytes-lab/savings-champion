"""
Gets the latest Twitter feed from settings-specific rss feed. This does 
not do anything clever such as linkyifying the urls, but probably should
going forward.
"""

from django.core.management.base import NoArgsCommand
from django.conf import settings
from common.models import Tweet
import datetime
from time import mktime
import feedparser


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        """ Check if each user has a corresponding notification preference """
        try :
            latest_tweet = Tweet.objects.latest('last_updated')
        except Tweet.DoesNotExist:
            latest_tweet = Tweet()

        feed_url = getattr(settings, 'TWITTER_RSS_FEED')
        feed = feedparser.parse(feed_url)
       
        for entry in feed['entries']:
            if not latest_tweet.last_updated or \
                    latest_tweet.last_updated < datetime.datetime.fromtimestamp(mktime(entry.get('updated_parsed'))) :
                
                latest_tweet.title = entry.get('title', '')
                latest_tweet.summary = entry.get('summary', '')
                latest_tweet.save()
            break