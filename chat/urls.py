'''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('set-password/', views.set_password_view, name='set_password'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    # ⚠️ Important: int path MUST come before str path
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/<str:username>/', views.chat_with, name='chat_with'),

    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),

    #path('upload_media/<int:room_id>/', views.upload_media_room, name='upload_media_room'),
    #path('upload_media/<str:username>/', views.upload_media, name='upload_media'),
    path("group/<int:room_id>/", views.chat_room, name="chat_room"),
    path("group/<int:room_id>/manage/", views.manage_group, name="manage_group"),

    path('group/<int:room_id>/manage/', views.manage_group, name='manage_group'),
    path('group/<int:room_id>/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    #path('group/<int:room_id>/add/', views.add_members, name='add_members'),
    path('group/<int:room_id>/delete/', views.delete_group, name='delete_group'),
    path('chat/<str:username>/upload/', views.upload_media, name='upload_media'),
    path('chat/room/<int:room_id>/upload/', views.upload_media_room, name='upload_media_room'),

]
'''

from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('set-password/', views.set_password_view, name='set_password'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 📌 Private Chat
    path('chat/<str:username>/', views.chat_with, name='chat_with'),
    path('chat/<str:username>/upload/', views.upload_media, name='upload_media'),

    # 📌 Group Chat
    #path('group/<int:room_id>/', views.chat_room, name='group_chat'),
    path('group/<int:room_id>/upload/', views.upload_media_room, name='upload_media_room'),
    path('group/<int:room_id>/', views.chat_room, name='chat_room'),

    # Group Management
    path('group/<int:room_id>/manage/', views.manage_group, name='manage_group'),
    path('group/<int:room_id>/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    path('group/<int:room_id>/delete/', views.delete_group, name='delete_group'),
    path('group/<int:room_id>/add/', views.add_members, name='add_members'),

    # Group Room List & Creation
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),


    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('set-new-password/', views.set_new_password_view, name='set_new_password'),

    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path("delete-message/<int:message_id>/", views.delete_message, name="delete_message"),

]
