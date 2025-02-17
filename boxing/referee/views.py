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
        fight.save()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            fights = Fight.objects.filter(room=room)
            fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=self.request)
            return JsonResponse({'success': True, 'fights_html': fights_html})

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.kwargs['uuid_room']})


class DeleteFight(LoginRequiredMixin, View):
    # View лучше работает с ajax(проще) чем DeleteView
    def post(self, request, number_fight):
        fight = get_object_or_404(Fight, number_fight=number_fight)

        if fight.room.boss_room != request.user:
            return JsonResponse({'success': False, 'error': 'Ты не можешь удалить этот бой!'})

        fight.delete()
        fights = Fight.objects.filter(room=fight.room)
        fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=request)

        return JsonResponse({'success': True, 'fights_html': fights_html})


class ChangeFight(LoginRequiredMixin, View):
    def post(self, request, number_fight):
        fight = get_object_or_404(Fight, number_fight=number_fight)  # 🔍 Ловим бой по номеру
        print(f"🔍 Найден бой: {fight}")

        if fight.room.boss_room != request.user:
            print("⛔ Ошибка: пользователь не является главным судьёй!")
            return JsonResponse({'success': False, 'error': 'Ты не можешь редактировать этот бой!'})

        form = FightForm(request.POST, instance=fight)

        if form.is_valid():
            new_number_fight = form.cleaned_data.get('number_fight')
            print(f"🔄 Новый номер боя: {new_number_fight}")

            # Проверяем, не существует ли уже такой номер
            if Fight.objects.filter(number_fight=new_number_fight).exclude(id=fight.id).exists():
                print("⚠ Ошибка: Такой номер боя уже существует!")
                return JsonResponse({'success': False, 'error': 'Такой номер боя уже существует!'})

            fight.fighter_1 = form.cleaned_data.get('fighter_1')
            fight.fighter_2 = form.cleaned_data.get('fighter_2')
            fight.number_fight = new_number_fight  # 🔥 Тут меняем номер боя прямо в объекте
            fight.save()

            print("✅ Бой успешно обновлён!")

            fights = Fight.objects.filter(room=fight.room)
            fights_html = render_to_string('referee/includes/fights_list.html', {'fights': fights}, request=request)

            return JsonResponse({'success': True, 'fights_html': fights_html})

        print("❌ Ошибка валидации формы!")
        print(form.errors)
        return JsonResponse({'success': False, 'error': 'Ошибка валидации формы'})
