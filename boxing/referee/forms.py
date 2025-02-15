from django import forms

from referee.models import Room, Fight


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name',]
        labels = {
            'name': 'Введите имя комнаты',
        }


class FightForm(forms.ModelForm):
    class Meta:
        model = Fight
        fields = ['number_fight', 'fighter_1', 'fighter_2']
        labels = {
            'number_fight': 'Номер боя',
            'fighter_1': 'Первый боец',
            'fighter_2': 'Второй боец',
        }