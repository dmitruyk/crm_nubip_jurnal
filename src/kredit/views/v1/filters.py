from django.http import JsonResponse
from ...models import Application
from django.conf.urls import url


def search(request):
    if request.method == 'GET':
        result = []
        filter_status = request.GET.get('status', None)
        query = Application.objects
        empty = Application.objects.none()

        if filter_status:
            filter_status = filter_status.strip()
            applications = Application.objects.filter(status__icontains=filter_status)
            for app in applications:
                empty |= query.filter(id=app.id)
            query = empty

        # TODO add more
        if query.count() > 1:
            for q in query:
                q = q.as_dict
                result.append(q)
        else:
            result.append({'404': 'object or filter not found'})

    return JsonResponse(result, status=200, safe=False)


urlpatterns = [
    url(r'^search$', search),
]
