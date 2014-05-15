try:
    from ..settings.local import *
except Exception, e:
    from ..settings.production import *
