from django.urls import path
from . import views

app_name = 'referee'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('crate_room/', views.CreateRoom.as_view(), name='create_room'),
    path('my_rooms/', views.MyRooms.as_view(), name='my_rooms'),
    path('join_room/', views.JoinRoom.as_view(), name='join_room'),
    path('room/<uuid:uuid_room>/', views.DetailRoom.as_view(), name='detail_room'),

    path('create_fight/<uuid:uuid_room>/', views.CreateFight.as_view(), name='create_fight'),
    path('delete_fight/<int:number_fight>/', views.DeleteFight.as_view(), name='delete_fight'),
    path('change/<int:number_fight>/', views.ChangeFight.as_view(), name='change_fight'),
]