import uuid
from django.db import models

from users.models import User


class Room(models.Model):
    name = models.CharField(max_length=50, blank=False)
    uuid_room = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    boss_room = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boss")
    user = models.ManyToManyField(User, related_name="rooms", through="RoomUsers")

    def __str__(self):
        return self.name


class RoomUsers(models.Model):
    '''промежуточная модель'''

    class Role(models.IntegerChoices):
        OBSERVER = 1, "Наблюдатель"
        JUDGE = 2, "Судья"

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.JUDGE)

    def __str__(self):
        return 'данные из промежуточной модели'