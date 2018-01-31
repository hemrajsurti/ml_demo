from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^closegraph/(?P<ticker>)$', views.closegraph, name='closegraph')
]