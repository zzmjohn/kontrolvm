from django.conf.urls.defaults import *

urlpatterns = patterns('apps.instance.views',
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'^delete-task/(?P<pk>\d+)/', 'delete_task'),
  url(r'^add', 'add'),
  url(r'^$', 'index'),
)
