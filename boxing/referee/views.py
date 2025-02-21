import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.shortcuts import get_object_or_404

from referee.forms import CreateRoomForm, FightForm
from referee.models import Room, RoomJudges, Fight, RoundScore
from users.models import User


class Home(TemplateView):
    template_name = 'referee/home.html'

class CreateRoom(CreateView):
    model = Room
    template_name = 'referee/create_room.html'
    form_class = CreateRoomForm

    def form_valid(self, form):
        '''form.instance(объект Room), .boss_room(обратились к полю главного судьи), self.request.user(и присвоили текущего пользователя)'''
        form.instance.boss_room = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        '''перенаправляем в detail_room с учетом адреса созданной комнаты'''
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.object.uuid_room})


class MyRooms(ListView):
    model = Room
    template_name = 'referee/my_rooms.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Room.objects.filter(boss_room=self.request.user)


class JoinRoom(View):
    def get(self, request):
        '''обычная загрузка страницы'''
        return render(request, 'referee/join_room.html')

    def post(self, request):
        '''отправка формы, работа с uuid'''
        uuid_room = request.POST.get('uuid_room')       # методом словаря get, взяли uuid_room из шаблона
        user = request.user                             # получили данные авторизованного пользователя

        try:
            room = Room.objects.get(uuid_room=uuid_room)
            RoomJudges.objects.create(room=room, user=user)                 # добавляем запись в промежуточную таблицу
            return redirect('referee:detail_room', uuid_room=uuid_room)
        except Room.DoesNotExist:
            return render(request, 'referee/join_room.html', {'error': 'Комната не найдена'})


class DetailRoom(DetailView):
    model = Room
    template_name = 'referee/room.html'
    context_object_name = 'object'
    slug_field = 'uuid_room'        # поле для поиска в модели
    slug_url_kwarg = 'uuid_room'    # имя переменной в path

    def get_context_data(self, **kwargs):
        '''формирую переменные для шаблона'''
        context = super().get_context_data(**kwargs)

        ### КОМНАТА
        room = context['object']    # объект АКТИВНОЙ комнаты
        context['uuid'] = room.uuid_room

        ### СУДЬИ
        context['is_boss'] = self.request.user == room.boss_room    # главный или нет
        context['is_active_judge'] = RoomJudges.objects.filter(room=room, user=self.request.user, is_active=True).exists()      # боковой судья или нет
        judges = RoomJudges.objects.filter(room=room)
        context['judges'] = judges                                 # получили ВСЕХ боковых судей
        context['judges_activ'] = judges.filter(is_active=True)    # только АКТИВНЫХ боковых судей

        ### БОИ(данные пар)
        context['fights'] = Fight.objects.filter(room=room)     # все бои для текущей комнаты

        return context

    def get_object(self, queryset=None, **kwargs):
        '''если uuid введен не верно, выводим свою ошибку вместо стандартной 404'''
        try:
            return get_object_or_404(Room, uuid_room=self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            # Добавляем кастомное сообщение
            raise Http404("Комната с таким UUID не найдена")


class CreateFight(LoginRequiredMixin, CreateView):
    model = Fight
    form_class = FightForm
    template_name = "referee/room.html"

    def form_valid(self, form):
        uuid_room = self.kwargs.get('uuid_room')
        room = get_object_or_404(Room, uuid_room=uuid_room)

        fight = form.save(commit=False)
        fight.room = room

        try:
            fight.save()
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Бой с таким номером уже существует в этой комнате.'}, status=400)

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            fights = Fight.objects.filter(room=room)
            fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=self.request)
            return JsonResponse({'success': True, 'fights_html': fights_html})

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.kwargs['uuid_room']})


class ChangeFight(LoginRequiredMixin, UpdateView):
    model = Fight
    form_class = FightForm
    template_name = "referee/room.html"

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


class SetWinner(LoginRequiredMixin, View):
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


class ViewNotes(LoginRequiredMixin, View):
    '''смотрим судейские записки'''
    def get(self, request, uuid_fight):
        fight = get_object_or_404(Fight, uuid=uuid_fight)
        rounds = RoundScore.objects.filter(fight=fight).order_by('round_number')

        # Формируем данные для отправки в формате JSON
        notes_data = []
        for round_score in rounds:
            notes_data.append({
                'round_number': round_score.round_number,
                'decision_1': round_score.decision_1,
                'decision_2': round_score.decision_2,
                'decision_3': round_score.decision_3,
            })

        return JsonResponse({'success': True, 'notes': notes_data})


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


class ToggleJudge(LoginRequiredMixin, View):
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