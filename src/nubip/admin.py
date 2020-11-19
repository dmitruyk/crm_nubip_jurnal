import datetime
import calendar
from django.urls import reverse
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from .utils.calendar import EventCalendar

from urllib.parse import urlencode
from django.shortcuts import redirect

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm, PasswordInput
from django.contrib.auth.hashers import make_password

from .models import *


@admin.register(MemberGroup)
class MemberGroupAdmin(admin.ModelAdmin):
    list_display = ['member_group', 'member_user', 'get_role']

    def get_role(self, obj):
        return obj.member_user.role


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
    # list_display = ['member_group', 'member_user', 'get_role']
    #
    # def get_role(self, obj):
    #     return obj.member_user.role


class MemberGroupInline(admin.TabularInline):
    model = MemberGroup
    extra = 1
    ordering = ['-created']


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    ordering = ['-created']

# @admin.register(PartnerInfo)
# class PartnerInfoAdmin(admin.ModelAdmin):
#     pass


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    inlines = [
            MemberGroupInline,
            # ChargeBoxActionInline,
            # ChargePointActionInline
        ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'role']

# @admin.register(AbstractModel)
# class AbstractModelAdmin(admin.ModelAdmin):
#     list_display = ['name', 'academic_group', 'day']
#     list_filter = ('academic_group',)
#     date_hierarchy = 'date'



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'notes', 'students']
    date_hierarchy = 'day'
    inlines = [
            UserProfileInline,
            # ChargeBoxActionInline,
            # ChargePointActionInline
        ]
    readonly_fields = ('students',)
    # fieldsets = [
    #     (None,               {'fields': ['name']}),
    #     ('Date information', {'fields': ['students'], 'classes': ['notes']}),
    # ]

    def students(self, obj):
        return obj.students()

    def user(self, obj):
        return obj.users()


    # fieldsets = [
    #     (None,               {'fields': ['name']}),
    #     ('Date information', {'fields': ['academic_group'], 'classes': ['notes']}),
    # ]

    def changelist_view(self, request, extra_context=None):
        if request.GET:
            return super().changelist_view(request, extra_context=extra_context)

        date = datetime.date.today()
        params = ['day', 'month', 'year']
        field_keys = ['{}__{}'.format(self.date_hierarchy, i) for i in params]
        field_values = [getattr(date, i) for i in params]
        query_params = dict(zip(field_keys, field_values))
        url = '{}?{}'.format(request.path, urlencode(query_params))
        return redirect(url)
    #change_list_template = 'admin/events/change_list.html'

    # def changelist_view(self, request, extra_context=None):
    #     after_day = request.GET.get('day__gte', None)
    #     extra_context = extra_context or {}
    #
    #     if not after_day:
    #         d = datetime.date.today()
    #     else:
    #         try:
    #             split_after_day = after_day.split('-')
    #             d = datetime.date(year=int(split_after_day[0]), month=int(split_after_day[1]), day=1)
    #         except:
    #             d = datetime.date.today()
    #
    #     previous_month = datetime.date(year=d.year, month=d.month, day=1)  # find first day of current month
    #     previous_month = previous_month - datetime.timedelta(days=1)  # backs up a single day
    #     previous_month = datetime.date(year=previous_month.year, month=previous_month.month,
    #                                    day=1)  # find first day of previous month
    #
    #     last_day = calendar.monthrange(d.year, d.month)
    #     next_month = datetime.date(year=d.year, month=d.month, day=last_day[1])  # find last day of current month
    #     next_month = next_month + datetime.timedelta(days=1)  # forward a single day
    #     next_month = datetime.date(year=next_month.year, month=next_month.month,
    #                                day=1)  # find first day of next month
    #
    #     extra_context['previous_month'] = reverse('admin:nubip_event_changelist') + '?day__gte=' + str(
    #         previous_month)
    #     extra_context['next_month'] = reverse('admin:nubip_event_changelist') + '?day__gte=' + str(next_month)
    #
    #     cal = EventCalendar()
    #     html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
    #     html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')
    #     extra_context['calendar'] = mark_safe(html_calendar)
    #     return super(EventAdmin, self).changelist_view(request, extra_context)




# @admin.register(CreditOrganizationInfo)
# class CreditOrganizationInfoAdmin(admin.ModelAdmin):
#     pass
#
# @admin.register(Offer)
# class OfferAdmin(admin.ModelAdmin):
#     pass
#
# @admin.register(CustomerProfile)
# class CustomerProfileAdmin(admin.ModelAdmin):
#     pass
#
# @admin.register(Application)
# class ApplicationAdmin(admin.ModelAdmin):
#     pass

# @admin.register(Passport)
# class PassportAdmin(admin.ModelAdmin):
#     pass
#
# @admin.register(PhoneNumber)
# class PhoneNumberAdmin(admin.ModelAdmin):
#     pass

# Register your models here.

# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     form = ClientForm
#     list_display = ('api_key', 'login')
#     ordering = ['created']
#     inlines = [
#         ProductInline,
#         # ChargeBoxActionInline,
#         # ChargePointActionInline
#     ]
#     # search_fields = ('phone_number', 'email', 'first_name', 'last_name')
#     # list_filter = ('country', 'organization', 'is_active')