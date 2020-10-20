from uuid import uuid4
from django.db import models


class CoreQuerySet(models.QuerySet):
    pass


class CoreManager(models.Manager):
    pass


class CoreModel(models.Model):

    objects = CoreManager()

    id = models.UUIDField(primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = "created"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid4()
        super(CoreModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)
