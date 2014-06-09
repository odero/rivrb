from django.shortcuts import render, redirect

from django.views.generic.base import TemplateView
from django.conf import settings
from django.core.cache import cache

from .models import Topic, Location

import twitter
import random

import requests

CACHE_TIMEOUT = 60 * 10  # 10 minutes


class HomeView(TemplateView):
    template_name = 'core/home.html'
    api = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self._get_api()
            query = self.request.GET.get('q', '').strip()

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
        ctx['query'] = self.request.GET.get('q', '').strip()
        if user.is_authenticated():
            ctx['my_topics'] = user.topics.all()
        return ctx

    def add_topic(self, topic_name):
        topics = Topic.objects.filter(name__iexact=topic_name)
        if topics.exists():
            topic = topics[0]
        else:
            topic = Topic.objects.create(name=topic_name)
        topic.users.add(self.request.user)

    def get_top_10_tweets(self):
        # if search term fetch top 10 tweets with that hashtag
        # else fetch top 10 tweets trending hashtag
        if not self.request.user.is_authenticated():
            return []

        query = self.request.GET.get('q', '').strip()

        tweets = cache.get(query, None)
        if tweets is None:
            if query:
                tweets = self._search_top_10_tweets(query)
                random.shuffle(tweets)
                self.favorite_tweets(tweets[:settings.TWEETS_APPLIED])
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
                try:
                    self.api.CreateFavorite(id=tweet.id)
                except Exception:
                    pass

    def retweet(self, tweets):
        for tweet in tweets:
            self.api.PostRetweet(tweet.id)

    def get_trending_topics(self):
        if not self.request.user.is_authenticated():
            return []

        tweep = self.get_twitter_profile()
        if not tweep:
            return []

        # use twitter timezone
        # if no timezone use twitter location
        # else fallback to worldwide trends
        if tweep.time_zone:
            loc_id = self.get_woeid(tweep.time_zone)
        elif tweep.location:
            loc_id = self.get_woeid(tweep.location)

        if loc_id:
            trends = self.get_location_trends(loc_id)
        else:
            trends = self.get_global_trends()

        return trends

    def get_twitter_profile(self):
        tweep = cache.get(self.request.user.username)
        if not tweep:
            tweep = self.api.GetUser(screen_name=self.request.user.username)
            if not tweep:
                return None
            cache.set(tweep.screen_name, tweep)
        return tweep

    def get_trending(self):
        trends = self.get_trending_topics()
        statuses_1 = self._search_top_10_tweets(trends[0].name)
        statuses_2 = self._search_top_10_tweets(trends[1].name)
        statuses = statuses_1 + statuses_2
        return statuses

    def _search_top_10_tweets(self, search_term):
        # fetch
        statuses = self.api.GetSearch(search_term)
        return statuses

    def get_woeid(self, loc_name):
        location = Location.objects.filter(name__iexact=loc_name)[:1]

        if location.exists():
            # location[0].users.add(self.request.user)
            return location[0].woeid

        url = 'https://query.yahooapis.com/v1/public/yql?q=select * from geo.places where text="{0}"&format=json'
        url = url.format(loc_name)

        try:
            resp = requests.get(url)
            json_resp = resp.json()
            places = json_resp['query']['results']['place']

            # query returns multiple places
            # give pref to first list item
            woeid = places[0]['woeid']
            name = places[0]['name']
            location = Location.objects.create(name=name, woeid=woeid)
            # location.users.add(self.request.user)
            return woeid
        except Exception, e:
            return 0

    def get_location_trends(self, woeid):
        cache_key = '{0}-trends'.format(woeid)
        trends = cache.get(cache_key)

        if not trends:
            trends = self.api.GetTrendsWoeid(woeid)
            cache.set(cache_key, trends, CACHE_TIMEOUT)
        return trends

    def get_global_trends(self):
        trends = cache.get('global-trends')
        if not trends:
            trends = self.api.GetTrendsCurrent()
            cache.set('global-trends', trends, CACHE_TIMEOUT)

        return trends

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


class DeleteTopicView(TemplateView):
    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            topics = Topic.objects.filter(pk=kwargs.get('topic_id'))
            if topics.exists():
                user.topics.remove(topics[0])

        return redirect('home')
