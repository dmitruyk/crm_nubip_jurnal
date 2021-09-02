from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.forms import ModelForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)
from django.contrib.admin.widgets import AdminDateWidget
from bootstrap_datepicker_plus import DatePickerInput
from .models import Event
from django import forms
from django.utils.translation import ugettext_lazy as _

STATUS_CHOICES = (
    (1, _("Один раз")),
    (2, _("Кожен день тижня")),
    (3, _("Через один тиждень")),
    # (4, _("Relevant")),
    # (5, _("Leading candidate"))
)

class MyCustomForm(ModelForm):

    #extra_field = forms.CharField()
    end_date = forms.DateInput()
    frequency_parameter = forms.ChoiceField(choices = STATUS_CHOICES,
                                            label="Повторюваність",
                                            initial="",
                                            widget=forms.Select(),
                                            required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        #print(self.user, '11111111111')
        self.rr = False
        super(MyCustomForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Event
        fields =[
            "day",
            "lecture",
            "academic_group",
            "index_number",
            "frequency_parameter",
            "end_date",
        ]

    day = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    # widgets = {
    #     'day': DatePickerInput(),
    #     #'end_date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
    # }

        # # If the user does not belong to a certain group, remove the field
        # if not self.user.groups.filter(name__iexact='mygroup').exists():
        #     del self.fields['confidential']


