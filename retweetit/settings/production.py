import os

from ..settings.base import *

import herokuify

from herokuify.common import *              # Common settings, SSL proxy header
from herokuify.aws import *                 # AWS access keys as configured in env
from herokuify.mail.mailgun import *        # Email settings for Mailgun add-on
from herokuify.mail.sendgrid import *       # ... or Sendgrid

DEBUG = bool(os.environ.get('DEBUG_MODE')) or False

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['rivrb.herokuapp.com']

# To not use https which is default
# AWS_S3_SECURE_URLS = False

# # prevent expiration querystrings
# AWS_QUERYSTRING_AUTH = False

# AWS_STORAGE_BUCKET_NAME = 'cdn.retweetit.com'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# # AWS and herokuify configs
# DEFAULT_FILE_STORAGE = "herokuify.storage.S3MediaStorage"
# MEDIA_URL = "//{0}.s3.amazonaws.com/media/".format(AWS_STORAGE_BUCKET_NAME)

# STATICFILES_STORAGE = "herokuify.storage.CachedS3StaticStorage"
# STATIC_URL = "//{0}.s3.amazonaws.com/static/".format(AWS_STORAGE_BUCKET_NAME)

# COMPRESS_STORAGE = "herokuify.storage.CachedS3StaticStorage"
# COMPRESS_OFFLINE = True


DATABASES = herokuify.get_db_config()       # Database config
CACHES = herokuify.get_cache_config()       # Cache config for Memcache/MemCachier

SECRET_KEY = os.environ.get('DJANGO_SECRET')

BROKER_URL = os.environ.get('REDISCLOUD_URL')

INSTALLED_APPS += (
    'waitress',
)

# Twitter OAuth Keys
SOCIAL_AUTH_TWITTER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

TWITTER_ACCESS_TOKEN_KEY = os.environ.get('TWITTER_ACCESS_TOKEN_KEY')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('MANDRILL_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('MANDRILL_APIKEY')
