try:
    from retweetit.settings.local import *
except Exception, e:
    from retweetit.settings.production import *
