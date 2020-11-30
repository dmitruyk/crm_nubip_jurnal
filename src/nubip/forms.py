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


class MyCustomForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        #print(self.user, '11111111111')
        super(MyCustomForm, self).__init__(*args, **kwargs)

        # # If the user does not belong to a certain group, remove the field
        # if not self.user.groups.filter(name__iexact='mygroup').exists():
        #     del self.fields['confidential']