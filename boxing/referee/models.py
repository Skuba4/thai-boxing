import uuid
from django.db import models

from users.models import User


class Room(models.Model):
    '''данные комнаты'''
    name = models.CharField(max_length=50, blank=False)
    uuid_room = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    boss_room = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boss')
    judges = models.ManyToManyField(User, related_name='judges_rooms', through='RoomJudges')

    def __str__(self):
        return 'данные комнаты'


class RoomJudges(models.Model):
    '''связь между комнатой и судьями через юзернеймы, для назначения списка судей'''
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_judges')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_judges')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return 'судья-комната'


class Fight(models.Model):
    '''информация о бое(бойцы, раунд)'''
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='fights')
    number_fight = models.PositiveIntegerField(unique=True, blank=False)
    fighter_1 = models.CharField(max_length=50, blank=False)
    fighter_2 = models.CharField(max_length=50, blank=False)
    winner = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return 'комната - пара - победитель'


class RoundScore(models.Model):
    '''информаия по каждому раунду от боковых судей'''
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField()
    decision_1 = models.TextField()       # судейская записка ПЕРВОГО судьи
    decision_2 = models.TextField()       # судейская записка ВТОРОГО судьи
    decision_3 = models.TextField()       # судейская записка ТРЕТЬЕГО судьи

    def __str__(self):
        return 'информация о раунде'




