from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.conf import settings
from .models import BlogPost
from .forms import BlogPostForm


class BlogPostListView(ListView):
    """Список опубликованных статей"""
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        """Выводим только опубликованные статьи"""
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogPostDetailView(DetailView):
    """Детальный просмотр статьи с увеличением счетчика просмотров"""
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Переопределяем get_object для увеличения счетчика просмотров"""
        obj = super().get_object(queryset=queryset)

        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        # Дополнительное задание: отправка поздравления при достижении 100 просмотров
        if obj.views_count >= 7:
            self.send_congratulation_email(obj)

        return obj

    def send_congratulation_email(self, post):
        """Отправка поздравления на почту при достижении 100 просмотров"""
        try:
            subject = f'Поздравление! Статья "{post.title}" достигла 100 просмотров!'
            message = f'''
            Поздравляем! Ваша статья "{post.title}" набрала 100 просмотров!

            Заголовок: {post.title}
            Просмотров: {post.views_count}
            Дата создания: {post.created_at}

            Продолжайте в том же духе!
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],  # Укажите email в settings.py
                fail_silently=True,  # Не прерываем выполнение при ошибке отправки
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            print(f"Ошибка отправки email: {e}")


class BlogPostCreateView(CreateView):
    """Создание новой статьи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blog:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать статью'
        context['button_text'] = 'Создать'
        return context


class BlogPostUpdateView(UpdateView):
    """Редактирование статьи"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def get_success_url(self):
        """После успешного редактирования перенаправляем на просмотр статьи"""
        return reverse_lazy('blog:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать статью'
        context['button_text'] = 'Сохранить'
        return context


class BlogPostDeleteView(DeleteView):
    """Удаление статьи"""
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:list')