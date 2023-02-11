from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index),
    path('index/', views.index, name='index'),
    path('group_list/', views.group_list, name='group_list'),
]