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

    class Meta:
        unique_together = ('room', 'user')  # ✅ Один судья не может быть добавлен дважды в одну комнату

    def __str__(self):
        return 'судья-комната'


class Fight(models.Model):
    WINNER_CHOICES = [
        ('fighter_1', 'Боец 1'),
        ('fighter_2', 'Боец 2'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='fights')
    number_fight = models.PositiveIntegerField(blank=False)
    fighter_1 = models.CharField(max_length=50, blank=False)
    fighter_2 = models.CharField(max_length=50, blank=False)
    winner = models.CharField(max_length=10, choices=WINNER_CHOICES, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'number_fight'], name='unique_fight_per_room')
        ]
        indexes = [
            models.Index(fields=['room', 'number_fight']),
            models.Index(fields=['fighter_1']),
            models.Index(fields=['fighter_2']),
        ]

    def save(self, *args, **kwargs):
        """Генерируем номер боя, если его нет"""
        if not self.number_fight:
            last_fight = Fight.objects.filter(room=self.room).order_by('-number_fight').first()
            self.number_fight = last_fight.number_fight + 1 if last_fight else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.number_fight}: {self.fighter_1} vs {self.fighter_2}'


class Notes(models.Model):
    data = models.DateField(auto_now=True)
    fight_number = models.IntegerField()
    judge = models.CharField(max_length=50)
    red_fighter = models.CharField(max_length=100)
    blue_fighter = models.CharField(max_length=100)
    round_number = models.IntegerField()
    red_remark = models.CharField(max_length=250)
    blue_remark = models.CharField(max_length=250)
    winner = models.CharField(max_length=10, choices=[("red", "Красный угол"), ("blue", "Синий угол")])

    def __str__(self):
        return 'судейская записка'
