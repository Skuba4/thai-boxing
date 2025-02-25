import json
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404

from referee.models import Room, RoomJudges, Fight, RoundScore
from users.models import User

__all__ = ['AddJudge', 'DeleteJudge', 'ActiveJudge']


class AddJudge(LoginRequiredMixin, View):
    def post(self, request, uuid_room):
        try:
            data = json.loads(request.body)
            username = data.get('username')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Ошибка чтения JSON.'})

        if not username:
            return JsonResponse({'success': False, 'error': 'Имя пользователя не указано.'})

        room = get_object_or_404(Room, uuid_room=uuid_room)

        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пользователь не найден.'})

        if user_to_add == request.user:
            return JsonResponse({'success': False, 'error': 'Вы не можете добавить себя как судью.'})

        if RoomJudges.objects.filter(room=room, user=user_to_add).exists():
            return JsonResponse({'success': False, 'error': 'Этот судья уже добавлен.'})

        RoomJudges.objects.create(room=room, user=user_to_add)

        # ✅ Перерендерим список судей
        judges = RoomJudges.objects.filter(room=room)
        judges_html = render_to_string('referee/includes/judges_list.html', {'judges': judges}, request=request)

        return JsonResponse({'success': True, 'judges_html': judges_html})


class DeleteJudge(LoginRequiredMixin, View):
    def post(self, request, uuid_room, judge_id):
        room = get_object_or_404(Room, uuid_room=uuid_room)
        judge = get_object_or_404(RoomJudges, room=room, user_id=judge_id)

        # Удаляем судью
        judge.delete()

        # ✅ Обновляем список судей
        judges = RoomJudges.objects.filter(room=room)
        judges_html = render_to_string('referee/includes/judges_list.html', {'judges': judges}, request=request)

        return JsonResponse({'success': True, 'judges_html': judges_html})


class ActiveJudge(LoginRequiredMixin, View):
    def post(self, request, uuid_room, judge_id):
        room = get_object_or_404(Room, uuid_room=uuid_room)
        judge = get_object_or_404(RoomJudges, room=room, user_id=judge_id)

        if not judge.is_active:
            # Проверяем лимит активных судей
            active_judges_count = RoomJudges.objects.filter(room=room, is_active=True).count()
            if active_judges_count >= 3:
                return JsonResponse({'success': False, 'error': 'Можно выбрать не более 3 активных судей.'})
            judge.is_active = True
        else:
            judge.is_active = False

        judge.save()

        # ✅ Обновляем список судей
        judges = RoomJudges.objects.filter(room=room)
        judges_html = render_to_string('referee/includes/judges_list.html', {'judges': judges}, request=request)

        return JsonResponse({'success': True, 'judges_html': judges_html})
