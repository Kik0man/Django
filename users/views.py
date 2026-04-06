from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import CustomUser


class UserRegistrationView(CreateView):
    """Регистрация пользователя"""
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Отправка приветственного письма
        self.send_welcome_email(form.cleaned_data['email'])

        messages.success(self.request, 'Регистрация успешно завершена! Теперь вы можете войти в систему.')
        return response

    def send_welcome_email(self, user_email):
        """Отправка приветственного письма после регистрации"""
        try:
            subject = 'Добро пожаловать в Skystore!'
            message = f'''
            Здравствуйте!

            Спасибо за регистрацию в нашем магазине Skystore!

            Теперь вы можете:
            - Добавлять новые продукты
            - Редактировать и удалять свои продукты
            - Просматривать блог
            - Оставлять комментарии

            С уважением,
            Команда Skystore
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")


class UserLoginView(LoginView):
    """Авторизация пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('catalog:product_list')

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().email}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """Выход из системы"""
    next_page = reverse_lazy('catalog:product_list')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя"""
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context