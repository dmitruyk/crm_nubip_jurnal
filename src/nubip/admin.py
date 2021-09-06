
import calendar
from django.urls import reverse
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from .utils.calendar import EventCalendar
from datetime import datetime, date
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import DateFieldListFilter
from .forms import CustomUserCreationForm, CustomUserChangeForm, MyCustomForm
from django.db.models import Count
from django.db.models.query import Q

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from import_export.admin import ExportActionMixin

from tabular_export.admin import export_to_csv_action, export_to_excel_action, export_to_excel_response

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
    list_display = ['report_user', 'report_presence', 'user_event_creator']
    list_filter = ('report_data_user_data__report_event',)
    date_hierarchy = 'report_data_user_data__report_event__day'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            queryset = queryset.filter()
        else:
            queryset = queryset.none()
        return queryset


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    ordering = ['name']


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
#     def save_model(self, request, obj, form, change):
#         try:
#             obj.user = request.user
#             super().save_model(request, obj, form, change)
#         except Exception as e:
#             self.message_user(request, str(e), level=messages.ERROR)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head']


class LectureNameInline(admin.TabularInline):
    model = LectureName
    extra = 0
    ordering = ['-name']


class TutorNameInline(admin.TabularInline):
    model = TutorName
    raw_id_fields = ('teacher',)
    extra = 0
    ordering = ['-teacher']


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
    ordering = ['user__user__last_name']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('user', )
        else:
            return super(UserEventInline, self).get_readonly_fields(request, obj)

    fieldsets = (
        (None, {'fields': ('user', 'presence', 'reason', 'additional_info',)}),
    )
    list_display = ['user', 'presence', 'reason', 'additional_info']

@admin.register(LectureName)
class LectureNameAdmin(admin.ModelAdmin):
    list_display = ['lecture_name']
    search_fields = ('name',)
    inlines = [
            TutorNameInline,
        ]

    def lecture_name(self, obj):
        return obj.name

    def lector(self, obj):
        return obj.teacher


class ReportDataEventInline(admin.TabularInline):
    model = ReportDataEvent
    extra = 0
    ordering = ['report_user__last_name']

    fieldsets = (
        (None, {'fields': ('report_user', 'report_presence', 'report_reason', 'report_additional_info',)}),
    )
    list_display = ['report_user', 'report_presence', 'report_reason', 'report_additional_info']


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [
            MemberGroupInline,
        ]
    list_display = ['name', 'students_count', 'curator', 'department', 'graduation', 'graduation_date']
    list_filter = ('name', 'course')
    raw_id_fields = ('curator',)
    ordering = ['name']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AcademicGroupAdmin, self).get_search_results(request, queryset, search_term)
       # print(search_term)
        try:
            # search_term_as_int = int(search_term)
            # queryset |= self.model.objects.filter(age=search_term_as_int)
            m_g = MemberGroup.objects.filter(member_user__last_name__icontains=search_term)
            if m_g:
                queryset |= self.model.objects.filter(pk__in=[m.member_group.id for m in m_g])
        except Exception as e:
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

    # def queryset(self, request, queryset):
    #     """
    #     Returns the filtered queryset based on the value
    #     provided in the query string and retrievable via
    #     `self.value()`.
    #     """
    #     # Compare the requested value
    #     if not request.user.is_superuser:
    #         department = Department.objects.filter(head=request.user).first()
    #         return queryset.filter(department=department)
    #     else:
    #         return queryset


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_filter = ('role',)
    list_display = ('name', 'username', 'is_staff', 'is_active', 'role', 'deducted')
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'password', 'role', 'user_permissions', 'groups')}),
        ('Permissions', {'fields': ('is_staff', 'deducted', 'deducted_date', 'is_active', 'is_superuser')}),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('name', 'password1', 'password2', 'is_staff', 'is_active', 'role', 'groups')}
    #     ),
    #  )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_name',)


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
class ReportUserEventAdmin(ExportActionMixin, admin.ModelAdmin):
    #search_fields = ('member__name', 'group')
    actions = (export_to_excel_action, export_to_csv_action, 'export_batch_summary_action')
    list_filter = (('report_event__day', DateRangeFilter), EventListFilter, ('report_event__day', DateFieldListFilter),'report_event__lecture',)
    inlines = [
            ReportDataEventInline,
        ]
    list_display = ['report_creator', 'role', '_day', 'index_number', 'report_event', 'group', 'count', 'submitted']
    date_hierarchy = 'report_event__day'
    ordering = ['report_event__day', 'report_event__academic_group__name', 'report_event__index_number__name']

    def index_number(self, obj):
        return obj.report_event.index_number
    index_number.admin_order_field = 'report_event__index_number__name'
    index_number.short_description = 'Пара'

    #import_id_fields = ('report_event__lecture',)
    #fields = ('report_event__lecture', 'role', 'report_event', 'count',)

    #actions = ('export_batch_summary_action', )
    #'export_batch_summary_action',
    def export_batch_summary_action(self, request, queryset):
        headers = ['Batch Name', 'My Computed Field']
        rows = queryset.annotate("…").values_list('title', 'computed_field_name')
        return export_to_excel_response('batch-summary.xlsx', headers, rows)
    export_batch_summary_action.short_description = 'Export Batch Summary'

    def _day(self, obj):
        return obj.report_event.day.__str__()
    _day.short_description = 'Дата'
    _day.admin_order_field = 'report_event__day'

    def count(self, obj):
        all_users = ReportDataEvent.objects.filter(report_data_user_data=obj,
                                                   user_event_creator=obj.report_creator).count()
            #filter(Q(user_event_creator=obj.report_creator) | Q(user_event_creator__isnull=True)).count()

        present_users = ReportDataEvent.objects.filter(report_data_user_data=obj,
                                                       report_presence=True,
                                                       user_event_creator=obj.report_creator).count()
           # .filter(Q(user_event_creator=obj.report_creator) | Q(user_event_creator__isnull=True)).count()

        return f'{all_users-present_users}/{present_users}/{all_users}'
    count.short_description = 'НБ/ПР/ВСЬОГО'

    def submitted(self, obj):
        tutors = TutorName.objects.filter(lecture=obj.report_event.lecture)
        try:
            if obj.report_event.academic_group.curator in [tutor.teacher for tutor in tutors]:
                teacher = 'K/B' if ReportUserEvent.objects.filter(report_event=obj.report_event,
                                                                  report_creator__role='curator').exists() else 'B'
            else:
                teacher = '' if ReportUserEvent.objects.filter(report_event=obj.report_event,
                                                               report_creator__role='teacher').exists() else 'B'

            curator = '' if ReportUserEvent.objects.filter(report_event=obj.report_event,
                                                           report_creator__role='curator').exists() else 'K'
            headman = '' if ReportUserEvent.objects.filter(report_event=obj.report_event,
                                                           report_creator__role='headman').exists() else 'C'

            if curator == '' and headman == '' and teacher == '':
                return '+'

            return f'{curator} {headman} {teacher}'
        except:
            return f'X X X'
    submitted.short_description = 'Не Подано'


    def group(self, obj):
        try:
            return obj.report_event.academic_group.name
        except:
            return None

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
            role = request.user.role
            if role == 'head_department':
                queryset = queryset.filter(report_event__academic_group__department__head=request.user)
            if role == 'curator':
                queryset = queryset.filter(report_event__academic_group__curator=request.user)
                    #exclude(report_creator=request.user)

        return queryset


from .models import Event
from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from django.http import HttpResponseRedirect

class CreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields =[
            "day",
        ]

    widgets = {
        'Date': DatePickerInput(),
    }



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = MyCustomForm
    list_display = ['lecture', 'academic_group', 'index_number', 'day', 'custom_column']
    list_filter = ('academic_group', )
    date_hierarchy = 'day'
    ordering = ('day', 'index_number__name')
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
        request = getattr(self, 'request', None)
        if request:
            if request.user.is_superuser:
                if ReportUserEvent.objects.filter(report_event=obj).exists():
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
        else:
            return format_html(
                '<span style="color: #{};">{}</span>',
                'ff5733',
                'Невідомо',
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

        if obj and request.user.is_superuser is False:
            ModelForm.base_fields['frequency_parameter'].disabled = True
            ModelForm.base_fields['end_date'].disabled = True
        return ModelFormWithRequest

    def students(self, obj):
        return obj.students()

    def user(self, obj):
        return obj.users()

    def save_model(self, request, obj, form, change):
        try:
            obj.user = request.user
            print(obj.user, request.user)
            obj.frequency_parameter = request.POST.get('frequency_parameter')
            obj.end_date = request.POST.get('end_date')
            super().save_model(request, obj, form, change)
        except Exception as e:
            #raise Exception(e)
            self.message_user(request, str(e), level=messages.ERROR)

    def save_formset(self, request, form, formset, change):
        if formset.model != UserEvent:
            print('save')
            return super(EventAdmin, self).save_formset(request, form, formset, change)
        print(request.POST.get('frequency_parameter'))
        instances = formset.save(commit=False)
        frequency_parameter = request.POST.get('frequency_parameter')
        for instance in instances:
            if not instance.pk:
                instance.request_user = request.user
            instance.request_user = request.user
            instance.frequency_parameter = frequency_parameter
            instance.save()
        formset.save_m2m()

    # def save_formset(self, request, form, formset, change):
    #     if formset.model != UserEventInline:
    #         return super(EventAdmin, self).save_formset(request, form, formset, change)
    #     instances = formset.save(commit=False)
    #     for instance in instances:
    #         print('22222222')
    #         if not instance.pk:
    #             print('fweweqwe')
    #             instance.user_request = request.user
    #         instance.save()
    #     formset.save_m2m()

    # fieldsets = [
    #     (None,               {'fields': ['name']}),
    #     ('Date information', {'fields': ['academic_group'], 'classes': ['notes']}),
    # ]


    def changelist_view(self, request, extra_context=None):
        self.request = request
        if request.GET:
            return super().changelist_view(request, extra_context=extra_context)

        __date = date.today()
        params = ['day', 'month', 'year']
        field_keys = ['{}__{}'.format(self.date_hierarchy, i) for i in params]
        field_values = [getattr(__date, i) for i in params]
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
        elif request.user.role in ['teacher', 'curator', 'head_department']:
            tutor_lectures = TutorName.objects.filter(teacher=request.user).all()
            lectures = [lec.lecture for lec in tutor_lectures]
            queryset = queryset.filter(Q(lecture__in=lectures) | Q(academic_group__curator=request.user))
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


from django.contrib.admin import SimpleListFilter


class CountryFilter(SimpleListFilter):
    title = 'Академічна група' # or use _('country') for translated title
    parameter_name = 'academic_group'

    def lookups(self, request, model_admin):
        academic_groups = set([report_data for report_data in AcademicGroup.objects.all()])
        return [(g.id, g.name) for g in academic_groups]

    def queryset(self, request, queryset):
        if self.value():
            academic_group = AcademicGroup.objects.filter(pk=self.value()).first()
            # member_users = MemberGroup.objects.filter(member_group=academic_group)
            # users = [member.member_user for member in member_users]
            q = queryset.filter(academic_group=academic_group)
            print(len(q))
            return q
        # if self.value():
        #     return queryset.filter(country__id__exact=self.value())

from django.db.models import Value, CharField
@admin.register(ReportModel)
class ReportModelModelAdmin(admin.ModelAdmin):
    list_display = ['custom_column']
    list_filter = (('day', DateRangeFilter), CountryFilter)
    change_list_template = 'admin/sale_summary_change_list.html'
    date_hierarchy = 'day'

    def get_rangefilter_timestamp_default(self, request):
        return ('2021-08-01', '2021-08-30')

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        teacher_filters = Q(userevent__presence=True,
                            userevent__user__user__role='teacher')

        headman_filters = Q(
                            )

        metrics = {
            'teacher_presence': Count('userevent', teacher_filters),
            'headman_presence': Count('userevent', headman_filters),
        }

        report_data = []

        groups = set(q.academic_group for q in qs)

        for g in groups:
            if g is not None:
                #ev = Event.objects.filter(academic_group=g)

                event_counter = qs.filter(academic_group=g).count()

                teacher_report_counter = ReportUserEvent.objects.filter(report_event__in=qs,
                                                                        report_event__academic_group=g,
                                                                        report_creator__role='teacher').count()

                headman_report_counter = ReportUserEvent.objects.filter(report_event__in=qs,
                                                                        report_event__academic_group=g,
                                                                        report_creator__role='headman').count()

                report_event = ReportUserEvent.objects.filter(report_event__in=qs, report_event__academic_group=g)

                rde_teacher = ReportDataEvent.objects.filter(report_data_user_data__in=report_event,
                                                             user_event_creator__role='teacher',
                                                             report_presence=True)

                rde_headman = ReportDataEvent.objects.filter(report_data_user_data__in=report_event,
                                                             user_event_creator__role='headman',
                                                             report_presence=True)

                member_academic_group = MemberGroup.objects.filter(member_group=g).select_related('member_user')

                member_academic_group_counter = User.objects.filter(pk__in=[m.member_user.id for m in member_academic_group],
                                                                    deducted=False,
                                                                    deducted_date__isnull=True).count()

                total_teacher_report_member_counter = member_academic_group_counter * teacher_report_counter

                total_headman_report_member_counter = member_academic_group_counter * headman_report_counter

                rde_teacher_counter = 0  if total_teacher_report_member_counter == 0 else \
                    round((rde_teacher.count() * 100) / total_teacher_report_member_counter, 2)

                rde_headman_counter = 0 if total_headman_report_member_counter == 0 else \
                    round((rde_headman.count() * 100) / total_headman_report_member_counter, 2)

                present_teacher_report = round(((teacher_report_counter * 100) / event_counter), 1)
                present_headman_report = round(((headman_report_counter * 100) / event_counter), 1)

                total_coefficient = (((rde_teacher_counter + rde_headman_counter) / 2) / 10)

                total_count = 0 if total_coefficient == 0 else round(total_coefficient, 1)

                report_data.append({'academic_group__name': g.name,
                                    'apply_teacher_reports': teacher_report_counter,
                                    'apply_headman_reports': headman_report_counter,
                                    'total_events': event_counter,
                                    'present_teacher_report': present_teacher_report,
                                    'present_headman_report': present_headman_report,

                                    'teacher_presence': rde_teacher_counter,
                                    'headman_presence': rde_headman_counter,
                                    'total': total_count
                                    }
                )


        #print(report_data)


        ls = list(
            qs.values('academic_group__name')
            .annotate(**metrics)
            .order_by('-day')
        )
        #print(ls)
        response.context_data['summary'] = report_data
        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )
        #print(qs.aggregate(**metrics))
        return response

    def custom_column(self, obj):
        return obj
        request = getattr(self, 'request', None)
        if request:
            if request.user.is_superuser:
                if ReportUserEvent.objects.filter(report_event=obj).exists():
                    return format_html(
                        '<span style="color: #{};">{}</span>',
                        '6be073',
                        'Подано',
                    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            queryset = Event.objects.all()
        return queryset


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