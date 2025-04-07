from django.urls import re_path
from django.urls import path
from .consumers import ChatConsumer, GroupChatConsumer,TimelineConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>[\w.@+-]+)/$', ChatConsumer.as_asgi()),
    re_path(r"ws/group/(?P<group_name>[\w\s-]+)/$", GroupChatConsumer.as_asgi()),
    re_path(r"ws/timeline/$", TimelineConsumer.as_asgi()),



]
