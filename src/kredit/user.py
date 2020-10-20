from django.conf import settings
from django.db import models as db_models
from django.contrib.auth import models
from django.utils.translation import ugettext_lazy as _
from .core.core import CoreModel


# TODO Add more fields to model User
class UserManager(models.UserManager):
    pass


class User(CoreModel, models.AbstractUser):
    class Meta:
        db_table = u'user'

    objects = UserManager()

    ROLES = (
        ('company', 'Company'),
        ('partner', 'Partner'),
        ('super', 'Super')
    )

    TURN_FORMS = (
        ('mr', 'Mr'),
        ('ms', 'Ms'),
        ('miss', 'Miss'),
        ('mrs', 'Mrs')
    )

    turn_form = db_models.CharField(_('Turn form'), choices=TURN_FORMS,
                                    max_length=5, null=True, blank=True)

    LANG_FORMS = (
        ('en', 'ENG'),
        ('ru', 'РУС'),
        ('ua', 'УКР'),
    )

    lang_form = db_models.CharField(_('Lang form'), choices=LANG_FORMS,
                                    max_length=5, null=True, blank=True)

    role = db_models.CharField(_('role'), choices=ROLES, null=False, max_length=10, blank=False)

    @property
    def name(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name,
                                  self.last_name)
        elif self.first_name:
            return '{}'.format(self.first_name)
        else:
            return None

    def __str__(self):
        return '{}'.format(self.username)

    def is_admin(self):
            return self.role in ('partner', 'super')

    def is_client(self):
            return self.role in ('company', 'partner')