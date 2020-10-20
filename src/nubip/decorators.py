import base64
from .models import APIClient as Client
from django.http import HttpResponseForbidden
from django.http import HttpRequest
from functools import wraps
from . import exceptions as ex
from django.contrib.auth import get_user_model


from django.http import HttpResponseForbidden, HttpResponseServerError

User = get_user_model()


def basic_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = next(a for a in args if isinstance(a, HttpRequest))
        login, password = None, None
        print(str(request))
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == 'basic':
                login, password = base64.b64decode(auth[1]).split(b':')
        if login and password:
            print(login, password)
            try:
                user = User.objects.get(username=login.decode('ascii'), is_active=True)
                print(user)
                if not password.decode('ascii') == user.password:
                    return HttpResponseForbidden()
                request.user = user
            except Exception as e:
                return HttpResponseForbidden(e)
            else:
                return func(*args, **kwargs)

    return wrapper


def login_required(r=None):
    """"""
    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.user.is_authenticated:
                if (
                        r and
                        (
                            (
                                r == 'abs_client'
                                and request.user.is_client())
                            or
                            (
                                r == 'abs_admin'
                                and request.user.is_admin())
                            or
                            (
                                isinstance(r, (list, tuple, set))
                                and request.user.role in r)
                            or
                            (
                                isinstance(r, str) and request.user.role == r)
                        )
                ) or not r:
                    return f(*args, **kwargs)
            return HttpResponseForbidden()
        return wrapper
    return actual_decorator

# def chk_user_role(func):
#     @wraps(func)
#     ACTION = {'company':['r', 'w', 'e', 's'],
#               'partner':[],
#               'super':[]}
#     ('company', 'Company'),
#     ('partner', 'Partner'),
#     ('super', 'Super')
#
#     def wrapper(user, action):
#         try:
#             client = Client.objects.get(login=user, is_active=True)
#             if not client:
#                 return HttpResponseForbidden()
#             else:
#
#                 if request.method == 'POST':
#                     api_key = request.headers.get('api-key')
#                     if not api_key == str(client.api_key.uuid):
#                         return HttpResponseForbidden()
#                 request.user = client
#             except Exception as e:
#                 raise ex.UnauthorizedException
#
#             else:
#                 return func(*args, **kwargs)
#
#         return wrapper