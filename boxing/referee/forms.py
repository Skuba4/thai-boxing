from django import forms

from referee.models import Room


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name',]
        labels = {
            'name': 'Введите имя комнаты',
        }