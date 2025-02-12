from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from referee.forms import CreateRoomForm
from referee.models import Room


class Home(TemplateView):
    template_name = 'referee/home.html'


class CreateRoom(CreateView):
    model = Room
    template_name = 'referee/create_room.html'
    form_class = CreateRoomForm

    def form_valid(self, form):
        """form.instance(объект Room), .boss_room(обратились к полю главного судьи), self.request.user(и присвоили текущего пользователя)"""
        form.instance.boss_room = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """перенаправляем в detail_room с учетом адреса созданной комнаты"""
        return reverse_lazy('referee:detail_room', kwargs={'uuid_room': self.object.uuid_room})