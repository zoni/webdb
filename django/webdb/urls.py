from django.conf.urls.defaults import *

urlpatterns = patterns('webdb.views',
    #url(r'^$', 'view', name='scanner_index'),
    #(r'^view/([\w<>, -]*)', 'view'),
    #(r'^view/([^/]*)', 'view'),
    #(r'^inbound/([^/]*)', 'inbound'),
    (r'^([^/]*)/([^/]*)', 'index'),
)

