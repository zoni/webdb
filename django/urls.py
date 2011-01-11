from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^webdb/', include('webdb.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    #(r'^accounts/', include('django.contrib.auth.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
    (r'^accounts/password_change/done/$', 'django.contrib.auth.views.password_change_done'),
    (r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset'),
    (r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^accounts/reset/done/$', 'django.contrib.auth.views.password_reset_complete'),

    (r'^$', include(admin.site.urls)),
)

