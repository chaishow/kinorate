from profiles.signals import create_user_profile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Пересоздаёт профили для всех пользователей без профиля'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        profiles_recreated = 0

        for user in User.objects.all():
            user.profile.delete()
            create_user_profile(instance=user, created=True)
            profiles_recreated += 1

        self.stdout.write(self.style.SUCCESS(f'Пересозданно профилей: {profiles_recreated}'))

