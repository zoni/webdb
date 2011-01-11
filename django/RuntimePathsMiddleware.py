from django.conf import settings
from django.core import signals
from django.core.urlresolvers import get_script_prefix

def set_runtime_paths(sender,**kwds):
    """Dynamically adjust path settings based on runtime configuration.

    This function adjusts various path-related settings based on runtime
    location info obtained from the get_script_prefix() function.  It also
    adds settings.BASE_URL to record the root of the Django server.
    """
    # We only want to run this once; the signal is just for bootstrapping
    signals.request_started.disconnect(set_runtime_paths)
    base_url = get_script_prefix()
    while base_url.endswith("/"):
        base_url = base_url[:-1]
    settings.BASE_URL = base_url
    #url_settings = ("MEDIA_URL","ADMIN_MEDIA_PREFIX","LOGIN_URL",
    #                         "LOGOUT_URL","LOGIN_REDIRECT_URL")
    url_settings = ("LOGIN_URL","LOGOUT_URL","LOGIN_REDIRECT_URL")

    for setting in url_settings:
        oldval = getattr(settings,setting)
        if "://" not in oldval and not oldval.startswith(settings.BASE_URL):
            if not oldval.startswith("/"):
                oldval = "/" + oldval
            setattr(settings,setting,settings.BASE_URL + oldval)

class RuntimePathsMiddleware:
    """Middleware to re-configure paths at runtime.

    This middleware class doesn't do any request processing.  Its only
    function is to connect the set_runtime_paths function to Django's
    request_started signal.  We use a middleware class to be sure that it's
    loaded before any requests are processed, but need to trigger on a signal
    because middleware is loaded before the script prefix is set.
    """
    def __init__(self):
        signals.request_started.connect(set_runtime_paths)

