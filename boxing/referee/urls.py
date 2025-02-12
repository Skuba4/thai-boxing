from django.urls import path
from . import views

app_name = 'referee'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('crate_room/', views.CreateRoom.as_view(), name='create_room'),
    path('my_rooms/', views.MyRooms.as_view(), name='my_rooms'),
    path('join_room/', views.JoinRoom.as_view(), name='join_room')
    # path('room/<uuid:uuid_room>/', views.DetailRoom.as_view(), name='detail_room'),
]