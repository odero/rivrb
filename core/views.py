from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView
from django.conf import settings
from django.core.cache import cache

from .models import Topic

import twitter
import random

CACHE_TIMEOUT = 60 * 10  # 10 minutes


class HomeView(TemplateView):
    template_name = 'core/home.html'
    api = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self._get_api()
            query = self.request.GET.get('q', '')

            if query:
                self.add_topic(query)
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        ctx = super(HomeView, self).get_context_data(**kwargs)
        statuses = self.get_top_10_tweets()
        random.shuffle(statuses)
        ctx['statuses'] = statuses
        ctx['trends'] = self.get_trending_topics()
        ctx['query'] = self.request.GET.get('q', '')
        if user.is_authenticated():
            ctx['my_topics'] = user.topics.all()
        return ctx

    def add_topic(self, topic_name):
        topic, created = Topic.objects.get_or_create(name=topic_name)
        topic.users.add(self.request.user)

    def get_top_10_tweets(self):
        # if search term fetch top 10 tweets with that hashtag
        # else fetch top 10 tweets trending hashtag
        if not self.request.user.is_authenticated():
            return []

        query = self.request.GET.get('q')

        tweets = cache.get(query, None)
        if tweets is None:
            if query:
                tweets = self._search_top_10_tweets(query)
                # self.favorite_tweets(tweets)
            else:
                tweets = self.get_trending()

            cache.set(query, tweets, CACHE_TIMEOUT)
        return tweets

    def favorite_tweets(self, tweets):

        users = {}
        for tweet in tweets:
            # dont try to favorite if had already favorited
            if not tweet.favorited:

                # don't favorite more than 2 tweets from one user
                sender = tweet.user.screen_name
                u = users.get(sender)
                if u:
                    if users[sender] == 2:
                        continue
                    else:
                        users[sender] += 1
                else:
                    users[sender] = 1
                self.api.CreateFavorite(id=tweet.id)

    def retweet(self, tweets):
        for tweet in tweets:
            self.api.PostRetweet(tweet.id)

    def get_trending_topics(self):
        if not self.request.user.is_authenticated():
            return []

        trends = cache.get('trends')
        if not trends:
            trends = self.api.GetTrendsCurrent()
            cache.set('trends', trends, CACHE_TIMEOUT)
        return trends

    def get_trending(self):
        # fetch global trends
        # TODO: figure out how to get woeid for location-based trends
        trends = self.get_trending_topics()
        statuses = self._search_top_10_tweets(trends[0].name)
        # TODO: then cache for 5 minutes
        return statuses

    def _search_top_10_tweets(self, search_term):
        # fetch
        statuses = self.api.GetSearch(search_term)
        return statuses

    def _get_api(self):
        user = self.request.user
        # get access tokens
        if not self.api:
            social_auth_context = user.social_auth.order_by('-id')[0]
            access_token = social_auth_context.extra_data['access_token']
            token_secret = access_token['oauth_token_secret']
            token_key = access_token['oauth_token']

            self.api = twitter.Api(
                consumer_key=settings.SOCIAL_AUTH_TWITTER_KEY, consumer_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                access_token_key=token_key, access_token_secret=token_secret)
        return self.api
