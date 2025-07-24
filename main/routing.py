# main/routing.py

from django.urls import re_path
from . import consumers
from django.urls import path
websocket_urlpatterns = [
    

    path("ws/live-votes/", consumers.VoteConsumer.as_asgi()),
    re_path(r'ws/admin/dashboard/$', consumers.AdminDashboardConsumer.as_asgi()),

]
