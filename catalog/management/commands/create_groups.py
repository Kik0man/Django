from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product

class Command(BaseCommand):
    help = 'Создает группу "Модератор продуктов" и назначает права'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Модератор продуктов')
        if created:
            self.stdout.write('Группа "Модератор продуктов" создана')
        else:
            self.stdout.write('Группа "Модератор продуктов" уже существует')

        # Получаем права
        content_type = ContentType.objects.get_for_model(Product)
        # Право на удаление (стандартное)
        delete_perm = Permission.objects.get(codename='delete_product', content_type=content_type)
        # Кастомное право на отмену публикации
        unpublish_perm = Permission.objects.get(codename='can_unpublish_product', content_type=content_type)

        group.permissions.add(delete_perm, unpublish_perm)
        self.stdout.write(self.style.SUCCESS('Права добавлены: delete_product, can_unpublish_product'))