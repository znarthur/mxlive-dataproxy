from django.conf.urls import url
import views

urlpatterns = [
    url(r'^data/create/', views.CreatePath.as_view()),
    url(r'^files/(?P<key>[a-f0-9]{40})/(?P<path>[^.]+)\.tar\.gz$', views.send_archive),
    url(r'^files/(?P<path>[^.]+)\.tar\.gz$', views.send_archive),
    #url(r'^data/(?P<key>[a-f0-9]{40})/(?P<path>[^.]+)\.tar\.gz$', views.send_archive, {'data_dir': True}),
    url(r'^files/(?P<key>[a-f0-9]{40})/(?P<path>.+)\.gif$', views.find_file),
    url(r'^files/(?P<key>[a-f0-9]{40})/(?P<path>.+)$', views.send_file),
]
