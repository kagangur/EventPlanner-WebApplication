"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from user.views import custom_logout_view
from user.views import register_view
from user import views




urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('',views.index,name = "index"),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/',register_view,name="register"),
    path('profile/',views.profile,name="profile"),
    path('stats/',views.stats,name="stats"),
    path('addevent/',views.addevent,name="addevent"),
    path('events/',views.events,name="events"),
    path('notifications/',views.notifications,name="notifications"),
    path('eventadvice/',views.eventadvice,name="eventadvice"),
    path('chats/',views.chats,name="chats"),
    path('eventmap/',views.eventmap,name="eventmap"),
    path('events/<int:id>/', views.eventdetail, name='eventdetail'),  # Event detail page
    path('events/basic/<int:id>/', views.event_detail1, name='event_detail_basic'),
    path('chats/<int:room_id>/', views.chatroom, name='chatroom'),
    path('profile/save_interests/', views.save_interests, name='save_interests'),
    path('profile/save_location/', views.save_location, name='save_location'),
    path('profile/save/', views.save_profile, name='save_profile'),
    path('save-profile-photo/', views.save_profile_photo, name='save_profile_photo'),
    path('changeprofile/', views.change_profile, name='change_profile'),
    path('chats/<int:room_id>/send/', views.send_message, name='send_message'),
    path('events/<int:id>/update/', views.update_event, name='update_event'),
    path('events/<int:id>/delete/', views.delete_event, name='delete_event'),
    path("forgot-password/", views.reset_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('delete_notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('route/<int:id>/', views.route_planner, name='route_planner'),
    path('join-event/<int:event_id>/', views.join_event, name='join_event'),
    path('leave_event/<int:id>/', views.leave_event, name='leave_event'),
    
    







]
