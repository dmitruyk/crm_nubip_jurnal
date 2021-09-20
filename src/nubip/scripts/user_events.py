from ..models import Event, UserEvent


def add_user_to_events(user_id, group_id, start_day):
    g_events = Event.objects.filter(academic_group__id=group_id, day__gte=start_day)
    print(g_events.count())
    for e in g_events:
        if not UserEvent.objects.filter(event=e, user__id=user_id).exists():
            try:
                print('creating')
                #_e = UserEvent(event=e, user__id=user_id)
                #_e.save()
            except:
                print('ex')
    print('finish')


def delete_all_user_events(user_id,):
    u_e = UserEvent.objects.filter(user__id=user_id)
    print(u_e.count())
    #u_e.delete()
    print('finish')


