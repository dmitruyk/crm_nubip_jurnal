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


# class PartnerInfo(CoreModel):
#     class Meta:
#         db_table = u'partner_info'
#
#     user = models.ForeignKey(
#         User,
#         related_name='partner_info_user',
#         on_delete=models.CASCADE
#     )
#
#     name = models.CharField(_('name'), max_length=100, null=True, blank=True, default=None)
#
#     contract_number = models.CharField(_('contract_number'), max_length=20)


# class CreditOrganizationInfo(CoreModel):
#     class Meta:
#         db_table = u'credit_organization_info'
#
#     user = models.OneToOneField(
#         User,
#         related_name='partner_info_credit_org',
#         on_delete=models.CASCADE
#     )
#
#     name = models.CharField(_('name'), max_length=100, null=True, blank=True, default=None)
#
#     contract_number = models.CharField(_('contract_number'), max_length=20)


# class Offer(CoreModel):
#     class Meta:
#         db_table = u'offer'
#
#     KINDS = (
#         ('companies', 'Companies'),
#         ('products', 'Products')
#     )
#
#     user = models.ForeignKey(
#         User,
#         related_name='user_offer_set',
#         on_delete=models.CASCADE
#     )
#
#     TYPES = (
#         ('need', 'NEED'),
#         ('mortgage', 'MORTGAGE'),
#         ('car_loan', 'CAR LOAN'),
#     )
#
#     uuid = models.UUIDField(default=uuid4, editable=False)
#
#     start_rotation = models.DateField(_('start_rotation'), default=None, null=False, blank=False)
#
#     end_rotation = models.DateField(_('start_rotation'), default=None, null=False, blank=False)
#
#     name = models.CharField(_('name'), max_length=100, null=True, blank=True, default=None)
#
#     type = models.CharField(_('type'), choices=TYPES, null=False, max_length=10, blank=False)
#
#     min_scoring_score = models.PositiveIntegerField(_('min_scoring_score'), default=0)
#
#     max_scoring_score = models.PositiveIntegerField(_('max_scoring_score'), default=0)
#
#     credit_organization = models.ForeignKey(CreditOrganizationInfo,
#                                             on_delete=models.CASCADE,
#                                             null=False,
#                                             blank=False,
#                                             )


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


class UserProfile(CoreModel):
    class Meta:
        db_table = u'customer_profile_set'

    uuid = models.UUIDField(default=uuid4, editable=False)

    first_name = models.CharField(_('customer_first_name'), null=False, max_length=200, blank=False)

    last_name = models.CharField(_('customer_last_name'), null=False, max_length=200, blank=False)

    add_name = models.CharField(_('customer_add_name'), null=True, max_length=200, blank=True)

    date_of_birth = models.DateField(_('date_of_birth'), default=None, null=False, blank=False)

    passport = models.OneToOneField(
        Passport,
        related_name='contact_info',
        on_delete=models.SET_NULL,
        null=True
    )

    phone_number = models.OneToOneField(
        PhoneNumber,
        related_name='contact_info',
        on_delete=models.SET_NULL,
        null=True
    )

    scoring_score = models.PositiveIntegerField(_('scoring_score'), default=0)

    # partner = models.ForeignKey(PartnerInfo,
    #                             on_delete=models.CASCADE,
    #                             null=False,
    #                             blank=False,
    #                             )

    @property
    def name(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name,
                                  self.last_name)
        elif self.first_name:
            return '{}'.format(self.first_name)
        else:
            return None

    # TODO add more fields in dic
    def as_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


# class Application(CoreModel):
#     class Meta:
#         db_table = u'application'
#
#     STATUS = (
#         ('new', 'New'),
#         ('sent', 'Sent'),
#         ('received', 'Received'),
#         ('approved', 'Approved'),
#         ('refused', 'Refused'),
#         ('issued', 'Isued'),
#     )
#
#     creation_date = models.DateField(_('creation_date'), default=None, null=False, blank=False)
#
#     send = models.DateField(_('creation_date'), default=None, null=True, blank=True)
#
#     customer = models.ForeignKey(
#         CustomerProfile,
#         related_name='ap_customer',
#         on_delete=models.CASCADE
#     )
#
#     offer = models.ForeignKey(
#         Offer,
#         related_name='ap_offer',
#         on_delete=models.CASCADE
#     )
#
#     status = models.CharField(_('type'), choices=STATUS, null=True, blank=True, max_length=10, default='new')
#
#     # TODO add more fields in dic
#     def as_dict(self):
#         return {
#             'creation_date': self.creation_date,
#             'send': self.send,
#             'customer': self.customer,
#             'offer': self.offer,
#             'status': self.status,
#
#         }

class AcademicGroup(CoreModel):
    class Meta:
        verbose_name_plural = "Академічні групи"

    name = models.CharField(null=False, blank=False, max_length=25, default=None, verbose_name='Назва')
    #member = models.ForeignKey(User, null=True, blank=True,default=None, on_delete=models.DO_NOTHING, verbose_name='Учасник')

    def __str__(self):
        return self.name


class MemberGroup(CoreModel):
    class Meta:
        verbose_name_plural = "Учасники"
        unique_together = ('member_group', 'member_user',)

    member_group = models.ForeignKey(AcademicGroup, null=True, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name='Учасник')
    member_user = models.ForeignKey(User, null=True, blank=True,default=None, on_delete=models.DO_NOTHING, verbose_name='Учасник')


# class Lesson(CoreModel):
#     class Meta:
#         verbose_name = 'Пара'
#         verbose_name_plural = 'Пары'
#
#     name = models.CharField(null=False, blank=False, max_length=25, default=None, verbose_name='Назва')
#
#     academic_group = models.ForeignKey(AcademicGroup, blank=True, default=None, on_delete=models.DO_NOTHING, verbose_name='Академічна група')


class Event(models.Model):
    name = models.CharField(null=True, blank=True, max_length=25, default=None, verbose_name='Назва предмету')
    academic_group = models.ForeignKey(AcademicGroup, null=True, blank=True, default=None, on_delete=models.DO_NOTHING,
                                       verbose_name='Академічна група')
    day = models.DateField(u'Day of the event', help_text=u'Day of the event')
    start_time = models.TimeField(u'Starting time', help_text=u'Starting time')
    end_time = models.TimeField(u'Final time', help_text=u'Final time')
    notes = models.TextField(u'Textual Notes', help_text=u'Textual Notes', blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

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

    def get_absolute_url(self):
        url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])
        return u'<a href="%s">%s</a>' % (url, str(self.start_time.strftime("%H:%M"))+'-'+str(self.end_time.strftime("%H:%M"))+' '+str(self.name)+' '+str(self.academic_group))

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Ending times must after starting times')

        events = Event.objects.filter(day=self.day, academic_group=self.academic_group)
        if events.exists():
            for event in events:
                if self.check_overlap(event.start_time, event.end_time, self.start_time, self.end_time):
                    raise ValidationError(
                        'There is an overlap with another event: ' + str(event.day) + ', ' + str(
                            event.start_time) + '-' + str(event.end_time))