from django.urls import path, re_path
import downloads.views as views

urlpatterns = [
    path('data/create/', views.CreatePath.as_view()),

    re_path(r'^files/archive/(?P<key>[a-f0-9]{40})/(?P<path>[^.]+\.tar\.gz)$', views.send_archive),
    re_path(r'^files/snapshot/(?P<key>[a-f0-9]{40})/(?P<path>.+)$', views.send_snapshot),
    re_path(r'^files/raw/(?P<key>[a-f0-9]{40})/(?P<path>.+)$', views.send_file),
    re_path(r'^files/multi/(?P<key>[a-f0-9]{40})/(?P<path>[^.]+\.tar\.gz)$', views.SendMulti.as_view()),
    re_path(r'^files/frame/(?P<key>[a-f0-9]{40})/(?P<path>.+)/(?P<brightness>\w{2}).png$', views.SendFrame.as_view()),
]
