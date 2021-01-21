import datetime
import calendar
from django.urls import reverse
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from .utils.calendar import EventCalendar

from datetime import date

from django.utils.translation import ugettext_lazy as _
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
    ordering = ['member_user__last_name']

    def get_role(self, obj):
        return None


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportDataEvent)
class ReportDataEventAdmin(admin.ModelAdmin):
    pass


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    pass


# def make_assign_to_user_action(user):
#     def assign_to_user(modeladmin, request, queryset):
#         for order in queryset:
#             order.assign_to(user)  # Method on Order model
#             messages.info(request, "Order {0} assigned to {1}".format(order.id,
#                                                                       user.first_name))
#
#     assign_to_user.short_description = "Assign to {0}".format(user.first_name)
#     # We need a different '__name__' for each action - Django
#     # uses this as a key in the drop-down box.
#     assign_to_user.__name__ = 'assign_to_user_{0}'.format(user.id)
#
#     return assign_to_user

from django.contrib.auth import get_user_model

@admin.register(LectureName)
class LectureNameAdmin(admin.ModelAdmin):
    list_display = ['lecture_name', 'lector']
    search_fields = ('name', 'teacher__first_name')

    def lecture_name(self, obj):
        return obj.name

    def lector(self, obj):
        return obj.teacher

    # def get_actions(self, request):
    #     actions = super(LectureNameAdmin, self).get_actions(request)
    #
    #     for user in get_user_model().objects.filter(is_staff=True).order_by('first_name'):
    #         action = make_assign_to_user_action(user)
    #         actions[action.__name__] = (action,
    #                                     action.__name__,
    #                                     action.short_description)
    #
    #     return actions


# @admin.register(UserEvent)
# class UserEventAdmin(admin.ModelAdmin):
#     pass


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head']


class LectureNameInline(admin.TabularInline):
    model = LectureName
    extra = 0
    ordering = ['-name']


class MemberGroupInline(admin.TabularInline):
    model = MemberGroup
    extra = 0
    ordering = ['member_user__last_name']
    raw_id_fields = ('member_user',)


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    ordering = ['-created']


class UserEventInline(admin.TabularInline):
    model = UserEvent
    extra = 0
    ordering = ['-created']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('user',)
        else:
            return super(UserEventInline, self).get_readonly_fields(request, obj)


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
    list_filter = ('name', 'course')
    raw_id_fields = ('curator',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AcademicGroupAdmin, self).get_search_results(request, queryset, search_term)
       # print(search_term)
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
        if not request.user.is_superuser:
            queryset = queryset.filter(department__head=request.user)
            queryset = queryset.annotate(
                students_count=Count('membergroup'),
            )
            return queryset

        queryset = queryset.annotate(
            students_count=Count('membergroup'),
        )
        return queryset


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_filter = ('role',)
    list_display = ('name', 'is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'password', 'role', 'user_permissions', 'groups')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('name', 'password1', 'password2', 'is_staff', 'is_active', 'role', 'groups')}
    #     ),
    #  )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


# from django.contrib.admin.filters import RelatedFieldListFilter
#
#
# class AcademicGroupFilter(RelatedFieldListFilter):
#     def __init__(self, field, request, *args, **kwargs):
#         """Get the species you want to limit it to.
#         This could be determined by the request,
#         But in this example we'll just specify an
#         arbitrary species"""
#         species = AcademicGroup.objects.all()
#
#         #Limit the choices on the field
#         field.remote_field.limit_choices_to = {'department__academic_group': species}
#
#         #Let the RelatedFieldListFilter do its magic
#         super(AcademicGroupFilter, self).__init__(field, request, *args, **kwargs)
class EventListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Академічна група')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'academic_group'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if request.user.is_superuser:
            academic_groups = AcademicGroup.objects.all()
        else:
            department = Department.objects.filter(head=request.user).first()
            academic_groups = AcademicGroup.objects.filter(department=department)
        return ((academic_group.id, academic_group.name) for academic_group in academic_groups)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        if self.value():
            return queryset.filter(report_event__academic_group=self.value())
        else:
            return queryset


@admin.register(ReportUserEvent)
class ReportUserEventAdmin(admin.ModelAdmin):
    #search_fields = ('member__name', 'group')
    list_filter = ('report_event__lecture', EventListFilter,)
    inlines = [
            ReportDataEventInline,
        ]
    list_display = ['report_creator', 'role', '_day', 'report_event', 'group', 'count']
    date_hierarchy = 'report_event__day'

    def _day(self, obj):
        return obj.report_event.day.__str__()
    _day.short_description = 'Дата'

    def count(self, obj):
        all_users = ReportDataEvent.objects.filter(report_data_user_data=obj).count()
        present_users = ReportDataEvent.objects.filter(report_data_user_data=obj, report_presence=True).count()

        return f'{present_users}/{all_users}'
    count.short_description = 'НБ/ПР'

    def group(self, obj):
        group = None
        return obj.report_event.academic_group.name
        # if obj.report_creator.role == 'student':
        #     m_g = MemberGroup.objects.filter(member_user=obj.report_creator).first()
        #     if m_g:
        #         group = m_g.member_group.name
        # if obj.report_creator.role == 'curator':
        #     a_g = AcademicGroup.objects.filter(curator=obj.report_creator).first()
        #     group = a_g.name
        # return group
    group.short_description = 'Група'

    def role(self, obj):
        return obj.report_creator.role
    role.short_description = 'Роль'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            queryset = queryset.filter()
        else:
            queryset = queryset.filter(report_event__academic_group__department__head=request.user)

        return queryset


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = MyCustomForm
    list_display = ['lecture', 'academic_group', 'index_number', 'day', 'custom_column']
    list_filter = ('academic_group', )
    #readonly_fields = ('lecture', 'academic_group', 'index_number', 'day', 'notes')
    date_hierarchy = 'day'
    ordering = ('day',)
    inlines = [
            UserEventInline,
            # ChargeBoxActionInline,
            # ChargePointActionInline
        ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('lecture', 'academic_group', 'index_number', 'day', 'custom_column', 'notes')
        else:
            return super(EventAdmin, self).get_readonly_fields(request, obj)
    #readonly_fields = ('students',)
    #form = Event(request.user, request.POST)
    # fieldsets = [
    #     (None,               {'fields': ['name']}),
    #     ('Date information', {'fields': ['students'], 'classes': ['notes']}),
    # ]

    # define the row x column value here
    def custom_column(self, obj):
        from django.utils.html import format_html
        request = getattr(self, 'request', None)
        if request:
            if ReportUserEvent.objects.filter(report_event=obj, report_creator=request.user).exists():
                return format_html(
                    '<span style="color: #{};">{}</span>',
                    '6be073',
                    'Подано',
                )
            else:
                return format_html(
                    '<span style="color: #{};">{}</span>',
                    'ff5733',
                    'НЕ Подано',
                )

        #00ff13
        # retval = ('green.jpg', 'This location checked in less than 5 minutes ago')
        # return format_html('<img src={} alt={} />', 'img/large-green-square-4336.png',
        #                    'This location checked in less than 5 minutes ago')

    # set the column heading here
    custom_column.short_description = 'Status'

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
        self.request = request
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
        elif request.user.role == 'headman':
            member = MemberGroup.objects.filter(member_user=request.user).first()
            if member:
                queryset = queryset.filter(academic_group=member.member_group)
        elif request.user.role in ['teacher', 'curator']:
            queryset = queryset.filter(Q(lecture__teacher=request.user) | Q(academic_group__curator=request.user))
        else:
            return queryset.none()
        #     queryset = []
        # elif request.user.role == 'head_department':
        #     queryset = queryset.filter(lecture__teacher=request.user)
        #
        #     head_department
        #     lecture

        return queryset


class FGEVInline(admin.TabularInline):
    model = FGEV
    extra = 0
    #ordering = ['-gev_event__gev_event__lecture__name']


# @admin.register(GEV)
# class GEVAdmin(admin.ModelAdmin):
#     inlines = [
#             FGEVInline,
#             # ChargeBoxActionInline,
#             # ChargePointActionInline
#         ]
#
#     def get_inline_instances(self, request, obj=None):
#         print(self.inlines, obj)
#         print([inline(self.model, self.admin_site) for inline in self.inlines])
#         return [inline(self.model, self.admin_site) for inline in self.inlines]
#     # list_display = ('Answer.question.question_text', 'Answer.User.user_id', 'Choice.choice_text')
#     readony_fields = ('lecture', 'day')
#     inlines = [
#         LectureNameInline,
#     ]
#     list_display = ('lecture', 'day', 'academic_group')
#     fieldsets = [
#         ('Question', {'fields': ['lecture']}),
#         ('User', {'fields': ['day']}),
#         ('Vote', {'fields': ['academic_group']}),
#     ]
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

# from django.http import HttpResponse
# from django.urls import path
#
# # my dummy model
# class DummyModel(models.Model):
#
#     class Meta:
#         verbose_name_plural = 'Dummy Model'
#         app_label = 'nubip'
#
# def my_custom_view(request):
#     return HttpResponse('Admin Custom View')
#
# class DummyModelAdmin(admin.ModelAdmin):
#     model = DummyModel
#
#     def get_urls(self):
#         view_name = '{}_{}_changelist'.format(
#             self.model._meta.app_label, self.model._meta.model_name)
#         return [
#             path('my_admin_path/', my_custom_view, name=view_name),
#         ]
# admin.site.register(DummyModel, DummyModelAdmin)