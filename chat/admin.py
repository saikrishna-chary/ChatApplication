from django.contrib import admin
from .models import CustomUser, ChatRoom, Message

admin.site.register(CustomUser)
admin.site.register(ChatRoom)
admin.site.register(Message)
