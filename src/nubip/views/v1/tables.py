from django.http import HttpResponse
from django.shortcuts import render


def detail_view(request):

    print(request.GET.get('group_id', None))
    return render(request, 'exmple.html')
# <td> <a href="{% url 'nubip:details' group_id='3' %}">{{ row.academic_group__name }}</a> </td>