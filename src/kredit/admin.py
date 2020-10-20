from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import ModelForm, PasswordInput
from django.contrib.auth.hashers import make_password

from .models import *


# class ProductInline(admin.TabularInline):
#     model = Product
#     # extra = 0
#     # ordering = ['-created']


@admin.register(PartnerInfo)
class PartnerInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    pass

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(CreditOrganizationInfo)
class CreditOrganizationInfoAdmin(admin.ModelAdmin):
    pass

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    pass

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass

@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    pass

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    pass

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