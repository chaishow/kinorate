from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from collection.models import Collection
from collection.constants import defaults


@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        Collection.objects.create(
            profile=profile,
            name=defaults.DEFAULT_COLLECTION_NAME,
            is_system=True,
            )

        Collection.objects.create(
            profile=profile,
            name=defaults.DEFAULT_RATED_COLLECTION_NAME,
            is_system=True,
            )
