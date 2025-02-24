import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.shortcuts import get_object_or_404

from referee.forms import FightForm
from referee.models import Room, Fight

__all__ = ['CreateFight', 'EditFight', 'DeleteFight', 'WinnerFight']


class CreateFight(LoginRequiredMixin, CreateView):
    model = Fight
    form_class = FightForm
    template_name = "referee/detail_room.html"

    def form_valid(self, form):
        uuid_room = self.kwargs.get('uuid_room')
        room = get_object_or_404(Room, uuid_room=uuid_room)

        fight = form.save(commit=False)
        fight.room = room

        try:
            fight.save()
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Бой с таким номером уже существует в этой комнате.'},
                                status=400)

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            fights = Fight.objects.filter(room=room)
            fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights},
                                           request=self.request)
            return JsonResponse({'success': True, 'fights_html': fights_html})

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.kwargs['uuid_room']})


class EditFight(LoginRequiredMixin, UpdateView):
    model = Fight
    form_class = FightForm
    template_name = "referee/detail_room.html"

    slug_field = 'uuid'  # ✅ Django ищет бой по UUID
    pk_url_kwarg = 'uuid_fight'  # ✅ Должно совпадать с URL

    def get_object(self, queryset=None):
        """Находим бой по UUID (чуть надежнее)"""
        uuid_fight = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(Fight, uuid=uuid_fight)

    def form_valid(self, form):
        """Обновляем бой и возвращаем JSON с отловом ошибок"""
        try:
            fight = form.save()

            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                fights = Fight.objects.filter(room=fight.room)
                fights_html = render_to_string(
                    'referee/includes/fights_list.html',
                    {'fights': fights},
                    request=self.request
                )
                return JsonResponse({'success': True, 'fights_html': fights_html})

            return super().form_valid(form)

        except IntegrityError:
            # ✅ Ловим ошибку при дублировании номера боя
            return JsonResponse({'success': False, 'error': 'Бой с таким номером уже существует!'}, status=400)

    def get_success_url(self):
        """После редактирования вернуться обратно в комнату"""
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.object.room.uuid_room})


class DeleteFight(LoginRequiredMixin, View):
    def post(self, request, uuid_fight):  # ✅ Удаление по UUID, а не по number_fight
        fight = get_object_or_404(Fight, uuid=uuid_fight)  # ✅ Теперь ищем по UUID

        if fight.room.boss_room != request.user:
            return JsonResponse({'success': False, 'error': 'Ты не можешь удалить этот бой!'})

        fight.delete()
        fights = Fight.objects.filter(room=fight.room)
        fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=request)

        return JsonResponse({'success': True, 'fights_html': fights_html})


class WinnerFight(LoginRequiredMixin, View):
    def post(self, request, uuid_fight):
        fight = get_object_or_404(Fight, uuid=uuid_fight)

        try:
            data = json.loads(request.body)
            winner = data.get('winner')

            if winner not in ['fighter_1', 'fighter_2', 'draw']:
                return JsonResponse({'success': False, 'error': 'Некорректный выбор победителя.'})

            fight.winner = winner
            fight.save()

            # Обновляем список боёв после выбора победителя
            fights = Fight.objects.filter(room=fight.room)
            fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=request)

            return JsonResponse({'success': True, 'fights_html': fights_html})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Ошибка обработки данных.'})
