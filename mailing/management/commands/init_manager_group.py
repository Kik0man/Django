from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Recipient, Message, Mailing
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Создать группу "Менеджеры" с необходимыми правами'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')
        if created:
            self.stdout.write('Группа "Менеджеры" создана.')
        else:
            self.stdout.write('Группа уже существует.')

        # Права на просмотр всех объектов
        perms = [
            ('can_view_all_recipients', Recipient),
            ('can_view_all_messages', Message),
            ('can_view_all_mailings', Mailing),
            ('can_disable_mailing', Mailing),
        ]
        for codename, model in perms:
            content_type = ContentType.objects.get_for_model(model)
            perm = Permission.objects.get(codename=codename, content_type=content_type)
            group.permissions.add(perm)

        # Также менеджер может блокировать пользователей (право change_user)
        user_ct = ContentType.objects.get_for_model(CustomUser)
        change_user_perm = Permission.objects.get(codename='change_customuser', content_type=user_ct)
        group.permissions.add(change_user_perm)

        self.stdout.write(self.style.SUCCESS('Права добавлены.'))