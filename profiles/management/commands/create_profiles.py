from profiles.signals import create_user_profile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Создаёт профили для всех пользователей без профиля'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users_without_profiles = User.objects.filter(profile__isnull=True)
        profiles_created = 0

        for user in users_without_profiles:
            create_user_profile(instance=user, created=True)
            profiles_created += 1

        self.stdout.write(self.style.SUCCESS(f'Создано профилей: {profiles_created}'))

