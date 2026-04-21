from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache

from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm


# Миксин для проверки, что пользователь является владельцем объекта
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


# Миксин для менеджеров (просмотр всех объектов)
class ManagerOrOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return True
        obj = self.get_object()
        return obj.owner == user


# Главная страница
class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cache_key = f'home_stats_{user.id}'
        stats = cache.get(cache_key)
        if stats is None:
            if user.is_authenticated:
                mailings = Mailing.objects.filter(owner=user)
                total_mailings = mailings.count()
                active_mailings = mailings.filter(status='started').count()
                unique_recipients = Recipient.objects.filter(owner=user).distinct().count()
            else:
                total_mailings = Mailing.objects.count()
                active_mailings = Mailing.objects.filter(status='started').count()
                unique_recipients = Recipient.objects.count()
            stats = {
                'total_mailings': total_mailings,
                'active_mailings': active_mailings,
                'unique_recipients': unique_recipients,
            }
            cache.set(cache_key, stats, 60 * 5)  # кеш на 5 минут
        context.update(stats)
        return context


# --- CRUD для получателей ---
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Получатель успешно создан.')
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель обновлен.')
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Получатель удален.')
        return super().delete(request, *args, **kwargs)


# --- CRUD для сообщений ---
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages_list'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение создано.')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено.')
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Сообщение удалено.')
        return super().delete(request, *args, **kwargs)


# --- CRUD для рассылок ---
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Обновляем статусы перед отображением
        for mailing in context['mailings']:
            mailing.update_status()
        return context


class MailingDetailView(LoginRequiredMixin, ManagerOrOwnerMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка создана.')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена.')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Рассылка удалена.')
        return super().delete(request, *args, **kwargs)


# Отправка рассылки вручную
class MailingSendView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        user = self.request.user
        return user == mailing.owner or user.groups.filter(name='Менеджеры').exists()

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if not mailing.can_send():
            messages.error(request, 'Рассылка не может быть отправлена сейчас.')
            return redirect('mailing:mailing_detail', pk=pk)

        # Отправка писем
        success_count = 0
        fail_count = 0
        for recipient in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='OK'
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=str(e)
                )
                fail_count += 1

        messages.success(
            request,
            f'Рассылка завершена. Успешно: {success_count}, ошибок: {fail_count}.'
        )
        return redirect('mailing:mailing_detail', pk=pk)


# Статистика и отчеты
class MailingReportView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = Mailing.objects.filter(owner=user)
        context['mailings'] = mailings.annotate(
            success_attempts=Count('attempts', filter=Q(attempts__status='success')),
            failed_attempts=Count('attempts', filter=Q(attempts__status='failed'))
        )
        return context


# Страница попыток рассылки
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=user)