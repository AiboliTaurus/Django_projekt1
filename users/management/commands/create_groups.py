# users/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Создает группы модераторов и контент-менеджеров'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Начинаем создание групп...'))

        self.create_moderator_group()
        self.create_content_manager_group()

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('ГРУППЫ УСПЕШНО СОЗДАНЫ!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))

    def create_moderator_group(self):
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if created:
            self.stdout.write('✓ Создана группа "Модератор продуктов"')
        else:
            self.stdout.write('✓ Группа "Модератор продуктов" уже существует, обновляем права')

        product_content_type = ContentType.objects.get_for_model(Product)

        permissions = Permission.objects.filter(
            content_type=product_content_type,
            codename__in=[
                'can_unpublish_product',
                'delete_product',
            ]
        )

        for perm in permissions:
            moderator_group.permissions.add(perm)
            self.stdout.write(f'  └─ Добавлено право: {perm.codename}')

    def create_content_manager_group(self):
        content_group, created = Group.objects.get_or_create(name='Контент-менеджер')

        if created:
            self.stdout.write('✓ Создана группа "Контент-менеджер"')
        else:
            self.stdout.write('✓ Группа "Контент-менеджер" уже существует, обновляем права')

        blog_content_type = ContentType.objects.get_for_model(BlogPost)

        permissions = Permission.objects.filter(
            content_type=blog_content_type
        )

        for perm in permissions:
            content_group.permissions.add(perm)
            self.stdout.write(f'  └─ Добавлено право: {perm.codename}')
