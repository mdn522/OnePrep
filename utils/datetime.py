from django.utils import timezone


def get_date_range(start_date, end_date):
    res = []
    current_date = start_date.date()
    end_date = end_date.date()
    while current_date <= end_date:
        res.append(current_date)
        current_date += timezone.timedelta(days=1)

    return res


def get_date_format(date):
    return date.strftime('%Y-%m-%d')


def get_md_format(date):
    return date.strftime('%m-%d')


def tz_now_w_ms():
    now = timezone.now()
    return now.replace(microsecond=int(now.microsecond / 1000))


