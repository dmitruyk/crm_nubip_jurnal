import os
import time
from .core.core import CoreModel
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

from django.db import models, transaction
from django.db.models import Q
from .user import User

from django.core.exceptions import ValidationError


from django.http import HttpResponse
from django.urls import reverse

from django.conf import settings


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

    name = models.CharField(max_length=500,
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
        ordering = ["name"]

    COURSE = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4')
    )

    name = models.CharField(null=False,
                            blank=False,
                            max_length=500,
                            default=None,
                            verbose_name='Шифр групи')

    course = models.CharField(
        null=True,
        blank=True,
        default=None,
        max_length=32,
        choices=COURSE,
        verbose_name='Курс'
    )

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

    graduation = models.BooleanField(_('graduation'), null=True, blank=True, default=False)

    graduation_date = models.DateField(verbose_name='Дата закінчення навчання',
                                       help_text=u'Місяць число рік',
                                       null=True,
                                       blank=True,
                                       default=None,
                                       )

    def clean(self):
        if self.curator:
            if self.curator.role not in ['teacher', 'curator', 'head_department']:
                raise ValidationError('Куратором може бути тількт користувач з роллю Куратор або Викладач!')

    def __str__(self):
        return self.name


class LectureName(CoreModel):

    class Meta:
        verbose_name_plural = "Перелік дисциплін"
        ordering = ["name"]

    name = models.CharField(null=True,
                            blank=True,
                            max_length=500,
                            default=None,
                            verbose_name='Назва предмету')

    def __str__(self):
        return f'{self.name}'


class TutorName(CoreModel):
    class Meta:
        verbose_name_plural = "Викладач"

    teacher = models.ForeignKey(User,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Викладач')

    lecture = models.ForeignKey(LectureName,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Дисципліна')


class Lecture(CoreModel):

    class Meta:
        verbose_name_plural = "Порядок занять"

    name = models.CharField(null=True,
                            blank=True,
                            max_length=500,
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


    day = models.DateField(verbose_name='Дата проведення', help_text=u'Місяць число рік', )
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

        if hasattr(self, 'user'):
            if ReportUserEvent.objects.filter(report_event=self, report_creator=self.user).exists():
                html = f'<html><body>Report for {self.lecture}, created by {self.user} already exists!</body></html>'
                return HttpResponse(html)

    def clean(self):
        pass

    def easy_save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @transaction.atomic
    def save(self, *args, **kwargs):
        sid = transaction.savepoint()
        try:
            if ReportUserEvent.objects.filter(report_event=self, report_creator=self.user,).exists():
                raise ValidationError(f'Звіт для {self.lecture}, від {self.user} вже подано! ')
            else:
                if self.frequency_parameter == '1':
                    if self.user.is_superuser:
                        if Event.objects.filter(academic_group=self.academic_group,
                                                index_number=self.index_number,
                                                day=self.day,
                                                ).exists():
                            raise ValidationError(f'Заняття з таким порядковим номером {self.index_number} '
                                                  f'для групи {self.academic_group} '
                                                  f'дата {self.day} вже існує!')
                    super().save(*args, **kwargs)
                    if self.academic_group and self.user.is_superuser:
                        UserEvent.objects.filter(event=self).delete()
                        students = MemberGroup.objects.filter(member_group=self.academic_group).\
                            filter(~Q(member_user__deducted=True))
                        for student in students:
                            user = UserProfile.objects.filter(user__id=student.member_user.id).first()
                            if user:

                                g, _ = UserEvent.objects.update_or_create(event=self, user=user)

                    else:
                        print('333333333')
                        user_events = UserEvent.objects.filter(event=self).first()
                        new_event_report = ReportUserEvent(report_event=self,
                                                           report_creator=self.user)
                        new_event_report.save()
                        #user_events.save()

                        # for event in user_events:
                        #
                        #     ReportDataEvent.objects.create(
                        #          report_data_user_data=new_event_report,
                        #          report_user=event.user.user,
                        #          user_event_creator=self.user
                        #          )


                        # user_events.presence = False
                        # user_events.reason = None
                        # user_events.additional_info = None
                        # user_events.save()


                        # UserEvent.objects.filter(event=self).update(presence=False,
                        #                                            reason=None,
                        #                                            additional_info=None)
                elif self.frequency_parameter == '2':
                    if self.end_date == '':
                        raise ValidationError('Поле кінцевої дати при такій періодичності не може бути пустим!')
                    event_day = self.day
                    last_event_day = datetime.strptime(self.end_date, "%Y-%m-%d").date()
                    week_day = event_day.strftime("%a")
                    week_number = event_day.isocalendar()[1]

                    end_week_number = last_event_day.isocalendar()[1]

                    for w in range(week_number, end_week_number+1, 1):
                        __event_day = datetime.strptime(f'{event_day.year}-{w}-{week_day}', "%Y-%W-%a").date()

                        if Event.objects.filter(academic_group=self.academic_group,
                                                index_number=self.index_number,
                                                day=__event_day,
                                                ).exists():
                            raise ValidationError(f'Заняття з таким порядковим номером {self.index_number} '
                                                  f'для групи {self.academic_group} на {__event_day} вже існує!')

                        if self.academic_group and self.user.is_superuser:
                            __event = Event(lecture=self.lecture,
                                            academic_group=self.academic_group,
                                            index_number=self.index_number,
                                            day=__event_day)

                            __event.user = self.users
                            __event.easy_save()

                            students = MemberGroup.objects.filter(member_group=self.academic_group).\
                                filter(~Q(member_user__deducted=True))

                            for student in students:
                                user = UserProfile.objects.filter(user__id=student.member_user.id).first()
                                if user:
                                    g, _ = UserEvent.objects.update_or_create(event=__event, user=user)

                        if settings.DEBUG:
                            print(week_number, w, __event_day, __event, g, _)

                elif self.frequency_parameter == '3':
                    if self.end_date == '':
                        raise ValidationError('Поле кінцевої дати при такій періодичності не може бути пустим!')
                    event_day = self.day
                    last_event_day = datetime.strptime(self.end_date, "%Y-%m-%d").date()
                    week_day = event_day.strftime("%a")
                    week_number = event_day.isocalendar()[1]

                    end_week_number = last_event_day.isocalendar()[1]

                    for w in range(week_number, end_week_number+1, 2):
                        __event_day = datetime.strptime(f'{event_day.year}-{w}-{week_day}', "%Y-%W-%a").date()

                        if Event.objects.filter(academic_group=self.academic_group,
                                                index_number=self.index_number,
                                                day=__event_day,
                                                ).exists():
                            raise ValidationError(f'Заняття з таким порядковим номером {self.index_number} '
                                                  f'для групи {self.academic_group} на {__event_day} вже існує!')

                        if self.academic_group and self.user.is_superuser:
                            __event = Event(lecture=self.lecture,
                                            academic_group=self.academic_group,
                                            index_number=self.index_number,
                                            day=__event_day)

                            __event.user = self.users
                            __event.easy_save()

                            students = MemberGroup.objects.filter(member_group=self.academic_group).\
                                filter(~Q(member_user__deducted=True))

                            for student in students:
                                user = UserProfile.objects.filter(user__id=student.member_user.id).first()
                                if user:
                                    g, _ = UserEvent.objects.update_or_create(event=__event, user=user)

                        if settings.DEBUG:
                            print(week_number, w, __event_day, __event, g, _)

                        #print(date(event_day.year, 1, 1) + relativedelta(weeks=w))

                    print(event_day, week_day, week_number, end_week_number, '<+++++++++')
                else:
                    raise Exception(f'For parameter: {self.frequency_parameter} method not implemented!')
            transaction.savepoint_commit(sid)
        except Exception as e:
            transaction.savepoint_rollback(sid)
            raise Exception(e)


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
            return '{} {}'.format(self.user.last_name,
                                  self.user.first_name)
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
        ('home', 'Сімейні обставини'),
        ('other', 'Інше')
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

    user_event_creator = models.ForeignKey(User,
                                           related_name='user_event_creator',
                                           null=True,
                                           blank=True,
                                           default=None,
                                           on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.user} -> {self.event.lecture.name}'

    def is_presence(self):
        if self.presence and self.reason:
            return True

    def is_not_presence(self):
        if not self.presence and not self.reason:
            return True

    def is_important(self):
        if not self.presence and self.reason == 'important' and not self.additional_info:
            return True

    def is_other(self):
        if not self.presence and self.reason == 'other' and not self.additional_info:
            return True

    def clean(self):
        if self.is_presence():
            raise ValidationError(f'Виберіть, будь ласка, один статус для {self.user}!')

        if self.is_not_presence():
            raise ValidationError(f'Вкажіть, будь ласка, причину вітсутності для {self.user}!')

        if self.is_important():
            raise ValidationError(f'Додайте додаткову інформацію про поважну причину для {self.user}!')

        if self.is_other():
            raise ValidationError(f'Додайте додаткову інформацію про причину вітсутності для {self.user}!')

    def save(self, *args, **kwargs):
        try:
            print(1, self.user, 'kkkkkk', 'ooo')
            if self.request_user:
                print(2)
                report_event = ReportUserEvent.objects.filter(report_event=self.event, report_creator=self.request_user).first()
        #        print(self.request)
                if ReportDataEvent.objects.filter(report_data_user_data=report_event,
                                                  report_user=self.user.user,
                                                  user_event_creator=self.request_user).exists():
                    print(3)

                    pass
                else:
                    print(4)
                    super().save(*args, **kwargs)
                    print(5)
                    ReportDataEvent.objects.create(report_data_user_data=report_event,
                                                   report_user=self.user.user,
                                                   user_event_creator=self.request_user,
                                                   report_presence=self.presence,
                                                   report_reason=self.reason,
                                                   report_additional_info=self.additional_info,
                                                   protected=True
                    )

                    UserEvent.objects.filter(pk=self.id).update(presence=False,
                                                                reason=None,
                                                                additional_info=None,
                                                                )
        except Exception as e:
            print('exeption')
            super().save(*args, **kwargs)


class ReportUserEvent(CoreModel):

    class Meta:
        verbose_name_plural = "Звіти"

    report_event = models.ForeignKey(Event,
                                     related_name='report_event',
                                     verbose_name='Дисципліна',
                                     null=True,
                                     blank=True,
                                     default=None,
                                     on_delete=models.DO_NOTHING)

    report_creator = models.ForeignKey(User,
                                       related_name='report_creator',
                                       verbose_name='Звіт створив',
                                       null=True,
                                       blank=True,
                                       default=None,
                                       on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Звіт {self.report_event}'


class ReportDataEvent(CoreModel):

    class Meta:
        verbose_name_plural = "Дані звітів"

    TYPES = (
        ('sickness', 'Хворіє'),
        ('important', 'Поважна'),
        ('home', 'Сімейні обставини'),
        ('other', 'Інше')
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

    protected = models.BooleanField(default=False)

    user_event_creator = models.ForeignKey(User,
                                           related_name='report_user_event_creator',
                                           null=True,
                                           blank=True,
                                           default=None,
                                           on_delete=models.DO_NOTHING)


class AbstractModel(Event):
    class Meta:
        verbose_name_plural = "Звіт"

    def __str__(self):
        return f'{self.name}'


class ReportModel(CoreModel):
    day = models.DateField(u'Дата проведення', help_text=u'Місяць число рік')

    class Meta:
        verbose_name_plural = "Зведений Звіт"



class GroupEventCreation(CoreModel):
    class Meta:
        abstract = True

    academic_group = models.ForeignKey(AcademicGroup,
                                       null=True,
                                       blank=True,
                                       default=None,
                                       on_delete=models.DO_NOTHING,
                                       verbose_name='Академічна група')

    day = models.DateField(u'Дата проведення', help_text=u'Рік місяць число')


class FGroupEventCreation(CoreModel):
    class Meta:
        abstract = True
    lecture = models.ForeignKey(LectureName,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.DO_NOTHING,
                                verbose_name='Назва предмету')

    index_number = models.ForeignKey(Lecture,
                                     null=True,
                                     blank=True,
                                     default=None,
                                     on_delete=models.DO_NOTHING,
                                     verbose_name='Заняття за розкладом')


class GEV(GroupEventCreation):
    pass
    # gev_event =  models.ForeignKey(Event,
    #                                 related_name='report_user_gev',
    #                                 null=True,
    #                                 blank=True,
    #                                 default=None,
    #                                 on_delete=models.DO_NOTHING)



    def answer(self):
        return self.user

    def __str__(self):
        return 'self.gev_event'


class FGEV(FGroupEventCreation):
    gev_event =  models.ForeignKey(GEV,
                                    related_name='report_user_gev',
                                    null=True,
                                    blank=True,
                                    default=None,
                                    on_delete=models.DO_NOTHING)