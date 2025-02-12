from django.urls import path
from . import views

app_name = 'referee'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('crate_room/', views.CreateRoom.as_view(), name='create_room'),
    path('<uuid:uuid_room>:/', views.Home.as_view(), name='detail_room'),
]