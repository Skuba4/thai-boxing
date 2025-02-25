from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from referee.forms import CreateRoomForm
from referee.models import Room, RoomJudges, Fight

__all__ = ['CreateRoom', 'MyRooms', 'DeleteRoom', 'JoinRoom', 'DetailRoom']


class CreateRoom(LoginRequiredMixin, CreateView):
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


class MyRooms(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'referee/my_rooms.html'
    context_object_name = 'object'

    def get_queryset(self):
        return Room.objects.filter(boss_room=self.request.user)


class DeleteRoom(LoginRequiredMixin, View):
    def post(self, request, uuid_room):
        room = get_object_or_404(Room, uuid_room=uuid_room, boss_room=request.user)
        room.delete()

        rooms = Room.objects.filter(boss_room=request.user)
        rooms_html = render_to_string('referee/includes/room_list.html', {'object': rooms}, request=request)

        return JsonResponse({'success': True, 'rooms_html': rooms_html})


class JoinRoom(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'referee/join_room.html')

    def post(self, request):
        uuid_room = request.POST.get('uuid_room')

        try:
            Room.objects.get(uuid_room=uuid_room)
            return redirect('referee:detail_room', uuid_room=uuid_room)
        except Room.DoesNotExist:
            return render(request, 'referee/join_room.html', {'error': 'Комната не найдена'})


class DetailRoom(LoginRequiredMixin, DetailView):
    model = Room
    template_name = 'referee/detail_room.html'
    context_object_name = 'object'
    slug_field = 'uuid_room'  # поле для поиска в модели
    slug_url_kwarg = 'uuid_room'  # имя переменной в path

    def get_context_data(self, **kwargs):
        '''формирую переменные для шаблона'''
        context = super().get_context_data(**kwargs)

        ### КОМНАТА
        room = context['object']  # объект АКТИВНОЙ комнаты
        context['uuid'] = room.uuid_room

        ### СУДЬИ
        context['is_boss'] = self.request.user == room.boss_room  # главный или нет
        context['is_active_judge'] = RoomJudges.objects.filter(room=room, user=self.request.user,
                                                               is_active=True).exists()  # боковой судья или нет
        judges = RoomJudges.objects.filter(room=room)
        context['judges'] = judges  # получили ВСЕХ боковых судей
        context['judges_activ'] = judges.filter(is_active=True)  # только АКТИВНЫХ боковых судей

        ### БОИ(данные пар)
        context['fights'] = Fight.objects.filter(room=room)  # все бои для текущей комнаты

        return context

    def get_object(self, queryset=None, **kwargs):
        '''если uuid введен не верно, выводим свою ошибку вместо стандартной 404'''
        try:
            return get_object_or_404(Room, uuid_room=self.kwargs.get(self.slug_url_kwarg))
        except Http404:
            # Добавляем кастомное сообщение
            raise Http404("Комната с таким UUID не найдена")
