import logging
from ...models import CustomerProfile, Passport, PhoneNumber, PartnerInfo
from ...decorators import basic_auth, login_required
from ... import exceptions as ex
from django.http import JsonResponse
from django.conf.urls import url
from django.views.generic import View
import json

logger = logging.getLogger(__name__)


class ApplicationView(View):
    pass


class FormView(View):
    pass


@basic_auth
@login_required('partner')
def create_application(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            customer = data.get('customer')
            passport_data = customer.get('passport')
            passport_number = passport_data.get('passport_data')
            passport_issue_date = passport_data.get('issue_date')

            customer_passport, _ = Passport.objects.get_or_create(number=passport_number,
                                                                  issue_date=passport_issue_date
                                                                  )
            phone_number = customer.get('phone_number')
            country_code = phone_number.get('country_code')
            area_code = phone_number.get('area_code')
            number = phone_number.get('number')
            type = phone_number.get('type')

            customer_phone_number, _ = PhoneNumber.objects.get_or_create(country_code=country_code,
                                                                         area_code=area_code,
                                                                         number=number,
                                                                         type=type)

            first_name = customer.get('first_name')
            last_name = customer.get('last_name')
            add_name = customer.get('add_name')
            date_of_birth = customer.get('date_of_birth')
            scoring_score = data.get('scoring_score')
            partner = PartnerInfo.objects.filter(user=request.user).first()
            customer, _ = CustomerProfile.objects.get_or_create(first_name=first_name,
                                                                last_name=last_name,
                                                                add_name=add_name,
                                                                date_of_birth=date_of_birth,
                                                                passport=customer_passport,
                                                                phone_number=customer_phone_number,
                                                                scoring_score=scoring_score,
                                                                partner=partner
                                                                )
            return JsonResponse({'status': 'accepted'}, status=200)
        except Exception as e:
            return JsonResponse({'Bad request!': str(e)}, status=400)

class SingleView(View):

    def get(self, request, customer_profile, *args, **kwargs):
        customer = CustomerProfile.objects.filter(pk=customer_profile).first()
        if customer is not None:
            result = customer.as_dict()
            return JsonResponse(result, status=200)

        raise ex.NotFoundException('charging_reservation__not_found')


urlpatterns = [
    url(r'^active$', ApplicationView.as_view()),
    url(r'^create$', create_application),
    url(r'^(?P<session_id>.+)$', SingleView.as_view()),
]
