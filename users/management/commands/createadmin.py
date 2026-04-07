from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.create(
            email = 'admin@gamil.com',
            first_name = 'admin',
            last_name = 'admin',
        )

        user.set_password('1234')

        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(self.style.SUCCESS(f'Успешно создан пользователь admin с email {user.email}!'))