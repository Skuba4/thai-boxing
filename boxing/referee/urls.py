from django.urls import path
from . import views

app_name = 'referee'

urlpatterns = [
    # БАЗОВЫЕ
    path('', views.Home.as_view(), name='home'),
    path('crate_room/', views.CreateRoom.as_view(), name='create_room'),
    path('my_rooms/', views.MyRooms.as_view(), name='my_rooms'),
    path('join_room/', views.JoinRoom.as_view(), name='join_room'),
    path('room/<uuid:uuid_room>/', views.DetailRoom.as_view(), name='detail_room'),
    # FIGHT
    path('create_fight/<uuid:uuid_room>/', views.CreateFight.as_view(), name='create_fight'),
    path('delete_fight/<uuid:uuid_fight>/', views.DeleteFight.as_view(), name='delete_fight'),
    path('change/<uuid:uuid_fight>/', views.ChangeFight.as_view(), name='change_fight'),
    path('set_winner/<uuid:uuid_fight>/', views.SetWinner.as_view(), name='set_winner'),
    # JUDGES
    path('view_notes/<uuid:uuid_fight>/', views.ViewNotes.as_view(), name='view_notes'),
    path('add_judge/<uuid:uuid_room>/', views.AddJudge.as_view(), name='add_judge'),
    path('delete_judge/<uuid:uuid_room>/<int:judge_id>/', views.DeleteJudge.as_view(), name='delete_judge'),
    path('toggle_judge/<uuid:uuid_room>/<int:judge_id>/', views.ToggleJudge.as_view(), name='toggle_judge'),
]



