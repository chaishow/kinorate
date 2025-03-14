from django.db import models, IntegrityError

class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    img_url = models.URLField(null=True, blank=True)

    @classmethod
    def from_json_dict(cls, json):
        obj = cls()
        for key, value in json.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    @classmethod
    def get_or_create_from_data(cls, data):
        search_fields = {
            'title': data.get('title'),
            'year': data.get('year'),
        }

        another_fields = {
            'description': data.get('description'),
            'img_url': data.get('img_url')
        }

        return cls.objects.get_or_create(
            **search_fields,
            defaults=another_fields
        )

    def __str__(self):
        return str(self.__dict__)


class Collection(models.Model):
    profile = models.ForeignKey('profiles.Profile',
                                on_delete=models.CASCADE,
                                related_name='collections')
    name = models.CharField(max_length=200, blank=False, null=False)
    films = models.ManyToManyField(Film, related_name='collections')
    is_system = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Rate(models.Model):
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    rate = models.IntegerField(null=True, default=None)

    def __str__(self):
        return str(self.rate)