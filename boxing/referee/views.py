from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.shortcuts import get_object_or_404

from referee.forms import CreateRoomForm
from referee.models import Room, RoomJudges


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
    slug_field = 'uuid_room'        # поле по которому ищем в модели
    slug_url_kwarg = 'uuid_room'    # указывает по какому значению из ссылки будет происходить поиск в таблице

    #     def get_context_data(self, **kwargs):
    #         context = super().get_context_data(**kwargs)
    #         room = context['object']  # Получаем объект комнаты из контекста
    #
    #         # Проверка, является ли текущий пользователь главным судьей
    #         context['is_boss'] = self.request.user == room.boss
    #
    #         # Получаем уникальных боковых судей (те, кто имеет роль 'judge')
    #         # Мы получаем все записи для данной комнаты и роли "judge"
    #         judges = RoomUsers.objects.filter(room=room, role='judge')
    #
    #         # Используем set для удаления повторений по полю 'user'
    #         unique_judges = list({judge.user for judge in judges})
    #
    #         context['judges'] = unique_judges
    #
    #         # Получаем все пары боев
    #         context['fights'] = Fight.objects.filter(room=room)
    #
    #         return context

    def get_object(self, queryset=None, **kwargs):
        '''если uuid введен не верно, то даст ошибку 404 (ПОД ВОПРОСОМ НУЖЕН ЛИ)'''
        return get_object_or_404(Room, uuid_room=self.kwargs.get(self.slug_url_kwarg))


