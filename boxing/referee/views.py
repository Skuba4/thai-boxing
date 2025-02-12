from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView

from referee.forms import CreateRoomForm
from referee.models import Room, RoomUsers


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
    '''обычная загрузка страницы'''
    def get(self, request):
        return render(request, 'referee/join_room.html')

    '''отправка формы, работа с uuid'''
    def post(self, request):
        uuid_room = request.POST.get('uuid_room')       # методом словаря get, взяли uuid_room из шаблона
        role = request.POST.get('role')                 # аналогично
        user = request.user                             # получили данные залогиненного пользователя

        try:
            room = Room.objects.get(uuid_room=uuid_room)
            # добавляем запись в промежуточную таблицу
            RoomUsers.objects.create(room=room, user=user, role=role)
        except Room.DoesNotExist:
            return render(request, 'referee/join_room.html', {'error': 'Комната не найдена'})

        return redirect('referee:detail_room', uuid_room=uuid_room)




# def get(self, request):
#     return render(request, 'referee/join_room.html')
#












# class DetailRoom(DetailView):
#     model = Room
#     template_name = 'template.html'  # имя шаблона
#
#     context_object_name = 'object'  # имя объекта в шаблоне (по умолчанию 'object')
#     pk_url_kwarg = 'pk'  # имя переданное из path (для pk)
#     slug_field = 'slug'  # поле модели для поиска по slug (по умолчанию 'slug')
#     slug_url_kwarg = 'slug'  # имя переданное из path (для slug)
#     queryset = MyModel.objects.all()  # queryset выборка из БД, далее берем объект по pk или slug
#
#     def get_context_data(self, **kwargs):  # дополнительные ДИНАМИЧЕСКИЕ ДАННЫЕ
#         context = super().get_context_data(**kwargs)  # сформировали базовый набор
#         context['variable'] = 'value'  # добавляем в сформированный context
#         return context
#
#     def get_object(self, queryset=None):  # извлечения объекта из базы данных по заданным параметрам
#         return get_object_or_404(MyModel.objects, slub='slug')  # либо даст объект, либо 404