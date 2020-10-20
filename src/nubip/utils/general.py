from django.db import connection
from django.utils import timezone


def get_now():
    return timezone.now()


def get_now_str():
    return get_now().isoformat(timespec='milliseconds')


def get_db_connections_count():
    db_name = connection.settings_dict.get('NAME') \
        if connection.settings_dict else None

    row = None
    if db_name:
        with connection.cursor() as cursor:
            try:
                cursor.execute("select count(*) as count "
                               "from pg_stat_activity "
                               "where datname = %s", [db_name])
                row = cursor.fetchone()
            finally:
                cursor.close()

    return row[0] if row else None


def to_human_readable_consumption(consumed_wh):
    return '{:.3f}'.format(consumed_wh / 1000.0)


def to_human_readable_duration(duration_sec):
    hours = duration_sec / 3600
    minutes = (duration_sec % 3600) / 60
    seconds = duration_sec % 60
    return '%02d:%02d:%02d' % (hours, minutes, seconds)


def to_human_readable_amount(amount):
    return '{:.2f}'.format(amount / 100.0)
