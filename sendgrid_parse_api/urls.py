from django.conf.urls.defaults import *
from .views import receiver

urlpatterns = patterns('',
    url(r'^$', receiver, name="sendgrid_parse_receiver"),
)
