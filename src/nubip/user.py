from django.conf import settings
from django.db import models as db_models
from django.contrib.auth import models
from django.utils.translation import ugettext_lazy as _
from .core.core import CoreModel
from django.contrib.auth.base_user import BaseUserManager


# TODO Add more fields to model User
class UserManager(models.UserManager, BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(CoreModel, models.AbstractUser):
    class Meta:
        db_table = u'user'
        verbose_name_plural = "Користувачі"

    objects = UserManager()

    ROLES = (
        ('student', 'Студент'),
        ('headman', 'Староста'),
        ('curator', 'Куратор'),
        ('teacher', 'Викладач'),
        ('head_department', 'Завідувач кафедри'),
        ('head_assistant', 'Заступник директора'),
        ('head', 'Директор'),
        ('admin', 'Admin')
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

    role = db_models.CharField(_('role'), choices=ROLES, null=False, max_length=20, blank=False)

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
        return '{}'.format(self.name)

    def is_admin(self):
            return self.role in ('partner', 'super')

    def is_client(self):
            return self.role in ('company', 'partner')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.contrib.auth.models import Group
        self.groups.clear()
        if self.role:
            try:
                my_group = Group.objects.get(name=self.role)
                my_group.user_set.add(self)
            except:
                raise Exception(f'Group for role {self.role} not found!')
