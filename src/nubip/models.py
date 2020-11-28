import os
import time
from .core.core import CoreModel
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta

from django.db import models, transaction
from .user import User

from django.core.exceptions import ValidationError
from django.urls import reverse


class APIKey(CoreModel):
    name = models.CharField(null=False, blank=False, max_length=25, default=None)
    uuid = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.name


class APIClient(CoreModel):

    class Meta:
        db_table = u'api_client'

    uuid = models.UUIDField(default=uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name='api_user_client',
        on_delete=models.CASCADE
    )
    login = models.CharField(null=False, blank=False, max_length=25)
    password = models.CharField(max_length=512, default=None, blank=True, null=True)
    api_key = models.ForeignKey(APIKey,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True,
                                default=None,
                                )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.login


class Passport(CoreModel):
    class Meta:
        db_table = u'passport'

    number = models.CharField(_('number'), max_length=20, null=True, blank=True)

    issue_date = models.DateField(_('issue date'), null=True, blank=True)


class PhoneNumber(CoreModel):
    class Meta:
        db_table = u'phone_number'

    TYPES = (
        ('main', 'Main'),
        ('work', 'Work'),
        ('home', 'Home'),
        ('other', 'Other')
    )

    country_code = models.CharField(_('country_code'), max_length=3,
                                    null=True, blank=True)

    area_code = models.CharField(_('area_code'), max_length=5,
                                 null=True, blank=True)

    number = models.CharField(_('number'), max_length=20, null=True, blank=True)

    type = models.CharField(_('type'), choices=TYPES, max_length=5, null=True, blank=True, default='main')


class Department(CoreModel):

    class Meta:
        verbose_name_plural = "Кафери"
        unique_together = ('name', 'head')

    name = models.CharField(max_length=30,
                            null=True,
                            blank=True,
                            default=None,
                            verbose_name='Назва кафедри')

    head = models.ForeignKey(User,
                             related_name='department_head',
                             null=True,
                             blank=True,
                             default=None,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Завідувач кафедри')

    def clean(self):
        if self.head.role != 'head_department':
            raise ValidationError('Завідувачем може бути тількт користувач з роллю Завідувач кафедри!')

    def __str__(self):
        return self.name


class AcademicGroup(CoreModel):
    class Meta:
        verbose_name_plural = "Академічні групи"

    name = models.CharField(null=False,
                            blank=False,
                            max_length=25,
                            default=None,
                            verbose_name='Шифр групи')

    curator = models.ForeignKey(User,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Куратор')

    department = models.ForeignKey(Department,
                                   null=True,
                                   blank=True,
                                   default=None,
                                   on_delete=models.DO_NOTHING,
                                   verbose_name='Базова каферда')

    def clean(self):
        if self.curator:
            if self.curator.role != 'curator':
                raise ValidationError('Куратором може бути тількт користувач з роллю Куратор!')

    def __str__(self):
        return self.name


class LectureName(CoreModel):

    class Meta:
        verbose_name_plural = "Предмет"
        unique_together = ('name', 'teacher',)

    name = models.CharField(null=True,
                            blank=True,
                            max_length=25,
                            default=None,
                            verbose_name='Назва предмету')

    teacher = models.ForeignKey(User,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Викладач')

    def clean(self):
        if self.teacher.role != 'teacher':
            raise ValidationError('Викладачем може бути тількт користувач з роллю Викладач!')

    def __str__(self):
        return f'Предмет: {self.name}. Викладач: {self.teacher}'


class Lecture(CoreModel):

    class Meta:
        verbose_name_plural = "Порядок занять"

    name = models.CharField(null=True,
                            blank=True,
                            max_length=25,
                            default=None,
                            verbose_name='Номер по порядку')

    def __str__(self):
        return self.name


class MemberGroup(CoreModel):

    class Meta:
        verbose_name_plural = "Члени групи"
        unique_together = ('member_group', 'member_user',)

    member_group = models.ForeignKey(AcademicGroup,
                                     null=True,
                                     blank=True,
                                     default=None,
                                     on_delete=models.DO_NOTHING,
                                     verbose_name='Група Учасника')

    member_user = models.ForeignKey(User,
                                    null=True,
                                    blank=True,
                                    default=None,
                                    on_delete=models.DO_NOTHING,
                                    verbose_name='Учасник')


class Event(models.Model):

    lecture = models.ForeignKey(LectureName,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Назва предмету')

    academic_group = models.ForeignKey(AcademicGroup,
                                       null=True,
                                       blank=True,
                                       default=None,
                                       on_delete=models.DO_NOTHING,
                                       verbose_name='Академічна група')

    index_number = models.ForeignKey(Lecture,
                                     null=True,
                                     blank=True,
                                     default=None,
                                     on_delete=models.DO_NOTHING,
                                     verbose_name='Заняття за розкладом')


    day = models.DateField(u'Day of the event', help_text=u'Day of the event')
    #start_time = models.TimeField(u'Starting time', help_text=u'Starting time')
    #end_time = models.TimeField(u'Final time', help_text=u'Final time')
    notes = models.TextField(u'Textual Notes', help_text=u'Textual Notes', blank=True, null=True)

    def __str__(self):
        return f'{self.lecture}'

    def students(self):
        member_group = MemberGroup.objects.filter(member_group=self.academic_group)

        return '33', '44'

    def users(self):

        return User.objects.all()

    def _is_rapport_exists(self):
        if ReportUserEvent.objects.filter(report_event=self).exists():
            return True
        return False
    _is_rapport_exists.boolean = True
    is_rapport_exists = property(_is_rapport_exists)

    class Meta:
        verbose_name = 'Розклад'
        verbose_name_plural = 'Розклад занять'

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (
                new_end >= fixed_start and new_end <= fixed_end):  # innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True

        return overlap

    # def get_absolute_url(self):
    #     url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
    #     return u'<a href="%s">%s</a>' % (url, str(self.start_time.strftime("%H:%M"))+'-'+str(self.end_time.strftime("%H:%M"))+' '+str(self.name)+' '+str(self.academic_group))

    # def clean(self):
    #     if self.end_time <= self.start_time:
    #         raise ValidationError('Ending times must after starting times')

        from django.http import HttpResponse
        if hasattr(self, 'user'):
            if ReportUserEvent.objects.filter(report_event=self, report_creator=self.user).exists():
                html = f'<html><body>Report for {self.lecture}, created by {self.user} already exists!</body></html>'
                print('ppp')
                return HttpResponse(html)
                #raise ValidationError(f'Report for {self.name}, created by {self.user} already exists! ')

        # if ReportUserEvent.objects.filter(report_event=self).exists():
        #     print(self.user)
        #     raise ValidationError(f'Report for {self.name}, created by {self.user} already exists! ')
        # print('2222')



        # events = Event.objects.filter(day=self.day, academic_group=self.academic_group)
        # if events.exists():
        #     for event in events:
        #         if self.check_overlap(event.start_time, event.end_time, self.start_time, self.end_time):
        #             raise ValidationError(
        #                 'There is an overlap with another event: ' + str(event.day) + ', ' + str(
        #                     event.start_time) + '-' + str(event.end_time))

    def save(self, *args, **kwargs):
        if ReportUserEvent.objects.filter(report_event=self, report_creator=self.user,).exists():
            raise ValidationError(f'Звіт для {self.lecture}, від {self.user} вже подано! ')
        super().save(*args, **kwargs)
        if self.academic_group and self.user.is_superuser:
            UserEvent.objects.filter(event=self).delete()
            students = MemberGroup.objects.filter(member_group=self.academic_group)
            for student in students:
                user = UserProfile.objects.filter(user=student.member_user).first()
                if user is not None:
                    UserEvent.objects.update_or_create(event=self, user=user)
        else:
            user_events = UserEvent.objects.filter(event=self)
            new_event_report = ReportUserEvent.objects.create(report_event=self,
                                                              report_creator=self.user,
                                                              )
            #print(user_events)
            for event in user_events:
                ReportDataEvent.objects.create(
                    report_data_user_data=new_event_report,
                    report_user=event.user.user,
                    )
                # profile = UserProfile.objects.filter(user=event.user.user).first()
                #
                # UserEvent.objects.filter(event=self).update(presence=False,
                #                                                           reason=None,
                #                                                           additional_info=None)


class UserProfile(CoreModel):
    class Meta:
        db_table = u'customer_profile_set'
        verbose_name_plural = "Профайли користувачів"

    user = models.OneToOneField(User, null=True, blank=True, default=None, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.name}'

    @property
    def name(self):
        if self.user.first_name and self.user.last_name:
            return '{} {}'.format(self.user.first_name,
                                  self.user.last_name)
        elif self.user.first_name:
            return '{}'.format(self.user.first_name)
        else:
            return None

    # TODO add more fields in dic
    def as_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class UserEvent(CoreModel):

    TYPES = (
        ('sickness', 'Хворіє'),
        ('important', 'Поважна'),
        ('home', 'Home'),
        ('other', 'Other')
    )

    class Meta:
        verbose_name_plural = "Заняття користувача"
        unique_together = ('event', 'user',)

    event = models.ForeignKey(Event,
                              null=True,
                              blank=True,
                              default=None,
                              on_delete=models.CASCADE,
                              verbose_name='Учасник')

    user = models.ForeignKey(UserProfile,
                             null=True,
                             blank=True,
                             default=None,
                             on_delete=models.DO_NOTHING,
                             verbose_name='Учасник')

    presence = models.BooleanField(default=False,
                                   verbose_name='Присутність')

    reason = models.CharField(choices=TYPES,
                              max_length=30,
                              null=True,
                              blank=True,
                              default=None,
                              verbose_name='Причина відсутності')

    additional_info = models.CharField(null=True,
                                       max_length=200,
                                       blank=True,
                                       verbose_name='Додаткова інформація')

    def save(self, *args, **kwargs):
        report_event = ReportUserEvent.objects.filter(report_event=self.event).first()
        ReportDataEvent.objects.update(
            report_data_user_data=report_event,
            report_user=self.user.user,
            report_presence=self.presence,
            report_reason=self.reason,
            report_additional_info=self.additional_info
        )



class ReportUserEvent(CoreModel):

    class Meta:
        verbose_name_plural = "Звіти"

    report_event = models.ForeignKey(Event,
                                     related_name='report_event',
                                     null=True,
                                     blank=True,
                                     default=None,
                                     on_delete=models.DO_NOTHING)

    report_creator = models.ForeignKey(User,
                                       related_name='report_creator',
                                       null=True,
                                       blank=True,
                                       default=None,
                                       on_delete=models.DO_NOTHING)


class ReportDataEvent(CoreModel):

    class Meta:
        verbose_name_plural = "Дані звітів"

    TYPES = (
        ('sickness', 'Хворіє'),
        ('important', 'Поважна'),
        ('home', 'Home'),
        ('other', 'Other')
        )

    report_data_user_data = models.ForeignKey(ReportUserEvent,
                                              related_name='report_data_user_data',
                                              null=True,
                                              blank=True,
                                              default=None,
                                              on_delete=models.DO_NOTHING)

    report_user = models.ForeignKey(User,
                                    related_name='report_user',
                                    null=True,
                                    blank=True,
                                    default=None,
                                    on_delete=models.DO_NOTHING)

    report_presence = models.BooleanField(default=False)

    report_reason = models.CharField(choices=TYPES,
                                     max_length=30,
                                     null=True,
                                     blank=True,
                                     default=None,
                                     verbose_name='Причина відсутності')

    report_additional_info = models.CharField(null=True,
                                              max_length=200,
                                              blank=True,
                                              verbose_name='Додаткова інформація')


class AbstractModel(Event):
    class Meta:
        verbose_name_plural = "Звіт"

    def __str__(self):
        return f'{self.name}'

