import datetime
import calendar
from django.urls import reverse
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from .utils.calendar import EventCalendar

from urllib.parse import urlencode
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm, MyCustomForm
from django.db.models import Count
from django.db.models.query import Q

from .models import *


@admin.register(MemberGroup)
class MemberGroupAdmin(admin.ModelAdmin):
    list_display = ['member_group', 'get_role']

    def get_role(self, obj):
        return None


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportDataEvent)
class ReportDataEventAdmin(admin.ModelAdmin):
    pass


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


class MemberGroupInline(admin.TabularInline):
    model = MemberGroup
    extra = 0
    ordering = ['member_user__last_name']


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    ordering = ['-created']


class UserEventInline(admin.TabularInline):
    model = UserEvent
    extra = 0
    ordering = ['-created']


class ReportDataEventInline(admin.TabularInline):
    model = ReportDataEvent
    extra = 0
    ordering = ['-created']


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [
            MemberGroupInline,
        ]
    list_display = ['name', 'students_count', 'curator', 'department']
    list_filter = ('name',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AcademicGroupAdmin, self).get_search_results(request, queryset, search_term)
        try:
            # search_term_as_int = int(search_term)
            # queryset |= self.model.objects.filter(age=search_term_as_int)
            m_g = MemberGroup.objects.filter(member_user__last_name__icontains=search_term)
            if m_g:
                queryset |= self.model.objects.filter(pk__in=[m.member_group.id for m in m_g])
        except Exception as e :
            raise Exception(e)
        return queryset, use_distinct

    def students_count(self, obj):
        return obj.students_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            students_count=Count('membergroup'),
        )
        return queryset

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('name', 'is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password', 'role', 'user_permissions', 'groups')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('name', 'password1', 'password2', 'is_staff', 'is_active', 'role', 'groups')}
    #     ),
    #  )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(ReportUserEvent)
class ReportUserEventAdmin(admin.ModelAdmin):
    #search_fields = ('member__name', 'group')
    #list_filter = ('member__role',)
    inlines = [
            ReportDataEventInline,
        ]
    list_display = ['report_creator', 'role', 'report_event', 'group', 'count']
    date_hierarchy = 'created'

    def count(self, obj):
        all_users = ReportDataEvent.objects.filter(report_data_user_data=obj).count()
        present_users = ReportDataEvent.objects.filter(report_data_user_data=obj, report_presence=True).count()

        return f'{present_users}/{all_users}'

    def group(self, obj):
        group = None
        if obj.report_creator.role == 'student':
            m_g = MemberGroup.objects.filter(member_user=obj.report_creator).first()
            if m_g:
                group = m_g.member_group.name
        if obj.report_creator.role == 'curator':
            a_g = AcademicGroup.objects.filter(curator=obj.report_creator).first()
            group = a_g.name
        return group

    def role(self, obj):
        return obj.report_creator.role

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            queryset = queryset.filter()
        else:
            queryset = queryset.filter(department__head=request.user)

        return queryset


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = MyCustomForm
    list_display = ['name', 'day']
    date_hierarchy = 'day'
    inlines = [
            UserEventInline,
            # ChargeBoxActionInline,
            # ChargePointActionInline
        ]
    #readonly_fields = ('students',)
    #form = Event(request.user, request.POST)
    # fieldsets = [
    #     (None,               {'fields': ['name']}),
    #     ('Date information', {'fields': ['students'], 'classes': ['notes']}),
    # ]


    def clean_name(self):
        if True:
            raise ValidationError("Something went wrong")
        return None

    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(EventAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormWithRequest(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['user'] = request.user
                return ModelForm(*args, **kwargs)

        setattr(ModelFormWithRequest, 'user', request.user)
        return ModelFormWithRequest


    def students(self, obj):
        return obj.students()

    def user(self, obj):
        return obj.users()

    def save_model(self, request, obj, form, change):
        try:
            obj.user = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, str(e), level=messages.ERROR)

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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            queryset = queryset.filter()
        else:
            member = MemberGroup.objects.filter(member_user=request.user).first()
            if member:
                queryset = queryset.filter(academic_group=member.member_group)

        return queryset


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